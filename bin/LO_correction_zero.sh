#!/bin/sh


###################################################
# Ch. Clergeon 2019/10/07
# fast dm_zero commands (tmux session tm_cacao2)
###################################################


#-- LOWFS channels outputs

tmux send-keys -t tm_cacao2 "readshmim LO_tt_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_integ" C-m
sleep 0.1

tmux send-keys -t tm_cacao2 "readshmim LO_tt_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_disp" C-m
sleep 0.1

tmux send-keys -t tm_cacao2 "readshmim dm01disp06" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp06" C-m
sleep 0.1

#--
tmux send-keys -t tm_cacao2 "readshmim LO_defocus_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_defocus_integ" C-m
sleep 0.1

tmux send-keys -t tm_cacao2 "readshmim LO_df_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_df_disp" C-m
sleep 0.1

tmux send-keys -t tm_cacao2 "readshmim dm01disp07" C-m
tmux send-keys -t tm_cacao2 "imzero dm01disp07" C-m
sleep 0.1

#-- HO decompo channels

#tmux send-keys -t tm_cacao2 "readshmim HO_tip_comp" C-m
#tmux send-keys -t tm_cacao2 "imzero HO_tip_comp" C-m

#tmux send-keys -t tm_cacao2 "readshmim HO_tilt_comp" C-m
#tmux send-keys -t tm_cacao2 "imzero HO_tilt_comp" C-m

#tmux send-keys -t tm_cacao2 "readshmim HO_defocus_comp" C-m
#tmux send-keys -t tm_cacao2 "imzero HO_defocus_comp" C-m

#tmux send-keys -t tm_cacao2 "readshmim HO_sum_comp" C-m
#tmux send-keys -t tm_cacao2 "imzero HO_sum_comp" C-m

#tmux send-keys -t tm_cacao2 "readshmim dm01disp05" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp05" C-m


#-- repeat zero dm01disp00 for dV limit


#tmux send-keys -t tm_cacao2 "readshmim dm01disp00" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp00" C-m
#
#tmux send-keys -t tm_cacao2 "readshmim dm01disp00" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp00" C-m

#tmux send-keys -t tm_cacao2 "readshmim dm01disp00" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp00" C-m

#tmux send-keys -t tm_cacao2 "readshmim dm01disp00" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp00" C-m



#---- Dchannel disp01 .. not sure 

#tmux send-keys -t tm_cacao2 "readshmim dm01disp01" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp01" C-m
#sleep 0.1


#tmux send-keys -t tm_cacao2 "readshmim LO_tt_gain" C-m
#tmux send-keys -t tm_cacao2 "imzero LO_tt_gain" C-m
#sleep 0.1


#tmux send-keys -t tm_cacao2 "readshmim LO_defocus_gain" C-m
#tmux send-keys -t tm_cacao2 "imzero LO_defocus_gain" C-m
sleep 0.1

