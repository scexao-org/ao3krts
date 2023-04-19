
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

# BEST !!!! 2018/11/01
#s.system("tmux send-keys -t tm_cacao 'setpix dmTT 110 0 0' C-m")
#os.system("tmux send-keys -t tm_cacao 'setpix dmTT -2800 1 0' C-m") 
# ----


os.chdir("/home/rts/RTS_2019/conf/")

os.system('tmux send-keys -t tm_cacao "cacao" C-m')

time.sleep(1)
os.system("tmux send-keys -t tm_cacao 'readshmim dmTT' C-m")



# --- load last saved TT flat from conf directory : dmTTsaved.fits

# Symbolic link created to point to the saved_dmTT_flats directory
#hdulist = fits.open("dmTTsaved.fits")
hdulist = fits.open("shmim_dmTT_flat.fits")
fits=hdulist[0].data
flat_tip=fits[0,0]
flat_tilt=fits[0,1]

cmd = "setpix dmTT "+str(flat_tip)+" 0 0"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "setpix dmTT "+str(flat_tilt)+" 1 0"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#os.system("tmux send-keys -t tm_cacao 'setpix dmTT 624 0 0' C-m")
#os.system("tmux send-keys -t tm_cacao 'setpix dmTT -2666 1 0' C-m") 

os.system("tmux send-keys -t tm_cacao 'readshmim delta_dmTT' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_dmTT 0 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_dmTT 0 1 0' C-m") 



# NEW 12/16/2019 : reset tip tilt integers on LOWFS side
os.system("tmux send-keys -t tm_cacao 'readshmim LO_tt_integ' C-m")
os.system("tmux send-keys -t tm_cacao 'imzero LO_tt_integ' C-m")

os.system("tmux send-keys -t tm_cacao 'readshmim LO_tt_disp' C-m")
os.system("tmux send-keys -t tm_cacao 'imzero LO_tt_disp' C-m")








os.system("tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m")
os.system("tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m")

os.system("tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m")
os.system("tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m")

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

    
