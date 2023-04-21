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



os.chdir("/home/rts/RTS_2019/conf/saved_wTT_flats/")

#save the new flat in the saved flats directory ( /RTS_2019/conf/saved_wTT_flats/ )
os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/saved_wTT_flats/" C-m')

os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(1)
os.system("tmux send-keys -t tm_cacao 'readshmim wttapply' C-m")
os.system("tmux send-keys -t tm_cacao 'savefits wttapply toto.fits' C-m")
time.sleep(0.5)
os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

#rename wavefront tip tilt flat to today's date
jour = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
name="wTT_flat"+"_"+jour+".fits"
print(name)
cmd2 ="mv toto.fits "+name
os.system(cmd2)


#modify the main symbolic link at the source of the conf directory
os.chdir("/home/rts/RTS_2019/conf/")
os.system("rm shmim_wTT_flat.fits")
cmd3 = "ln -s saved_wTT_flats/"+name+" shmim_wTT_flat.fits"
os.system(cmd3)

#save the new configuration (all symbolic links) to the saved_conf directory with today's date
name = "saved_conf_"+jour
cmd4 = "mkdir conf_history/"+name
os.system(cmd4)
cmd5 = "cp -pr shmim* conf_history/"+name
os.system(cmd5)

