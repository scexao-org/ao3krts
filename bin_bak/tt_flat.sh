#!/bin/sh

###################################################
# Ch. Clergeon 2019/10/07
# fast tt_flat commands (tmux session tm_cacao2)
###################################################





# --- load last saved TT flat from conf directory : dmTTsaved.fits


tmux send-keys -t tm_cacao2 'rm toto' C-m
tmux send-keys -t tm_cacao2 'rm toto_bis' C-m


# load the last saved dm tip tilt fits file - dimesion 8x1 in shared memory
tmux send-keys -t tm_cacao2 'loadfits shmim_dmTT_flat.fits toto' C-m

# crop in new shared memory the file keeping the first two pixels
tmux send-keys -t tm_cacao2 'extractim toto toto_bis 2 1 0 0' C-m

#load the dmTT shared memory: dimension 2x1
tmux send-keys -t tm_cacao2 'readshmim dmTT' C-m

#copy the fits two first pixels to dmTT shared memory
tmux send-keys -t tm_cacao2 'cpsh toto_bis dmTT' C-m

#reset the delta_dmTT shared memory
tmux send-keys -t tm_cacao2 'readshmim delta_dmTT' C-m
tmux send-keys -t tm_cacao2 'setpix delta_dmTT 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix delta_dmTT 0 1 0' C-m


#-- LOWFS tip tilt channels outputs

tmux send-keys -t tm_cacao2 "readshmim LO_tt_integ" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_integ" C-m

tmux send-keys -t tm_cacao2 "readshmim LO_tt_disp" C-m
tmux send-keys -t tm_cacao2 "imzero LO_tt_disp" C-m

#tmux send-keys -t tm_cacao2 "readshmim dm01disp06" C-m
#tmux send-keys -t tm_cacao2 "imzero dm01disp06" C-m


#trigger the dmTT flat writting on the DAC
tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m
tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m


    
