#!/bin/sh

###################################################
# Ch. Clergeon 2019/10/07
# fast dm_flat commands (tmux session tm_cacao2)
###################################################



#--------------------- Load Flat --------------------------


tmux send-keys -t tm_cacao2 "rm tempo" C-m

tmux send-keys -t tm_cacao2 "loadfits shmim_dm_flat.fits tempo" C-m

#convert the best flat  in float = flat_fl.fits

tmux send-keys -t tm_cacao2 "saveflfits tempo flat_fl.fits" C-m



#-----------------------------------------------------------


# load the float values into "flat"

tmux send-keys -t tm_cacao2 "rm flat" C-m


tmux send-keys -t tm_cacao2 "loadfits flat_fl.fits flat" C-m


# read shared memory to receive the flat : dm comb channel 00

tmux send-keys -t tm_cacao2 "readshmim dm01disp00" C-m


# copy "flat values" to the dm comb channel 00 (4 times due to hardware dV limitation)

tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m




#-- NEW 12/10/2019

# read cacao_out shared memory and zero the correction channel

#-- cacao output
tmux send-keys -t tm_cacao2 "readshmim cacao_out" C-m
tmux send-keys -t tm_cacao2 "imzero cacao_out" C-m

tmux send-keys -t tm_cacao2 "readshmim dm01disp03" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp03" C-m

#-- LOWFS channels outputs

tmux send-keys -t tm_cacao2 "readshmim LO_tt_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_integ" C-m

tmux send-keys -t tm_cacao2 "readshmim LO_tt_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_disp" C-m

tmux send-keys -t tm_cacao2 "readshmim dm01disp06" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp06" C-m

#--
tmux send-keys -t tm_cacao2 "readshmim LO_defocus_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_defocus_integ" C-m

tmux send-keys -t tm_cacao2 "readshmim LO_df_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_df_disp" C-m

tmux send-keys -t tm_cacao2 "readshmim dm01disp07" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp07" C-m

#-- HO decompo channels

tmux send-keys -t tm_cacao2 "readshmim HO_tip_comp" C-m
tmux send-keys -t tm_cacao2 "imzero HO_tip_comp" C-m

tmux send-keys -t tm_cacao2 "readshmim HO_tilt_comp" C-m
tmux send-keys -t tm_cacao2 "imzero HO_tilt_comp" C-m

tmux send-keys -t tm_cacao2 "readshmim HO_defocus_comp" C-m
tmux send-keys -t tm_cacao2 "imzero HO_defocus_comp" C-m

tmux send-keys -t tm_cacao2 "readshmim HO_sum_comp" C-m
tmux send-keys -t tm_cacao2 "imzero HO_sum_comp" C-m

tmux send-keys -t tm_cacao2 "readshmim dm01disp05" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp05" C-m


# copy "flat values" to the dm comb channel 00 (4 times due to hardware dV limitation)

tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m
tmux send-keys -t tm_cacao2 "cpsh flat dm01disp00" C-m


# exit cacao
#tmux send-keys -t tm_cacao2 "^C" C-m
tmux send-keys -t tm_cacao2 "exitCLI" C-m
sleep 1
#remove the temporally files

tmux send-keys -t tm_cacao2 "cd /home/rts/RTS_2019/conf/" C-m
tmux send-keys -t tm_cacao2 "rm flat_fl.fits" C-m

#restart cacao
tmux send-keys -t tm_cacao2 "cacao" C-m

