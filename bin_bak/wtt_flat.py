
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

# BEST !!!! in accordance with past RTS values
#s.system("tmux send-keys -t tm_cacao 'setpix wtt 6265 0 0' C-m")
#os.system("tmux send-keys -t tm_cacao 'setpix wtt 4364 1 0' C-m") 
# ----

os.chdir("/home/rts/RTS_2019/conf/")
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(1)
os.system("tmux send-keys -t tm_cacao 'readshmim wtt' C-m")


# -- WTT FLAT case TT FLAT apllied

# point to the new symbolic link in the saved_wTT_flats directory
#hdulist = fits.open("WTTsaved.fits")
hdulist = fits.open("shmim_wTT_flat.fits")
fits=hdulist[0].data
"""
flat_tip=fits[0,0]
flat_tilt=fits[0,1]

cmd = "setpix wtt "+str(flat_tip)+" 0 0"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "setpix wtt "+str(flat_tilt)+" 1 0"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

"""
#""" manual
os.system("tmux send-keys -t tm_cacao 'setpix wtt 6265 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix wtt 4364 1 0' C-m")
#---"""

os.system("tmux send-keys -t tm_cacao 'readshmim delta_wtt' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_wtt 0 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_wtt 0 1 0' C-m") 

os.system("tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m")
os.system("tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m")

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

    
