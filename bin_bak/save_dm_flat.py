#!/usr/bin/env python

from astropy.io import fits
import numpy as np
import matplotlib
from matplotlib import pylab as pltx1
from scipy.ndimage.interpolation import zoom
from pylab import*
from random import randint
from matplotlib.figure import Figure
import os
import glob
import time
from datetime import datetime


os.chdir("/home/rts/RTS_2019/conf/saved_dmflats/")

#save the new flat in the saved flats directory ( /RTS_2019/conf/saved_dmflats/ )
os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/saved_dmflats/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(1)
os.system("tmux send-keys -t tm_cacao 'readshmim dm01disp' C-m")

#os.system("tmux send-keys -t tm_cacao 'savefits dm01disp dm_flat.fits' C-m")
cmd = "savefits dm01disp toto.fits"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

#rename flat to today's date
jour = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
name="dm_flat"+"_"+jour+".fits"
print(name)
cmd2 ="mv toto.fits "+name
os.system(cmd2)

#modify the main symbolic link at the source of the conf directory
os.chdir("/home/rts/RTS_2019/conf/")
os.system("rm shmim_dm_flat.fits")
cmd3 = "ln -s saved_dmflats/"+name+" shmim_dm_flat.fits"
os.system(cmd3)
#save the new configuration (all symbolic links) to the conf_history directory with today's date
name = "saved_conf_"+jour
cmd4 = "mkdir conf_history/"+name
os.system(cmd4)
cmd5 = "cp -pr shmim* conf_history/"+name
os.system(cmd5)

