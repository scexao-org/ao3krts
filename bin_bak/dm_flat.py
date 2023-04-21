#!/usr/bin/env python

from pylab import*
import os
import time


#os.chdir("/home/rts/RTS/AO188_2018_LGS/conf/")
os.chdir("/home/rts/RTS_2019/conf/")
#os.system("rm flat_fl.fits")

# start cacao
os.system('tmux send-keys -t tm_cacao "cd /home/rts/RTS_2019/conf/" C-m')
os.system('tmux send-keys -t tm_cacao "cacao" C-m')

time.sleep(1.0)    



#--------------------- Load Flat --------------------------


#cmd = "loadfits dm_flat.fits tempo" replaced by symbolic link
cmd = "loadfits shmim_dm_flat.fits tempo"

print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#convert the best flat  in float = flat_fl.fits
cmd = "saveflfits tempo flat_fl.fits"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#-----------------------------------------------------------



# load the float values into "flat"
cmd = "loadfits flat_fl.fits flat"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

# read shared memory to receive the flat : dm comb channel 00
cmd = "readshmim dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

# copy "flat values" to the dm comb channel 00
cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#redo for hardware limitation (case flat values > limit per iter.)
cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#redo for hardware limitation (case flat values > limit per iter.)
cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#redo for hardware limitation (case flat values > limit per iter.)
cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)



#-- NEW 12/10/2019

# read cacao_out shared memory and zero the correction channel

#-- cacao output
cmd = "readshmim cacao_out"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero cacao_out"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim dm01disp03"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero dm01disp03"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


#-- LOWFS channels outputs

cmd = "readshmim LO_tt_integ"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero LO_tt_integ"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim LO_tt_disp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero LO_tt_disp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim dm01disp06"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero dm01disp06"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#--

cmd = "readshmim LO_defocus_integ"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero LO_defocus_integ"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim LO_df_disp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero LO_df_disp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "readshmim dm01disp07"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero dm01disp07"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

#-- HO decompo channels


cmd = "readshmim HO_tip_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero HO_tip_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim HO_tilt_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero HO_tilt_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim HO_defocus_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero HO_defocus_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim HO_sum_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero HO_sum_comp"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)


cmd = "readshmim dm01disp05"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd = "imzero dm01disp05"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)




# copy "flat values" to the dm comb channel 00 (4 times due to hardware dV limitation)

cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)

cmd =  "cpsh flat dm01disp00"
print(cmd)
cmd1 ="tmux send-keys -t tm_cacao"+" '"+cmd+"'"+" "+"C-m"
os.system(cmd1)



# exit cacao
os.system("tmux send-keys -t tm_cacao 'exitCLI' C-m")

#remove the temporally files
os.chdir("/home/rts/RTS_2019/conf/")
os.system("rm flat_fl.fits")
