#!/bin/bash

###################################################
# Ch. Clergeon 2020/06/20
# startup script for AO188 interface communication
# NEW CACAO VERSION
# HARDWARE
###################################################


RED="\e[1;31m"
GREEN="\e[1;32m"
BLUE="\e[1;34m"
ECOL="\e[0m" # End terminal color


# ------------------------
# CACAO startup
# ------------------------

# ------------------------
# init fpdp boards
# ------------------------

echo -e "\n"
echo -e "${GREEN}Reset fpdp boads connections${ECOL} \n"
echo -e "\n"

${RTS_PACK_ROOT}/scripts/fpdp_reset.sh
sleep 1.0
${RTS_PACK_ROOT}/scripts/fpdp_reset.sh
sleep 1.0

# ------------------------
# START/init tmux sessions
# ------------------------

echo -e "\n"
echo -e "${GREEN}Initialize tmux sessions...${ECOL} \n"
echo -e "\n"

#tmux new-session -d -s tm_ao188

echo -e "\n"
echo -e "${BLUE}Done.  Here's a 'tmux ls':${ECOL} \n"
echo -e "\n"

tmux ls

echo ""
echo ""

# -----------------------------------------
# Spin up the CRED1. This assumes it's cold.
#------------------------------------------

echo -e "${GREEN}Starting IIWI acquisition... ${ECOL}\n"
cam-iiwistart
echo -e "${RED}Startup executed. Check apapane/iiwi SHM.${ECOL}\n"

echo -e "${GREEN}Starting APD acquisition... ${ECOL}\n"
python -m camstack.cams.ao_apd tmux -u 0

echo -e "${RED}Startup executed. Check apapane/iiwi SHM.${ECOL}\n"

echo -e "${GREEN}Starting APD acquisition... ${ECOL}\n"
python -m camstack.cams.ao_apd tmux -u 0

echo -e "${RED}Startup executed. Check apapane/iiwi SHM.${ECOL}\n"

echo -e "${GREEN}Starting APD acquisition... ${ECOL}\n"
python -m camstack.cams.ao_apd tmux -u 0

echo -e "${RED}Startup executed. Check apapane/iiwi SHM.${ECOL}\n"

# -----------------------------------------
# Spin up the CACAO loop(s)
#------------------------------------------

echo -e "${GREEN}Reconfiguring CACAO loops... ${ECOL}\n"

echo -e "${RED}Done.${ECOL}\n"

(cd ${HOME}/AOloop;
rm -rf .apd188.cacaotaskmanager-log/;   # Loop 1
rm -rf .lowfs188.cacaotaskmanager-log/; # Loop 2
rm -rf .nir188.cacaotaskmanager-log/;   # Loop 3
rm -rf .ttoff188.cacaotaskmanager-log/; # Loop 4
cacao-loop-deploy ao3k-nirpyr188; # Loop 3 but also spins up DM00 / DM10
cacao-loop-deploy ao3k-ttoff188;  # Loop 4 and spins up DM01 / DM11
cacao-loop-deploy ao3k-apd188;    # Loop 1
cacao-loop-deploy ao3k-lowfs188;  # Loop 2
)

# -----------------------------------------
# Starting up the DMCombs
#------------------------------------------

# TODO Not sure of that???
(cd ${HOME}/AOloop/nir188-rootdir;
cacao-aorun-001-dmsim start;
cacao-aorun-000-dm start
)
(cd ${HOME}/AOloop/ttoff188-rootdir;
cacao-aorun-001-dmsim start;
cacao-aorun-000-dm start
)
sleep 3.0

# --------------------------------------------------
# Start the DM communication - STEP 1: DM main (NGS)
# --------------------------------------------------

echo -e "${GREEN}Start DM communication... ${ECOL}\n"

# Assert DMch2disp-00 is running!! And that it has created dm00disp.
ln -sf /milk/shm/dm00disp.im.shm /milk/shm/bim188_float.im.shm
# Assert DMch2disp-01 (TToffload loop) is running!! And that it has created dm00disp.
ln -sf /milk/shm/dm01disp.im.shm /milk/shm/tt_value_float.im.shm

# Non-loop input SHMs
creashmim ctt_value_float 1 2 -z --type=f32
creashmim wtt_value_float 1 2 -z --type=f32

# Output telemetry SHMs
creashmim bim188_tele 1 188 -z --type=f32
creashmim ctt_telemetry 1 2 -z --type=f32
creashmim tt_telemetry 1 2 -z --type=f32
creashmim wtt_telemetry 1 2 -z --type=f32

creashmim dmvolt 1 188 -z --type=u16 # This one is to make dm_displouf happy.

bim188-hwint lo # Start the loopback DAC40 interface

echo -e "${BLUE}DM communication available TO LOOPBACK FAKE DAC40"
echo -e "${BLUE}DM communication available on SHMs "bim188_float" "tt_value_float" "wtt_value_float" "ctt_value_float" ... ${ECOL}\n"

sleep 3

# ------------------------------------------------------------------
# Start CACAO process WFS acquisition (requires SHM from APD script)
# ------------------------------------------------------------------


#----------------------------
# Load dmTT flat and wtt flat
#----------------------------

echo -e "${GREEN}load dmTT amd wTT flats...${ECOL}\n"
${RTS_PACK_ROOT}/bin/tt_flat.py # Load fits to DMcomb channel 0.
sleep 3
${RTS_PACK_ROOT}/bin/wtt_flat.py
sleep 3

#----------------------------------------------------
# Start the DM communication - STEP 2: DM LOGIC (LGS)
#----------------------------------------------------

#-----------------
# zero DM channels
#-----------------

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

echo -e "${GREEN}Start gen2 interface... ${ECOL}\n"

echo -e "${RED}Warning creating dummy SHMS for HDF, LTT, ADF, APD, CURV... ${ECOL}\n"
creashmim Httg 1 1 -z --type=f32
creashmim Hdfg 1 1 -z --type=f32
creashmim LO_tt_gain 1 2 -z --type=f32
creashmim LO_defocus_gain 1 1 -z --type=f32
creashmim ADF_gain 1 1 -z --type=f32
creashmim ADFg 1 1 -z --type=f32
creashmim wttg 1 1 -z --type=f32
creashmim LO_tt 1 2 -z --type=f32
creashmim LO_defocus 1 1 -z --type=f32

# TODO
${HOME}/src/rts/g2if_server/g2if/scripts/g2if_restart
sleep 3.0

echo -e "${BLUE}DM communication started ... ${ECOL}\n"
echo -e "\n\n"
echo -e "${GREEN}RTS interface scripts started ! ${ECOL}\n"
