#!/usr/bin/env python
'''
Covers for the following equivalent bash:
Allows toggling between real DAC40 control (FPDP channel 0)
And loopback FPDP DAC40 (send ch2, receive ch3)

tmux new -d -s fpdp_dm
tmux send-keys -t fpdp_dm "hwint-dac40 -s bim188_float -u 0" Enter
PID=$(pgrep hwint-dac40)
milk-exec "csetandprioext $PID dm188_drv 45"

Usage:
    bim188-hwint (lo|hw)
'''

from docopt import docopt
import subprocess
import time

from swmain.infra import tmux

if __name__ == "__main__":
    args = docopt(__doc__)

    HW = args['hw']
    if HW:
        UNIT = 0
    else:
        UNIT = 2

    pane = tmux.find_or_create('fpdp_dm')
    tmux.kill_running(pane)

    pane.send_keys(f'hwint-dac40 -s bim188_float -u {UNIT}')

    time.sleep(0.5)
    pid = tmux.find_pane_running_pid(pane)
    subprocess.run(['milk-exec', f'"csetandprioext {pid} dm188_drv 45"'])

    pane_recv = tmux.find_or_create('fpdp_recv')
    tmux.kill_running(pane_recv)

    if not HW:
        pane_recv.send_keys('hwacq-fpdptake -D -s bim188_loopback -u 3 -l 0')
        time.sleep(0.5)
        pid = tmux.find_pane_running_pid(pane_recv)
        subprocess.run(['milk-exec', f'"csetandprioext {pid} fpdp_recv 45"'])
