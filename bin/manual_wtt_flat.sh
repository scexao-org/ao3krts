#!/bin/bash
#take two values dmTT flat ttx; tty
#send it as new dmTT flat value


#actual value
#tmux send-keys -t tm_chris "cacao" C-m
#tmux send-keys -t tm_chris "readshmim dmTT" C-m
#tmux send-keys -t tm_chris "saveflfits dmTT /home/rts/Chris/dmTT_flat_temp.fits" C-m

read -p "Enter dm flat wttx: " wttx
read -p "Enter dm flat wtty: " wtty

if [ "$wttx" -gt "8191" ] || [ "$wttx" -lt "0" ]
then 
    echo "wttx values must be between 0 (0V) and +8192 (+9.9V) )"  
    exit
fi
 
if [ "$wtty" -gt "8192" ] || [ "$wtty" -lt "0" ]
then 
    echo "wtty values must be between 0 (0V) and +8192 (+9.9V) )"
    exit
fi

echo "You want to change the WTT flat value as: WTT ( $wttx ; $wtty )"
read -p " Is that right ? ( y / n)" answ



if [ "$answ" = "y" ]
then
    echo "your answer is Yes: the WTT flat will be updated"

    tmux send-keys -t tm_cacao "cacao" C-m
    tmux send-keys -t tm_cacao "readshmim wtt" C-m
    tmux send-keys -t tm_cacao "setpix wtt $wttx 0 0" C-m
    tmux send-keys -t tm_cacao "setpix wtt $wtty 1 0" C-m

    tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m
    tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m

    tmux send-keys -t tm_cacao "exitCLI" C-m



else
    echo "your answer is No: WTT flat not updated"
fi
