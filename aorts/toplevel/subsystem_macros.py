from __future__ import annotations

import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux

from . import common as common
from .. import config

from swmain.network.pyroclient import connect_aorts
from scxconf import pyrokeys

OK = common.MacroRetcode.SUCCESS
ERR = common.MacroRetcode.FAILURE


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


def iiwi_startup() -> common.T_RetCodeMessage:
    '''
    This shouldn't happen much either.
    '''
    from camstack.cam_mains.main import main
    main(cam_name_arg='IIWI')  # TODO this can change
    time.sleep(1)
    tmux_iiwi = tmux.find('iiwi_ctrl')  # Hope it's not None
    if tmux_iiwi is None:
        return (ERR, "Iiwi startup failure (no tmux)")

    # Wait for the pyro proxy to go live
    now = time.time()
    while time.time() - now < 20.0:
        if tmux.find_pane_running_pid(tmux_iiwi) is None:
            return (ERR, "Iiwi startup failure (iiwi_ctrl crash).")
        try:
            iiwi_proxy = connect_aorts(pyrokeys.IIWI)
            iiwi_proxy.poll_camera_for_keywords()
            return (OK, "Iiwi started successfully.")
        except:
            pass

    return (ERR, "Iiwi startup failure (no pyro proxy after 20 seconds).")


def iiwi_teardown() -> common.T_RetCodeMessage:
    '''
    This really should not be needed at all.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('iiwi_ctrl')
    tmux.send_keys(tmux_apd, 'release(); quit()')

    if not (tmux.expect_no_pid(tmux_apd, timeout_sec=10)):
        return (ERR, "APD acquisition halt error. Inspect tmux apd_ctrl.")

    return (OK, "Iiwi acquisition halted successfully.")


def apd_startup() -> common.T_RetCodeMessage:
    from camstack.cam_mains.main import main
    main(cam_name_arg='APD')
    time.sleep(1)
    tmux_apd = tmux.find('apd_ctrl')  # Hope it's not None
    if tmux_apd is None:
        return (ERR, "APD acq startup failure (no tmux)")

    # Wait for the pyro proxy to go live
    now = time.time()
    while time.time() - now < 20.0:
        if tmux.find_pane_running_pid(tmux_apd) is None:
            return (ERR, "APD startup failure (apd_ctrl crash).")
        try:
            iiwi_proxy = connect_aorts(pyrokeys.APD)
            iiwi_proxy.poll_camera_for_keywords()
            return (OK, "APD acq. started successfully.")
        except:
            pass

    return (ERR, "APD startup failure (no pyro proxy after 20 seconds).")


def apd_teardown() -> common.T_RetCodeMessage:
    '''
    Should only be needed when switching to passthrough.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('apd_ctrl')
    tmux.send_keys(tmux_apd, 'release(); quit()')

    if not tmux.expect_no_pid(tmux_apd, timeout_sec=10):
        return (ERR, "APD acquisition halt error. Inspect tmux apd_ctrl.")

    return (OK, "APD acquisition halted successfully.")


def pt_apd_startup() -> common.T_RetCodeMessage:
    '''
    Starter for passthrough (no conversion) mode.
    '''
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux.kill_running(tmux_apd)
    tmux_apd.send_keys('hwint-fpdp-pt -s apd_raw -u 0 -t 2 -B 464')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_apd) is None:
        return (ERR,
                "APD passthrough relay did not start. Inspect tmux pt_apd.")

    return (OK, "FPDP passthrough startup complete.")


def pt_dac_startup() -> common.T_RetCodeMessage:
    tmux_dac = tmux.find_or_create('pt_dac')
    tmux.kill_running(tmux_dac)
    tmux_dac.send_keys('hwint-fpdp-pt -s dac40_raw -u 3 -t 1 -B xxx')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_dac) is None:
        return (ERR,
                "DAC40 passthrough relay did not start. Inspect tmux pt_dac.")

    return (OK, "FPDP passthrough startup complete.")


def pt_apd_teardown() -> common.T_RetCodeMessage:
    '''
    Teardown for passthrough (no conversion) mode.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux.kill_running(tmux_apd)

    if not tmux.expect_no_pid(tmux_apd, timeout_sec=3):
        return (ERR, "FPDP APD passthrough halt error. Inspect tmux pt_apd")

    return (OK, "FPDP DAC passthrough halted successfully.")


def pt_dac_teardown() -> common.T_RetCodeMessage:
    tmux_dac = tmux.find_or_create('pt_dac')
    tmux.kill_running(tmux_dac)

    if not tmux.expect_no_pid(tmux_dac, timeout_sec=3):
        return (ERR, "FPDP DAC passthrough halt error. Inspect tmux pt_dac")

    return (OK, "FPDP DAC passthrough halted successfully.")


def dac40_startup() -> common.T_RetCodeMessage:
    tmux_sesh = tmux.find_or_create('fpdp_dm')
    tmux_sesh.send_keys('hwint-dac40 -s bim188_float -u 1')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_sesh) is None:
        return (ERR, "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    shm_dmsend = SHM(f'dm{config.DMNUM_BIM188}disp')
    shm_dmtele = SHM(config.SHMNAME_BIM188)
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros(188, np.float32))
    shm_dmtele.get_data(True, timeout=0.1)
    if shm_dmtele.get_counter() <= ctr_tele:
        return (ERR, "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    return (OK, "DAC40 FPDP startup complete.")


def dac40_teardown() -> common.T_RetCodeMessage:
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
        return (ERR,
                "DAC40 halt error during DM/TTs zeroing. Inspect tmux fpdp_dm.")

    # Teardown the tmux
    tmux_sesh = tmux.find_or_create('fpdp_dm')
    tmux.kill_running(tmux_sesh)

    if tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
        return (OK, "DAC40 halted successfully.")

    return (ERR, "DAC40 halt error. Inspect tmux fpdp_dm.")


def dm3k_startup():
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux_sesh.send_keys('hwint-alpao -L')

    time.sleep(1)

    if tmux.find_pane_running_pid(tmux_sesh) is None:
        return (ERR, "DM3k driver did not start. Inspect tmux dm64_drv.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    shm_dmsend = SHM(f'dm{config.DMNUM_ALPAO}disp')
    shm_dmtele = SHM(config.SHMNAME_ALPAO)
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros((64, 64), np.float32))
    shm_dmtele.get_data(True, timeout=0.1)
    if shm_dmtele.get_counter() <= ctr_tele:
        return (ERR, "DM3k driver did not start. Inspect tmux dm64_drv.")

    return (OK, "DM3k driver startup complete.")


def dm3k_teardown():
    # DM zero --all
    from ..control.dm3k import DM3kManager

    DM3kManager().zero(zero_all=True)  # Eh.

    # Teardown the tmux
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux.kill_running(tmux_sesh)

    if not tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
        return (ERR, "DM3k halt error. Inspect tmux dm64_drv.")

    tmux_sesh.send_keys('hwint_alpao -R')  # Fire a reset to the HSDL links.
    return (OK,
            "DM3k driver halted successfully. Does NOT comprise a HKL poweroff."
            )
