#!/bin/sh

###################################################
# Ch. Clergeon 2019/09/23
# startup script for AO188 interface communication
# HARDWARE
###################################################


# ------------------------
# CACAO startup
# ------------------------

echo -e "\n"
echo -e "\e[1;32mStart CACAO\e[0m \n"
echo -e "\n"
echo -e "\n"

# load configuration file
echo -e "\e[1;32mLoad CACAO configuration file... \e[0m \n"
source /home/rts/AOloop/cacaovars.ao188.bash
echo -e "\n"
echo -e "\e[1;31mCACAO configuratin file loaded. \e[0m \n"
sleep 3
 
# start conf process (DM comb - etc ...)
echo -e "\e[1;32mStart CACAO setup: start configuration process... \e[0m \n"
cacao-setup
sleep 15
echo -e "\n"
echo -e "\e[1;31mCACAO setup started (conf process ON). \e[0m \n"
echo -e "\e[1;33mprocess running in:\e[0m \n"
echo -e "\e[1;33mSee tmux a -t ao188_fpsCTRL\e[0m \n"
echo -e "\n"
echo -e "\n"

# start running process
echo -e "\e[1;32mStart CACAO setup: start running process... \e[0m \n"


# Dm comb 01
#echo "confstart DMcomb-01" >> /milk/shm/ao188_fpsCTRL.fifo
echo "runstart DMcomb-01" >> /milk/shm/ao188_fpsCTRL.fifo
sleep 5

# Sim - acquWFS-1
#echo "confstart acquWFS-1" >> /milk/shm/ao188_fpsCTRL.fifo
echo "runstart acquWFS-1" >> /milk/shm/ao188_fpsCTRL.fifo
sleep 5


echo -e "\n"
echo -e "\e[1;31mCACAO setup started (run process ON). \e[0m \n"
echo -e "\e[1;33mprocess running in:\e[0m \n"
echo -e "\e[1;33mSee tmux a -t ao188_fpsCTRL\e[0m \n"
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
# START/init tmux sessions
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




# -----------------------------------------
# Start CACAO in the tmux tm_cacao2 session 
#------------------------------------------


# kill cacao if still running in the session
tmux send-keys -t tm_cacao2 "^C" C-m
sleep 0.5
tmux send-keys -t tm_cacao2 "cd /home/rts/RTS_2019/conf/" C-m
sleep 0.5
tmux send-keys -t tm_cacao2 "cacao" C-m





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
tmux send-keys -t tm_fpdp_dm './fpdptest_LGS_DM' C-m
tmux send-keys -t tm_fpdp_dm 'DM_ON' C-m
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

tmux send-keys -t tm_cacao '\x03' C-m

sleep 2

#-----------------------------------------------------------
# START Loop process !
#-----------------------------------------------------------

# LoopRun-1

#echo "confstart loopRUN-1" >> /milk/shm/ao188_fpsCTRL.fifo
echo "runstart loopRUN-1" >> /milk/shm/ao188_fpsCTRL.fifo
sleep 5





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




#-----------------------------------------------------------
# Start the gen2 interface: new  10/2019
#-----------------------------------------------------------

echo -e "\e[1;32mStart gen2 interface... \e[0m\n"

tmux new-session -d -s tm_ao188
tmux send-keys -t tm_ao188 'g2if_restart' C-m
tmux detach -s tm_ao188
sleep 3

echo -e "\e[1;31mDM communication started ... \e[0m\n"



echo -e "\n"
echo -e "\n"
echo -e "\e[1;34mRTS interface scripts started ! \e[0m\n"
