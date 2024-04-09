from __future__ import annotations

import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux

from . import common as cm
from .. import config


def general_startup():
    '''
        Cover what's in rts_start.sh

        But be smarter about it.

        FPDP_reset: yes

        APD acq: not in PT mode

        cacao-loop-deploys: yes

        Iiwi acq: yes

        Miscellany SHMs for legacy g2if: yes
        g2if: yes but it needs smarts.
    '''


def iiwi_startup() -> cm.T_RetCodeMessage:
    pass


def iiwi_teardown() -> cm.T_RetCodeMessage:
    pass


def apd_startup() -> cm.T_RetCodeMessage:
    pass


def apd_teardown() -> cm.T_RetCodeMessage:
    pass


def pt_startup() -> cm.T_RetCodeMessage:
    '''
    Starter for passthrough (no conversion) mode.
    '''
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux_apd.send_keys('hwint-fpdp-pt -s 0 -t 2 -B 464')

    tmux_dac = tmux.find_or_create('pt_dac')
    tmux_dac.send_keys('hwint-fpdp-pt -s 3 -t 1 -B XXX')

    time.sleep(1)
    if tmux.find_pane_running_pid(tmux_apd) is None:
        return (cm.MacroRetcode.FAILURE,
                "APD passthrough relay did not start. Inspect tmux pt_apd.")
    if tmux.find_pane_running_pid(tmux_dac) is None:
        return (cm.MacroRetcode.FAILURE,
                "DAC40 passthrough relay did not start. Inspect tmux pt_dac.")

    return (cm.MacroRetcode.SUCCESS, "FPDP passthrough startup complete.")


def pt_teardown() -> cm.T_RetCodeMessage:
    '''
    Teardown for passthrough (no conversion) mode.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux.kill_running(tmux_apd)
    tmux_dac = tmux.find_or_create('pt_dac')
    tmux.kill_running(tmux_dac)

    if not (tmux.expect_no_pid(tmux_apd, timeout_sec=3) and
            tmux.expect_no_pid(tmux_dac, timeout_sec=3)):
        return (cm.MacroRetcode.FAILURE,
                "FPDP passthrough halt error. Inspect tmux pt_apd and/or pt_dac"
                )

    return (cm.MacroRetcode.SUCCESS, "FPDP passthrough halted successfully.")


def dac40_startup() -> cm.T_RetCodeMessage:
    tmux_sesh = tmux.find_or_create('fpdp_dm')
    tmux_sesh.send_keys('hwint-dac40 -s bim188_float -u 1')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_sesh) is None:
        return (cm.MacroRetcode.FAILURE,
                "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    shm_dmsend = SHM(f'dm{config.DMNUM_BIM188}disp')
    shm_dmtele = SHM(config.SHMNAME_BIM188)
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros(188, np.float32))
    shm_dmtele.get_data(True, timeout=0.1)
    if shm_dmtele.get_counter() <= ctr_tele:
        return (cm.MacroRetcode.FAILURE,
                "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    return (cm.MacroRetcode.SUCCESS, "DAC40 FPDP startup complete.")


def dac40_teardown() -> cm.T_RetCodeMessage:
    # DM zero --all
    from ..control.bim188 import Bim188Manager
    from ..control.tt import TipTiltManager
    from ..control.wtt import WTTManager

    Bim188Manager().zero(zero_all=True)
    TipTiltManager().zero(zero_all=True)
    WTTManager().zero()

    if not (np.all(
            SHM(config.SHMNAME_BIM188).get_data(True, timeout=0.1) == 0.0) and
            np.all(SHM(config.SHMNAME_TT).get_data(True, timeout=0.1) == 0.0)
            and
            np.all(SHM(config.SHMNAME_WTT).get_data(True, timeout=0.1) == 0.0)):
        (cm.MacroRetcode.FAILURE,
         "DAC40 halt error during DM/TTs zeroing. Inspect tmux fpdp_dm.")

    # Teardown the tmux
    tmux_sesh = tmux.find_or_create('fpdp_dm')
    tmux.kill_running(tmux_sesh)

    if tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
        return (cm.MacroRetcode.SUCCESS, "DAC40 halted successfully.")

    return (cm.MacroRetcode.FAILURE, "DAC40 halt error. Inspect tmux fpdp_dm.")


def dm3k_startup():
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux_sesh.send_keys('hwint-alpao -L')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_sesh) is None:
        return (cm.MacroRetcode.FAILURE,
                "DM3k driver did not start. Inspect tmux dm64_drv.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    shm_dmsend = SHM(f'dm{config.DMNUM_ALPAO}disp')
    shm_dmtele = SHM(config.SHMNAME_ALPAO)
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros((64, 64), np.float32))
    shm_dmtele.get_data(True, timeout=0.1)
    if shm_dmtele.get_counter() <= ctr_tele:
        return (cm.MacroRetcode.FAILURE,
                "DM3k driver did not start. Inspect tmux dm64_drv.")

    return (cm.MacroRetcode.SUCCESS, "DM3k driver startup complete.")


def dm3k_teardown():
    # DM zero --all
    from ..control.dm3k import DM3kManager

    DM3kManager().zero(zero_all=True)  # Eh.

    # Teardown the tmux
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux.kill_running(tmux_sesh)

    if not tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
        return (cm.MacroRetcode.FAILURE,
                "DM3k halt error. Inspect tmux dm64_drv.")

    tmux_sesh.send_keys('hwint_alpao -R')  # Fire a reset to the HSDL links.
    return (cm.MacroRetcode.SUCCESS,
            "DM3k driver halted successfully. Does NOT comprise a HKL poweroff."
            )
