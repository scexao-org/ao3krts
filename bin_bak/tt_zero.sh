#!/bin/sh

###################################################
# Ch. Clergeon 2019/10/07
# fast tt_zero commands (tmux session tm_cacao2)
###################################################

tmux send-keys -t tm_cacao2 'readshmim dmTT' C-m
tmux send-keys -t tm_cacao2 'setpix dmTT 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix dmTT 0 1 0' C-m

tmux send-keys -t tm_cacao2 'readshmim delta_dmTT' C-m
tmux send-keys -t tm_cacao2 'setpix delta_dmTT 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix delta_dmTT 0 1 0' C-m

tmux send-keys -t tm_cacao2 'readshmim dmTTapply' C-m
tmux send-keys -t tm_cacao2 'imzero dmTTapply' C-m


#-- LOWFS tip tilt channels outputs

tmux send-keys -t tm_cacao2 "readshmim LO_tt_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_integ" C-m

tmux send-keys -t tm_cacao2 "readshmim LO_tt_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_disp" C-m



tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m

