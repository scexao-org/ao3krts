
#!/usr/bin/env python


###################################################
# Ch. Clergeon 2019/10/07
# slow dm_zero commands (tmux session tm_cacao)
###################################################

from matplotlib import pylab as pltx1
from scipy.ndimage.interpolation import zoom
from pylab import*
from random import randint
import os
import time



os.system('tmux send-keys -t tm_cacao "cacao" C-m')


#--- DMchannel offset
cmd = "readshmim dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)


#-- NEW 12/10/2019

# read cacao_out shared memory and zero the correction channel

cmd = "readshmim cacao_out"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero cacao_out"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp03"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp03"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

#-- LOWFS channels outputs


cmd = "readshmim LO_tt_integ"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_tt_integ"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim LO_tt_disp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_tt_disp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp06"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp06"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

#--


cmd = "readshmim LO_defocus_integ"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_defocus_integ"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim LO_df_disp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_df_disp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp07"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp07"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

#-- HO decompo channels


cmd = "readshmim HO_tip_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero HO_tip_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim HO_tilt_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero HO_tilt_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim HO_defocus_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero HO_defocus_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim HO_sum_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero HO_sum_comp"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp05"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp05"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)



#---- Dchannel disp01 .. not sure 
cmd = "readshmim dm01disp01"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp01"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)


cmd = "readshmim LO_tt_gain"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_tt_gain"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)



cmd = "readshmim LO_defocus_gain"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero LO_defocus_gain"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)





#---- repeat  Dchannel disp00 .. for dV limit  not sure 
cmd = "readshmim dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)

cmd = "readshmim dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
cmd =  "imzero dm01disp00"
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)
time.sleep(0.1)







os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")
