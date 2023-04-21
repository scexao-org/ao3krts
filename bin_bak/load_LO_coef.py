
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



os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(1)

#  LO tip tilt coef

os.system("tmux send-keys -t tm_cacao 'readshmim DMTT_TO_LOTT' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix DMTT_TO_LOTT 3.91 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix DMTT_TO_LOTT -3.91 1 0' C-m") 
time.sleep(1)

#  LO defocus coef
os.system("tmux send-keys -t tm_cacao 'readshmim ADF_TO_LDF' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix ADF_TO_LDF 0.0 0 0' C-m")
time.sleep(0.4)
os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")




#  LO defocus response matrix
os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(1)

    
#cmd = "loadfits LDF_rm_test_fl.fits da_def"
# LOdef_rm_corr_fl.fits became RM_LO_def.fits

# create the simbolic link to saved_LO_RM directory
#cmd = "loadfits RM_LO_def.fits da_def"
cmd = "loadfits shmim_RM_LO_defocus.fits da_def"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim LDF_rm"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh da_def LDF_rm"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")
