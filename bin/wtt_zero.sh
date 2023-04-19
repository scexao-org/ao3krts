#!/bin/sh

###################################################
# Ch. Clergeon 20/06/23
# fast wtt_zero commands (tmux session tm_cacao2)
###################################################

tmux send-keys -t tm_cacao2 'readshmim wtt' C-m
tmux send-keys -t tm_cacao2 'setpix wtt 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix wtt 0 1 0' C-m

tmux send-keys -t tm_cacao2 'readshmim delta_wtt' C-m
tmux send-keys -t tm_cacao2 'setpix delta_wtt 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix delta_wtt 0 1 0' C-m

tmux send-keys -t tm_cacao2 'readshmim wttapply' C-m
tmux send-keys -t tm_cacao2 'imzero wttapply' C-m


tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m

