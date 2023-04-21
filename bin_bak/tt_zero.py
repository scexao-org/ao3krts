
#!/usr/bin/env python

from pylab import*
import os
import time

os.system('tmux send-keys -t tm_cacao "cacao" C-m')

time.sleep(1)

os.system("tmux send-keys -t tm_cacao 'readshmim dmTT' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix dmTT 0 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix dmTT 0 1 0' C-m") 

os.system("tmux send-keys -t tm_cacao 'readshmim delta_dmTT' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_dmTT 0 0 0' C-m")
os.system("tmux send-keys -t tm_cacao 'setpix delta_dmTT 0 1 0' C-m") 

os.system("tmux send-keys -t tm_cacao 'readshmim dmTTapply' C-m")
os.system("tmux send-keys -t tm_cacao 'imzero dmTTapply' C-m")


# NEW: 12/17/2019 : reset LOWFS tt integ and disp

os.system("tmux send-keys -t tm_cacao 'readshmim LO_tt_integ' C-m")
os.system("tmux send-keys -t tm_cacao 'imzero LO_tt_integ' C-m")

os.system("tmux send-keys -t tm_cacao 'readshmim LO_tt_disp' C-m")
os.system("tmux send-keys -t tm_cacao 'imzero LO_tt_disp' C-m")




os.system("tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m")
os.system("tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m")

os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")
    
