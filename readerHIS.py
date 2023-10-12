import numpy as np
import glob, os
import re
import sys

####################################
######## HIS to ROOT ###############
####################################
"""
mockNDarray makes a lists of ndarrays (or lists)
            immitate an ndarray (without data copy)
"""
# from __future__ import absolute_import
# __author__  = "Sebastian Haase <seb.haase@gmail.com>"
# __license__ = "BSD license - see LICENSE file"

import numpy as np

mmap_shape = None # default: map entire file; change this to handle BIG files


class mockNDarray(object):
    def __init__(self, *arrs):
        def conv(a):
            if hasattr(a,'view'):
                return a.view()   # we use view(), so that we can fix it up
            if hasattr(a,'__len__'):
                return mockNDarray(*a) # recursively mockify lists
            if a is None:
                return mockNDarray()   # None makes an empty mockNDarray
            return np.array(a) # use standard conversion to ndarray (copy!) 
            # raise ValueError, "don't know how to mockify %s" %(a,)
        self._arrs = [conv(a) for a in arrs]
        self._mockAxisSet(0)

    def _mockAxisSet(self, i):
        """
        this is the workhorse function, that makes the internal state consistent
        sets:
            self._mockAxis
            self._ndim
            self._shape
        """
        self._mockAxis = i
        if len(self._arrs)==0:
            self._ndim     = 0
            self._shape    = ()
            return
        self._ndim     = 1+max((a.ndim for a in self._arrs))
        self._shape    = [1]*self._ndim

        #fix up shape of sub array so that they all have ndim=self._ndim-1
        #  fill shape by prepending 1s
        #  unless ndim was 0, then set shape to tuple of 0s
        nd1 = self._ndim-1
        for a in self._arrs:
            if a.ndim == nd1:
                continue
            if isinstance(a, mockNDarray):
                if a._ndim ==0:
                    a._ndim= nd1
                    a._shape = (0,)*nd1
            else:
                if a.ndim == 0:
                    a.shape = (0,)*nd1
                else:
                    a.shape = (1,)*(nd1-a.ndim)+a.shape

        # fixup the shape to reflext the "biggest" shape possible, like a "convex hull"
        iSub=0 # equal to i, except for i>_mockAxis: its one less
        for i in range(self._ndim):
            if i == self._mockAxis:
                self._shape[i] = len(self._arrs)
                continue
            for a in self._arrs:
                # OLD: the a.ndim>iSub check here means, that sub arrays may be "less dimensional" then `self` would imply if it was not "mock"
                # OLD:   if a.ndim <= self._ndim and a.ndim>iSub:
                if self._shape[i] < a.shape[iSub]:
                    self._shape[i] = a.shape[iSub]
            iSub+=1
        self._shape = tuple( self._shape )

    def _getshape(self):
        return self._shape
    def _setshape(self, s):
        # minimal "dummy" implementation
        #  useful for functions like U.mean2d, which want to set shape to -1,s[-2],s[-1]
        __setShapeErrMsg = "mockNDarray supports only trivial set_shape functionality"
        foundMinus=False
        if len(self._shape) != len(s):
            raise ValueError(__setShapeErrMsg)
        for i in range(len(self._shape)):
            if s[i] == -1:
                if foundMinus:
                    raise ValueError( __setShapeErrMsg)
                else:
                    foundMinus = True
            elif s[i] != self._shape[i]:
                    raise ValueError (__setShapeErrMsg)

    shape = property( _getshape,_setshape )


    def _getndim(self):
        return self._ndim
    ndim = property( _getndim )

    def _getdtype(self):
        return min((a.dtype for a in self._arrs)) if self._ndim else None
    dtype = property( _getdtype )

    def __len__(self):
        return self._shape[0]

    def __getitem__(self, idx):
        import copy
        if isinstance(idx, int):
            if self._mockAxis == 0:
                return self._arrs[idx]
            else:
                s = copy.copy(self)
                s._arrs = [a[idx] for a in self._arrs]
                s._mockAxisSet( self._mockAxis-1 )
                return s
        elif isinstance(idx, tuple):
            if idx == ():
                return self
            if Ellipsis in idx:
                # expand Ellipsis [...] to make slice-handling easier ....
                dimsGiven = len(idx)-1
                for EllipsisIdx in range(len(idx)):
                    if idx[EllipsisIdx] is Ellipsis:
                        break
                idx = idx[:EllipsisIdx ] + (slice(None),)*(self._ndim-dimsGiven) + idx[EllipsisIdx+1:]

            if len(idx) <= self._mockAxis:
                mockIdx = slice(None)
                idxSkipMock = idx
            else:
                mockIdx = idx[self._mockAxis]
                idxSkipMock = idx[:self._mockAxis] + idx[self._mockAxis+1:]


            if isinstance(mockIdx, slice):
                s = copy.copy(self)

                s._arrs = [a[idxSkipMock] for a in self._arrs[mockIdx]]
                shiftMockAxisBecauseOfInt = sum((1 for i in idx[:self._mockAxis] if not isinstance(i, slice)))
                s._mockAxisSet( self._mockAxis-shiftMockAxisBecauseOfInt )
                return s
            elif mockIdx is None:
                s = copy.copy(self)
                s._arrs = [a[None][idxSkipMock] for a in self._arrs]
                s._mockAxisSet( self._mockAxis+1 )
                idxSkipMock = (slice(None),)+idxSkipMock  # adjust idxSkipMock to keep new axis
                return s[idxSkipMock]

            else: # mockIdx is "normal" int - CHECK
                # return non-mock ndarray, (or mockNDarray, if there are nested ones)
                return self._arrs[mockIdx][idxSkipMock]

        elif idx is Ellipsis:
            return self
        elif isinstance(idx, slice):
            #raise RuntimeError, "mockarray: slice indices not implemented yet"
            s = copy.copy(self)

            if self._mockAxis ==0:
                s._arrs = self._arrs[idx]
                #s._shape[0] = len(self._arrs)
            else:
                s._arrs = [a[idx] for a in self._arrs[mockIdx]]
                #s._shape[0] = len(self._arrs[0])
            #shiftMockAxisBecauseOfInt = sum((1 for i in idx[:self._mockAxis] if not isinstance(i, slice)))
            s._mockAxisSet( self._mockAxis )
            return s
        elif idx is None: # np.newaxis:
            s = copy.copy(self)
            s._arrs = [a[None] for a in self._arrs]
            s._mockAxisSet( self._mockAxis+1 )
            return s


        raise IndexError ("should not get here .... " )

    def transpose(self, *axes):
        if len(axes) == 1:
            axes = axes[0] # convert  transpose(self, axes) to  transpose(self, *axes)

        if len(axes) != self._ndim:
            raise ValueError ("axes don't match mockarray")

        for newMockAxis in range(self._ndim):
            if axes[newMockAxis] == self._mockAxis:
                break
        else:
            raise ValueError ("axes don't contain mockAxis")

        othersAxes = (ax if ax<newMockAxis else ax-1 for ax in axes[:newMockAxis] + axes[newMockAxis+1:])

        othersAxes = tuple(othersAxes)
        import copy
        s = copy.copy(self)
        s._mockAxisSet(newMockAxis)
        #s._shape = tuple(np.array(s._shape)[list(axes)])

        for i,a in enumerate(s._arrs):
            s._arrs[i] = a.transpose( *othersAxes )

        return s

    def view(self):
        from copy import copy
        return copy(self)

# 64 bytes
dtypeHIS = np.dtype([
    ('magic', 'a2'),
    ('ComLen', np.uint16),
    ('iDX', np.uint16),
    ('iDY', np.uint16),
    ('iX', np.uint16),
    ('iY', np.uint16),
    ('pixType', np.uint16),
    ('numImgs', np.uint32),
    ('numChan', np.uint16),
    ('chan', np.uint16),
    ('timeStamp', np.float64),
    ('marker', np.uint32),
    ('miscinfo', '30i1'),
    ])

hisType2numpyDtype = {
    1: np.uint8,
    2: np.uint16,
    3: np.uint32,
    11: ('RGB', (np.uint8,np.uint8,np.uint8)),
    12: ('RGB', (np.uint16,np.uint16,np.uint16)),
}


class ndarray_inHisFile(np.ndarray):
    def __new__(cls, input_array, hisInfo=None):
        obj = np.asarray(input_array).view(cls)
        obj.HIS = hisInfo
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.HIS = getattr(obj, 'HIS', None)

def _try_openHIS_fastMap(m):
    hisHdr0 = m[:64]
    hisHdr0.dtype = dtypeHIS
    try:
        hisHdr0 = hisHdr0[0]
    except IndexError:
        raise EOFError("zero Bytes HIS file")

    imgPixDType = hisType2numpyDtype[ hisHdr0['pixType'] ]
    pixBytes = imgPixDType().itemsize
    nx,ny,nz = hisHdr0['iDX'],  hisHdr0['iDY'],  hisHdr0['numImgs']
    comLen=hisHdr0['ComLen']

    expectedBytes = (64 + pixBytes*nx*ny) * nz + comLen

    if expectedBytes != len(m):
        return None # there are probably comments in other sections, fastMap cannot be used

    mm = m[comLen:] # first hdr will be "corrupt", since comment is just before first imgData
    a = np.recarray(nz, dtype=[( 'hdr',     dtypeHIS ),
                                ( 'imgData', (imgPixDType, (ny,nx)) ),
                                ],
                    buf=mm)

    if comLen:
        hisComment = m[64:64+comLen]
        hisComment.dtype = '|S%d'%(comLen,)
    else:
        hisComment = ('',)
    comment = hisComment[0]  # there is "one" comment per sect

    class hisInfo:
        hdr0 = hisHdr0
        comment0 = comment
        hdr = a['hdr']

    fastHisArr = ndarray_inHisFile(a['imgData'], hisInfo=hisInfo)
    return fastHisArr

def readSection(m, offsetSect = 0):
    """
    m:          numpy memmap of a file
    offsetSect: offset of first byte of section to be read
    """

    offsetComment = offsetSect + 64

    hisHdr = m[offsetSect:offsetComment]
    hisHdr.dtype = dtypeHIS

    # try:
    #     hisHdr = hisHdr[0]
    # except IndexError:
    #     raise EOFError, "End of HIS file reached"

    #assert hisHdr['magic'] == 'IM'

    commentLength = hisHdr['ComLen']
    offsetImg     = offsetComment + commentLength[0]

    if commentLength:
        hisComment = m[offsetComment:offsetImg]
        hisComment.dtype = '|S%d'%(hisHdr['ComLen'],)
    else:
        hisComment = ('',)
    imgPixDType = hisType2numpyDtype[ hisHdr['pixType'][0] ]
    imgBytes = int(hisHdr['iDX'][0]) * int(hisHdr['iDY'][0]) * imgPixDType().itemsize

    sectEnd = offsetImg + imgBytes

    img = m[offsetImg:sectEnd]
    img.dtype = imgPixDType
    img.shape = hisHdr['iDY'][0], hisHdr['iDX'][0]


    #import weakref
    #hisHdr     = weakref.proxy( hisHdr )
    #hisComment = weakref.proxy( hishisComment )

#20100224     img.__class__ = ndarray_inHisFile
    class hisHeaderInfo:
        hdr = hisHdr
        comment = hisComment[0]  # there is "one" comment per sect
        offsetNext = sectEnd

#20100224     img.HIS = hisHeaderInfo
    img = ndarray_inHisFile(img, hisInfo=hisHeaderInfo)

    return img

def openHIS(fn, mode='r'):

    """
    open Hamamatsu Image Sequence
    return a mockNDarray
    each section contains a HIS attribute,
        which contains hdr, offsetNext and comment
    """
    m = np.memmap(fn, shape=mmap_shape, mode=mode)

    if mmap_shape is None:
        a = _try_openHIS_fastMap(m)
        if a is not None:
            return a

    offset=0
    imgs = []
    while 1: # for i in range(10):
        try:
            img = readSection(m, offset)
        except:
            break
        imgs.append(img)

        offset = img.HIS.offsetNext
    return mockNDarray(*imgs)


