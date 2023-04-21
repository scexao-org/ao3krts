
#!/bin/sh

###################################################
# Ch. Clergeon 2020/06/23
# fast wtt_flat commands (tmux session tm_cacao2)
###################################################



# BEST !!!! in accordance with past RTS values
#s.system("tmux send-keys -t tm_cacao 'setpix wtt 6265 0 0' C-m")
#os.system("tmux send-keys -t tm_cacao 'setpix wtt 4364 1 0' C-m") 
# ----



# load the last saved dm tip tilt fits file - dimesion 8x1 in shared memory
tmux send-keys -t tm_cacao2 'loadfits shmim_wTT_flat.fits toto' C-m





# crop in new shared memory the file keeping the first two pixels
#tmux send-keys -t tm_cacao2 'extractim toto toto_bis 2 1 0 0' C-m

#load the dmTT shared memory: dimension 2x1
tmux send-keys -t tm_cacao2 'readshmim wtt' C-m

tmux send-keys -t tm_cacao2 'setpix wtt 6265 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix wtt 4364 1 0' C-m


tmux send-keys -t tm_cacao2 'readshmim delta_wtt' C-m
tmux send-keys -t tm_cacao2 'setpix delta_wtt 0 0 0' C-m
tmux send-keys -t tm_cacao2 'setpix delta_wtt 0 1 0' C-m

#trigger the dmTT flat writting on the DAC
tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m
tmux send-keys -t tm_cacao2 'readshmim dmvoltf' C-m
tmux send-keys -t tm_cacao2 'imsetsempost dmvoltf -1' C-m


    
