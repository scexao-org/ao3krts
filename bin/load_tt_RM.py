
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


dir_rmTT='/home/rts/RTS_2019/conf/'
os.chdir(dir_rmTT)

#hdulist = fits.open('rep_tilt.fits')
#tilt=1.0*hdulist[0].data

#hdulist = fits.open('rep_tip.fits') 
#tip=1.0*hdulist[0].data

#os.system("rm tilt_fl.fits")
#os.system("rm tip_fl.fits")

os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
    
time.sleep(2)


# TIP

# create symbolic link to saved_tt_RM/tip_RM.fits
#cmd = "loadfits 'tip_RM.fits' tempo"
cmd = "loadfits 'shmim_tip_RM.fits' tempo_tip"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "saveflfits tempo_tip 'tip_fl.fits'"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "loadfits tip_fl.fits da_tip"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim rm_ttx"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_tip rm_ttx"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)




# TILT
# create symbolic link to saved_tt_RM/tilt_RM.fits
#cmd = "loadfits tilt_RM.fits tempo"
cmd = "loadfits 'shmim_tilt_RM.fits' tempo_tilt"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "saveflfits tempo_tilt tilt_fl.fits"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "loadfits tilt_fl.fits da_tilt"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim rm_tty"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_tilt rm_tty"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)





os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")


# remove temporally files 
os.system("rm tilt_fl.fits")
os.system("rm tip_fl.fits")
