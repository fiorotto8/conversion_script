# Conversion Upload and Reco of .HIS files

## Automatic conversion

`his2root_cycle.py` is the code that convert the .HIS file to .root files.
It checks the run numbers present in a starting folder that contains the .HIS file (should be `run#####.HIS`) and compare the .root files already converted in a target directory. Both the folders are hard-coded in this script.
A cycle is started that converts all the missing .root files.
.HIS files are not removed after the conversion for now.

### Setting up a cronjob

The idea is to let this script running in background and convert the .HIS files as soon they are created.
To set up cronjob service at machine start in WSL check [here](https://www.howtogeek.com/746532/how-to-launch-cron-automatically-in-wsl-on-windows-10-and-11/).
If cronjob service is running you can setup the cronjob with `crontab -e` and write the following lines
```
PYTHONPATH=path/to/root/lib
00 * * * * python3 path/to/his2root_cycle.py >> path/to/cronCONV_log.txt 2>&1
59 * * * * ps -axu | grep his2root_cycle.py | awk '{print $2}' | xargs kill -SIGINT
```
This makes the code running every hour. If the conversion is not finished in time, the script is killed and the .root file on processing is deleted to avoid to save corroupted root files.

An eventual error on the cronlog.txt is normal:
```
sh: 1: root-config: not found
Error in <TUnixSystem::GetFromPipe>: command "root-config --has-dataframe" returned 32512
```

## Upload on cloud
Open a shell and launch `source activate_agent.sh`
After that you can launch `python3 Cycle_ROOT2cloud.py <startRunNum> <stopRunNum>`
Check oftenly the shell beacuse sometimes the oidc-agent is crashing...

## Semi-automatic Reconstruction
The reconstruction code is a pain in the a**...
So a working version of it is mounted of the MANGO PC, for different PC and version we should check
This version is a slighly modified from the Winter23-patch2, but it cannot still work on multi-core 
The strategy is to reconstruct **one** run every 20min via cronjob, any errors should be handeled manually.
*Attention*:
- pedestal runs should be artificially created in the `reco_folder`, otherwise you reconstruct them (not critical)
- check on the `cronRECO_log.txt` that the reconstrcions succeded otherwise you should remove the .root not completed and the cron will re-reconstruct it
- crontab line: `*/20 * * * * python3 path/to/recoCycle.py >> path/to/cronRECO_log.txt 2>&1`
