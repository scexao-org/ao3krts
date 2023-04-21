
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

os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')
time.sleep(2)

cmd = "loadfits 'shmim_NGS_control_matrix.fits' tempo"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


#cmd = "readshmim aol1_contrM"
cmd = "readshmim aol1_CMat"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#cmd =  "cpsh tempo aol1_contrM"
cmd =  "cpsh tempo aol1_CMat"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#cmd =  "cpsh aol1_contrM aol1_contrMc"
#print(cmd)
#cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
#os.system(cmd1)

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

