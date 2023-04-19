
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


#dir_rmTT='/home/rts/RTS/AO188_2018_LGS2/conf/'
#os.chdir(dir_rmTT)
#hdulist = fits.open('rep_tilt.fits')
#tilt=1.0*hdulist[0].data
#hdulist = fits.open('rep_tip.fits') 
#tip=1.0*hdulist[0].data

os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(2)


#load ADF response matrix
# RM_AU1_fl.fits became RM_ADF.fits"

# create the simbolinc link to saved_ADF_RM
#cmd = "loadfits RM_ADF.fits da_def"
cmd = "loadfits shmim_RM_ADF.fits da_def"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim ADF_rm"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_def ADF_rm"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")


