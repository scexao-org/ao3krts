
#!/usr/bin/env python


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
import subprocess
from termcolor import colored

# open the loop on AO188 and close APD  shutters (default safety)

#t=colored('system will now  shutdown...','blue')
#print(t)
#os.system("tmux send-keys -t tm_ao188 'loop off 0' C-m")
#time.sleep(3)
#os.system("tmux send-keys -t tm_ao188 'howfs lash close' C-m")
#time.sleep(3)
#os.system("tmux send-keys -t tm_ao188 'shutdown_ao188.pl' C-m")

while var !='yes' and var !='no':

    t=colored("AO loop not running, safe to turn off AO ? (yes/no): ","red")
    var = str(input(t))
    t = colored('Thank you ... the system will now shutdown ...')
    print(t)

if var == 'yes':

    t=colored('system will now  shutdown...','blue')
    print(t)
    #os.system("tmux send-keys -t tm_ao188 'loop off 0' C-m")
    #time.sleep(3)
    os.system("tmux send-keys -t tm_ao188 'howfs lash close' C-m")
    time.sleep(3)
    os.system("tmux send-keys -t tm_ao188 'shutdown_ao188.pl' C-m")
    time.sleep(3)
    os.system("tmux send-keys -t tm_ao188 'yes' C-m")
    time.sleep(80)
    t= colored('dm zero..','blue')
    print(t)
    os.system("tmux send-keys -t tm_dm_cnt 'python dm_zero.py' C-m")
    time.sleep(4)
    t= colored('tt zero..','blue')
    print(t)
    os.system("tmux send-keys -t tm_tt_cntr 'python tt_zero.py' C-m")
    time.sleep(20)
    t= colored('Stop Fpdp boards connection...','blue')
    print(t)
    os.system("tmux send-keys -t tm_fpdp_dm '\x03' C-m")
    os.system("tmux send-keys -t tm_fpdp_apd '\x03' C-m")
    time.sleep(4)

    t=colored('system is now shutdown...','blue')
    print(t)
else:
    t = colored('please turn off the AO loop control before proceeding')
    print(t)


