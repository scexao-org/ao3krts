#!/bin/bash
#take two values dmTT flat ttx; tty
#send it as new dmTT flat value


#actual value
#tmux send-keys -t tm_chris "cacao" C-m
#tmux send-keys -t tm_chris "readshmim dmTT" C-m
#tmux send-keys -t tm_chris "saveflfits dmTT /home/rts/Chris/dmTT_flat_temp.fits" C-m

read -p "Enter dm flat ttx: " ttx
read -p "Enter dm flat tty: " tty

if [ "$ttx" -gt "8191" ] || [ "$ttx" -lt "-8192" ]
then 
    echo "ttx values must be between -8191 (-9.9V) and +8192 (+9.9V) )"  
    exit
fi
 
if [ "$tty" -gt "8191" ] || [ "$tty" -lt "-8192" ]
then 
    echo "tty values must be between -8191 (-9.9V) and +8192 (+9.9V) )"
    exit
fi

echo "You want to change the dmTT flat value as: dmTT ( $ttx ; $tty )"
read -p " Is that right ? ( y / n)" answ



if [ "$answ" = "y" ]
then
    echo "your answer is Yes: the dm TT flat will be updated"

    tmux send-keys -t tm_cacao "cacao" C-m
    tmux send-keys -t tm_cacao "readshmim dmTT" C-m
    tmux send-keys -t tm_cacao "setpix dmTT $ttx 0 0" C-m
    tmux send-keys -t tm_cacao "setpix dmTT $tty 1 0" C-m

    tmux send-keys -t tm_cacao 'readshmim dmvoltf' C-m
    tmux send-keys -t tm_cacao 'imsetsempost dmvoltf -1' C-m

    tmux send-keys -t tm_cacao "exitCLI" C-m



else
    echo "your answer is No: dm TT flat not updated"
fi
