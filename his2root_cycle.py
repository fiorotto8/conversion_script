import os,sys
import h5py
import numpy as np
import ROOT
import re
from readerHIS import openHIS
import tqdm
import signal
import ROOT
from datetime import datetime as dt
import signal

def signal_handler(sig, frame):  #trapping signal
    print(str(dt.now())+" - closed by SIGINT, removed .root file not completed run"+str(('%05d' % num)))
    rf.Close()
    os.remove(rf_name)
    sys.exit(0) #stop the cycle

def get_numbers_from_filename(filename):
    return re.search(r'\d+', filename).group(0)

#root and his config
file = open("/mnt/c/Users/Cygnus/Desktop/SOFTWARE/conversion_script/dirconfig.txt", "r")
for string in file:
    exec(string)
file.close()

#get the run numbers to ceonvert and the one already converted
his_num,root_num=[],[]
for filename in os.listdir(his_folder):
    his_num.append(get_numbers_from_filename(filename))
for filename in os.listdir(root_folder):
    root_num.append(get_numbers_from_filename(filename))


to_convert_string=set(his_num).difference(root_num)
to_convert=[int(item) for item in to_convert_string]
to_convert.sort()
#print(to_convert)

if len(to_convert)==0:
    print(str(dt.now())+" - No file to convert!")
    sys.exit()
else:
    print(str(dt.now())+" - Start conversion runs",to_convert)
#cycle and convert
for num in to_convert:
    print(str(dt.now())+" - START converting run"+str(('%05d' % num)))

    prename="/run%05d.HIS" % (num)
    aftername="/histograms_Run%05d.root" % (num)

    his_file=his_folder+prename
    stem, _ = os.path.splitext(his_file)
    runN = stem.split('run')[-1]
    run = runN if len(runN) else 'XXXX'
    try: his = openHIS(his_file)
    except PermissionError:
        print(str(dt.now())+" - File"+str(('%05d' % num))+" is still on data taking, skipping")
        continue 

    rf_name=root_folder+aftername
    rf=ROOT.TFile(rf_name,'recreate')

    for idx, section in enumerate(his):
        signal.signal(signal.SIGINT, signal_handler)
        (nx,ny) = section.shape
        title = stem + ('_%04d' % idx)
        postfix = 'run{run}_ev{ev}'.format(run=run,ev=idx)
        title = 'pic_{pfx}'.format(pfx=postfix)
        h2 = ROOT.TH2S(title,title,nx,0,nx,ny,0,ny)
        h2.GetXaxis().SetTitle('x')
        h2.GetYaxis().SetTitle('y')
        #_ = array2hist(np.fliplr(np.transpose(section)),h2)
        start=np.fliplr(np.transpose(section))
        for i,row in enumerate(start):
            for j,col in enumerate(row):
                h2.SetBinContent(i,j,col)
        h2.Write()
    print(str(dt.now())+" - DONE converting run"+str(('%05d' % num)))
    rf.Close()
print(str(dt.now())+" - Finished")


