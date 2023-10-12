# Conversion (and Upload) of .HIS files

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
00 * * * * python3 path/to/his2root_cycle.py >> path/to/cron_log.txt 2>&1
59 * * * * ps -axu | grep his2root_cycle.py | awk '{print $2}' | xargs kill -SIGINT
```
This makes the code running every hour. If the conversion is not finished in time, the script is killed and the .root file on processing is deleted to avoid to save corroupted root files.
