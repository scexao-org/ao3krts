#!/bin/sh

###################################################
# Ch. Clergeon 2020/07/06
# startup script for AO188 interface communication
# (SCEXAO test with new DM interface script)
# for simulator only
###################################################




# ------------------------
# CACAO startup
# ------------------------



echo -e "\n"
echo -e "\e[1;32mStart NEW CACAO SIMULATOR\e[0m \n"
echo -e "\n"
echo -e "\n"

echo -e "\e[1;32mSim:Load conf files and start process... \e[0m \n"

(cd /home/rts/AOloop/ao188lhs_new/ ; cacao-task-manager -X 4 cacaoloop-ao188lhs)

sleep 4


# Sim - StreamDelay 01
#echo "confstart streamDelay-01" >> /milk/shm/ao188lhs_fpsCTRL.fifo
echo "confstart streamDelay-01" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "confupdate streamDelay-01" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "runstart streamDelay-01" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 5

# Sim - simmvmgpu-1
echo "confstart simmvmgpu-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "confupdate simmvmgpu-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "runstart simmvmgpu-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 5

# Sim - acquWFS-1
echo "confstart acquWFS-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "runstart acquWFS-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 5


echo -e "\n"
echo -e "\e[1;31mSim CACAO setup started (run process ON). \e[0m \n"
echo -e "\e[1;33mprocess running in:\e[0m \n"
echo -e "\e[1;33mSee tmux a -t ao188lhs_new_fpsCTRL\e[0m \n"
echo -e "\n"
echo -e "\n"

### ????### " status proces ??? feedback CRASHED OR NOT CRASHED?

echo -e "\n"
echo -e "\n"




# ------------------------
# init fpdp boards
# ------------------------

echo -e "\n"
echo -e "\e[1;32mInitialize fpdp boads connections\e[0m \n"
echo -e "\n"

/home/rts/RTS_2019/bin/ctr_init
sleep 3
/home/rts/RTS_2019/bin/ctr_init
sleep 3
# ------------------------
# START/init (create) tmux sessions
# ------------------------

echo -e "\n"
echo -e "\e[1;32mInitialize tmux sessions...\e[0m \n"
echo -e "\n"
# ??
tmux new-session -d -s tm_ao188
tmux new-session -d -s tm_tt_cntr
tmux new-session -d -s tm_log_dm
tmux new-session -d -s tm_log_apd
tmux new-session -d -s tm_dm_cnt
# main tmux sessions
tmux new-session -d -s tm_cacao
tmux new-session -d -s tm_cacao2
tmux new-session -d -s tm_fpdp_dm
tmux new-session -d -s tm_fpdp_dm_logic
tmux new-session -d -s tm_fpdp_apd
tmux new-session -d -s tm_chris

tmux new-session -d -s tm_ptp

# -----------------------------------------
# Start CACAO in the tmux tm_cacao2 session
#------------------------------------------

# kill cacao if still running in the session
tmux send-keys -t tm_cacao2 "^C" C-m
sleep 0.5
tmux send-keys -t tm_cacao2 "cd /home/rts/RTS_2019/conf/" C-m
sleep 0.5
tmux send-keys -t tm_cacao2 "cacao" C-m
sleep 1

# ---------------------------
# Start the APD communication
# ---------------------------

echo -e "\e[1;32mStart APDs communication... \e[0m\n"

tmux new-session -d -s tm_fpdp_apd
tmux send-keys -t tm_fpdp_apd 'cd /home/rts/RTS_2019/APD3/ ' C-m
tmux send-keys -t tm_fpdp_apd './fpdptest_new_nour_APD' C-m
tmux detach -s tm_fpdp_apd

echo -e "\e[1;31mAPDs communication started! \e[0m\n"
sleep 3

# --------------------------------------------------
# Start the DM communication - STEP 1: DM main (NGS)
# --------------------------------------------------

echo -e "\e[1;32mStart DM communication... \e[0m\n"

tmux new-session -d -s tm_fpdp_dm
tmux send-keys -t tm_fpdp_dm 'cd /home/rts/RTS_2019/DM/ ' C-m
tmux send-keys -t tm_fpdp_dm './fpdptest_LGS_DM_SCEXAO' C-m
tmux send-keys -t tm_fpdp_dm 'DM_OFF' C-m
tmux detach -s tm_fpdp_dm

echo -e "\e[1;31mDM communication in stand-by ... \e[0m\n"

sleep 3
#--------------------------------------------
# Load configuration files in shared memories
#--------------------------------------------

echo -e "\e[1;32mload configuration files...\e[0m\n"
python /home/rts/RTS_2019/bin/load_LO_coef.py
sleep 1
python /home/rts/RTS_2019/bin/load_tt_RM.py
sleep 1
python /home/rts/RTS_2019/bin/load_wtt_RM.py
sleep 1
python /home/rts/RTS_2019/bin/load_ADF_RM.py
sleep 1

#----------------------------
# Load dmTT flat and wtt flat
#----------------------------

echo -e "\e[1;32mload dmTT amd wTT flats...\e[0m\n"
python /home/rts/RTS_2019/bin/tt_flat.py
sleep 1
python /home/rts/RTS_2019/bin/wtt_flat.py
sleep 1
#----------------------------------------------------
# Start the DM communication - STEP 2: DM LOGIC (LGS)
#----------------------------------------------------

echo -e "\e[1;32mStart DM LOGIC script... \e[0m\n"

tmux new-session -d -s tm_fpdp_dm_logic
tmux send-keys -t tm_fpdp_dm_logic 'cd /home/rts/RTS_2019/DM/ ' C-m
tmux send-keys -t tm_fpdp_dm_logic './fpdptest_LGS_logic' C-m
tmux detach -s tm_fpdp_dm_logic
echo -e "\e[1;31mDM LOGIC started ... \e[0m\n"
sleep 3

#-----------------
# zero DM channels
#-----------------

echo -e "\e[1;32mZero DM channels...\e[0m\n"
python /home/rts/RTS_2019/bin/dm_zero.py
sleep 1


#--------------------------------
# Load default NGS control matrix
#--------------------------------

echo -e "\e[1;32mLoading the default Control Matrix for NGS mode...\e[0m\n"
python /home/rts/RTS_2019/bin/load_NGS_CM.py
echo -e "\e[1;31mControl Matrix (NGS) loaded...\e[0m\n"

sleep 1



# Set default Httg and Hdfg to 1 (NGS)

tmux send-keys -t tm_cacao "cacao" C-m

sleep 2

tmux send-keys -t tm_cacao 'readshmim Httg' C-m
tmux send-keys -t tm_cacao 'setpix Httg 1 0 0' C-m

sleep 1

tmux send-keys -t tm_cacao 'readshmim Hdfg' C-m
tmux send-keys -t tm_cacao 'setpix Hdfg 1 0 0' C-m

tmux send-keys -t tm_cacao 'exitCLI' C-m

sleep 2


#-----------------------------------------------------------
# START Loop process !
#-----------------------------------------------------------

# Sim - LoopRun-1

#echo "confstart loopRUN-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo




echo "setval loopRUN-1.wfsrefON OFF">>/milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1
echo "setval loopRUN-1.loopZERO OFF">>/milk/shm/ao188lhs_new_fpsCTRL.fifo
sleep 1





read -p "ARE ALL configuration well loaded and process ready to sart? (yes/no)" response
if [[ $response == "yes" ]] 

then


echo "runstart loopRUN-1" >> /milk/shm/ao188lhs_new_fpsCTRL.fifo


#-----------------------------------------------------------
# Start the DM communication - FINAL STEP: start DM writting
#-----------------------------------------------------------

echo -e "\e[1;32mStart DM writting... \e[0m\n"

tmux new-session -d -s tm_fpdp_dm
tmux send-keys -t tm_fpdp_dm 'cd /home/rts/RTS_2019/DM/ ' C-m
tmux send-keys -t tm_fpdp_dm 'DM' C-m
tmux detach -s tm_fpdp_dm
sleep 3

echo -e "\e[1;31mDM communication started ... \e[0m\n"


echo -e "\e[1;32m REstart g2if ... \e[0m\n"
#g2if_restart
sleep 3



echo -e "\n"
echo -e "\n"
echo -e "\e[1;34mRTS interface scripts started ! \e[0m\n"

fi



