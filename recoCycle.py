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
import time

def signal_handler(sig, frame):  #trapping signal
    print(str(dt.now())+" - closed by SIGINT, removed .root file not completed run"+str(('%05d' % num)))
    os.remove(name)
    sys.exit(1) #stop the cycle

def get_numbers_from_filename(filename):
    return re.search(r'\d+', filename).group(0)

#root and reco config
file = open("/mnt/c/Users/Cygnus/Desktop/SOFTWARE/conversion_script/dirconfig.txt", "r")
for string in file:
    exec(string)
file.close()

#get the run numbers to ceonvert and the one already converted
reco_num,root_num=[],[]
for filename in os.listdir(reco_folder):
    reco_num.append(get_numbers_from_filename(filename))
for filename in os.listdir(root_folder):
    root_num.append(get_numbers_from_filename(filename))


to_convert_string=set(root_num).difference(reco_num)
to_convert=[int(item) for item in to_convert_string]
to_convert.sort()
#print(to_convert)

if len(to_convert)==0:
    print(str(dt.now())+" - No file to reconstruct!")
    sys.exit()
else:
    print(str(dt.now())+" - Start reconstruction runs",to_convert)
#cycle and convert
num=to_convert[0]
name=reco_folder+"/reco_run%05d_3D.root" % (num)
#rf=ROOT.TFile(name,'recreate')
print(str(dt.now())+" - START reconstruct run"+str(('%05d' % num)))
os.system("cd /mnt/c/Users/Cygnus/Desktop/SOFTWARE/reconstruction && python3 reconstruction.py configFile_MANGO.txt -t /mnt/e/MANGO_ROOTconverted --pdir ./output_plots -r "+str(('%05d' % num))+" --outdir "+str(reco_folder))
print(str(dt.now())+" - FINISH reconstruct run"+str(('%05d' % num)))
signal.signal(signal.SIGINT, signal_handler)
