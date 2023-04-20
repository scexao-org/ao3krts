#!/bin/bash

###################################################
# Ch. Clergeon 2020/06/20
# startup script for AO188 interface communication
# NEW CACAO VERSION
# HARDWARE
###################################################


# ------------------------
# CACAO startup
# ------------------------

# ------------------------
# init fpdp boards
# ------------------------

echo -e "\n"
echo -e "\e[1;32mReset fpdp boads connections\e[0m \n"
echo -e "\n"

${RTS_PACK_ROOT}/bin/ctr_init
sleep 1.0
${RTS_PACK_ROOT}/bin/ctr_init
sleep 1.0

# ------------------------
# START/init tmux sessions
# ------------------------

echo -e "\n"
echo -e "\e[1;32mInitialize tmux sessions...\e[0m \n"
echo -e "\n"

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

# ------------------------------------------------------------------
# Start CACAO process WFS acquisition (requires SHM from APD script)
# ------------------------------------------------------------------

# --------------------------------------------------
# Start the DM communication - STEP 1: DM main (NGS)
# --------------------------------------------------

echo -e "\e[1;32mStart DM communication... \e[0m\n"

# Assert DMch2disp-00 is running!! And that it has created dm00disp.
ln -sf /milk/shm/dm00disp.im.shm /milk/shm/bim188_float.im.shm
# Assert DMch2disp-01 (TToffload loop) is running!! And that it has created dm00disp.
ln -sf /milk/shm/dm01disp.im.shm /milk/shm/tt_value_float.im.shm
creashmim wtt_value_float 1 2 -z --type=f32

creashmim bim188_telemetry 1 188 -z --type=f32
creashmim tt_telemetry 1 2 -z --type=f32
creashmim wtt_telemetry 1 2 -z --type=f32

tmux send-keys -t fpdp_dm "hwint-dac40 -s bim188_float -u 0" Enter

echo -e "\e[1;31mDM communication available on SHMs "bim188_float" "tt_value_float" "wtt_value_float"  ... \e[0m\n"

sleep 3
#--------------------------------------------
# Load configuration files in shared memories
#--------------------------------------------

#----------------------------
# Load dmTT flat and wtt flat
#----------------------------

echo -e "\e[1;32mload dmTT amd wTT flats...\e[0m\n"
${RTS_PACK_ROOT}/bin/tt_flat.py
sleep 3
${RTS_PACK_ROOT}/bin/wtt_flat.py
sleep 3

#----------------------------------------------------
# Start the DM communication - STEP 2: DM LOGIC (LGS)
#----------------------------------------------------

#-----------------
# zero DM channels
#-----------------

echo -e "\e[1;32mZero DM phys channels...\e[0m\n"
${RTS_PACK_ROOT}/bin/dm_zero.py
sleep 1


#--------------------------------
# Load default NGS control matrix
#--------------------------------

# Set default Httg and Hdfg to 1 (NGS)

#-----------------------------------------------------------
# START Loop process !
#-----------------------------------------------------------


#####################################################################
#
#### ---- SECURITY FOR OPERATORS --- CHECK if conf is loaded properly

#####################################################################

#-----------------------------------------------------------
# Start the DM communication - FINAL STEP: start DM writting
#-----------------------------------------------------------

#-----------------------------------------------------------
# Start the gen2 interface: new  10/2019
#-----------------------------------------------------------

echo -e "\e[1;32mStart gen2 interface... \e[0m\n"

tmux new-session -d -s tm_ao188
tmux send-keys -t tm_ao188 "g2if_restart" Enter
sleep 3

echo -e "\e[1;31mDM communication started ... \e[0m\n"

echo -e "\n"
echo -e "\n"
echo -e "\e[1;34mRTS interface scripts started ! \e[0m\n"

