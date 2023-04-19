
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


dir_rmWTT='/home/rts/RTS_2019/conf/'
os.chdir(dir_rmWTT)

os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
    
time.sleep(2)



# TIP

# create symbolic link to saved_wtt_RM/wtip_RM.fits
#cmd = "loadfits 'wtip_RM.fits' tempo"
cmd = "loadfits 'shmim_wtip_RM.fits' tempo_wtip"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "saveflfits tempo_wtip 'wtip_fl.fits'"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "loadfits wtip_fl.fits da_tip"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim rm_wttx"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_tip rm_wttx"

# to show the RM on the GUI... stop apd reading loop, then:
#cmd = "readshmim curv_ord"
#cmd =  "cpsh da_tip curv_ord"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


time.sleep(2)

# TILT
# create symbolic link to saved_wtt_RM/wtilt_RM.fits
#cmd = "loadfits wtilt_RM.fits tempo"
cmd = "loadfits 'shmim_wtilt_RM.fits' tempo_wtilt"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "saveflfits tempo_wtilt wtilt_fl.fits"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "loadfits wtilt_fl.fits da_tilt"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim rm_wtty"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_tilt rm_wtty"


# to show the RM on the GUI... stop apd reading loop, then:
#cmd = "readshmim curv_ord"
#cmd = "cpsh da_tilt curv_ord"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

# remove temporally files
os.system("rm wtilt_fl.fits")
os.system("rm wtip_fl.fits")
