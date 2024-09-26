from __future__ import annotations

import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux
from swmain.infra.rttools import milk_make_rt

from . import common as cmn
from .. import config

from ..cacao_stuff.loop_manager import CacaoLoopManager

from swmain.network.pyroclient import connect_aorts
from scxconf import pyrokeys

OK = cmn.MacroRetcode.SUCCESS
ERR = cmn.MacroRetcode.FAILURE


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


@cmn.RTS_MODULE.IIWI.register_startup_function
def iiwi_startup() -> cmn.T_RetCodeMessage:
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


@cmn.RTS_MODULE.IIWI.register_stop_function
def iiwi_teardown() -> cmn.T_RetCodeMessage:
    '''
    This really should not be needed at all.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('iiwi_ctrl')
    tmux.send_keys(tmux_apd, 'release(); quit()')

    if not (tmux.expect_no_pid(tmux_apd, timeout_sec=15)):
        return (ERR, "IIWI acquisition halt error. Inspect tmux apd_ctrl.")

    return (OK, "Iiwi acquisition halted successfully.")


@cmn.RTS_MODULE.APD.register_startup_function
def apd_startup() -> cmn.T_RetCodeMessage:
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


@cmn.RTS_MODULE.APD.register_stop_function
def apd_teardown() -> cmn.T_RetCodeMessage:
    '''
    Should only be needed when switching to passthrough.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('apd_ctrl')
    tmux.send_keys(tmux_apd, 'release(); quit()')

    if not tmux.expect_no_pid(tmux_apd, timeout_sec=10):
        return (ERR, "APD acquisition halt error. Inspect tmux apd_ctrl.")

    return (OK, "APD acquisition halted successfully.")


@cmn.RTS_MODULE.PT_APD.register_startup_function
def pt_apd_startup() -> cmn.T_RetCodeMessage:
    '''
    Starter for passthrough (no conversion) mode.
    '''
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux.kill_running(tmux_apd)
    tmux_apd.send_keys('hwint-fpdprelay -s apd_raw -u 0 -t 2 -B 464')

    time.sleep(1)

    pid = tmux.find_pane_running_pid(tmux_apd)
    if pid is None:
        return (ERR,
                "APD passthrough relay did not start. Inspect tmux pt_apd.")

    milk_make_rt('fpdp_recv', pid, 45)

    return (OK, "FPDP passthrough startup complete.")


@cmn.RTS_MODULE.PT_DAC.register_startup_function
def pt_dac_startup() -> cmn.T_RetCodeMessage:

    loop9 = CacaoLoopManager(*config.LINFO_BIM3KTRANSLATION)
    loop9.mvalC2dm.run_stop()
    loop9.acquWFS.run_stop()

    tmux_dac = tmux.find_or_create('pt_dac')
    tmux.kill_running(tmux_dac)

    try:
        dac_raw_shm = SHM('dac40_raw')
        tmux_dac.send_keys(
                'hwint-fpdprelay -s dac40_raw -u 3 -t 1 -B 420 -T -R')
    except FileNotFoundError:
        # Create SHM
        tmux_dac.send_keys('hwint-fpdprelay -s dac40_raw -u 3 -t 1 -B 420 -T')

    time.sleep(1)

    pid = tmux.find_pane_running_pid(tmux_dac)
    if pid is None:
        return (ERR,
                "DAC40 passthrough relay did not start. Inspect tmux pt_dac.")

    loop9.acquWFS.run_start()
    loop9.mvalC2dm.run_start()

    milk_make_rt('dm188_drv', pid, 40)

    return (OK, "FPDP passthrough startup complete.")


@cmn.RTS_MODULE.PT_APD.register_stop_function
def pt_apd_teardown() -> cmn.T_RetCodeMessage:
    '''
    Teardown for passthrough (no conversion) mode.
    '''
    # Teardown the tmux
    tmux_apd = tmux.find_or_create('pt_apd')
    tmux.kill_running(tmux_apd)

    if not tmux.expect_no_pid(tmux_apd, timeout_sec=3):
        return (ERR, "FPDP APD passthrough halt error. Inspect tmux pt_apd")

    return (OK, "FPDP DAC passthrough halted successfully.")


@cmn.RTS_MODULE.PT_DAC.register_stop_function
def pt_dac_teardown() -> cmn.T_RetCodeMessage:
    tmux_dac = tmux.find_or_create('pt_dac')
    tmux.kill_running(tmux_dac)

    if not tmux.expect_no_pid(tmux_dac, timeout_sec=3):
        return (ERR, "FPDP DAC passthrough halt error. Inspect tmux pt_dac")

    return (OK, "FPDP DAC passthrough halted successfully.")


@cmn.RTS_MODULE.DAC40.register_startup_function
def dac40_startup() -> cmn.T_RetCodeMessage:

    # If in DM3K mode, this SHM may not exist
    # And we still need it for hwint-dac40 to start.
    try:
        dm00disp = SHM('dm00disp')
    except FileNotFoundError:
        dm00disp = SHM('dm00disp', np.zeros((188, 1), np.float32))

    tmux_sesh = tmux.find_or_create('fpdp_dm')
    tmux_sesh.send_keys('hwint-dac40 -s bim188_float -u 1')

    time.sleep(1)

    pid = tmux.find_pane_running_pid(tmux_sesh)
    if pid is None:
        return (ERR, "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    try:
        shm_dmsend = SHM(f'dm{config.DMNUM_BIM188}disp')
        shm_dmsend.set_data(np.zeros(188, np.float32))
    except FileNotFoundError:
        shm_dmsend = SHM(f'dm{config.DMNUM_BIM188}disp',
                         np.zeros(188, np.float32))

    shm_dmtele = SHM(config.SHMNAME_BIM188)
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros(188, np.float32))

    shm_dmtele.get_data(True, timeout=0.5)

    if shm_dmtele.get_counter() <= ctr_tele:
        return (ERR, "DAC40 FPDP did not start. Inspect tmux fpdp_dm.")

    milk_make_rt('dm188_drv', pid, 40)

    return (OK, "DAC40 FPDP startup complete.")


@cmn.RTS_MODULE.DAC40.register_stop_function
def dac40_teardown() -> cmn.T_RetCodeMessage:
    # DM zero --all

    from ..control.dm import BIM188Manager, TTManager, WTTManager

    # BIM188Manager().zero(do_ch_zero=True, do_other_channels=True)
    TTManager().zero(do_ch_zero=True, do_other_channels=True)
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


@cmn.RTS_MODULE.DM3K.register_startup_function
def dm3k_startup():
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux_sesh.send_keys('hwint-alpao64 -L')

    shm_dmtele = SHM(config.SHMNAME_ALPAO, np.zeros((64, 64), np.float32))

    time.sleep(1)

    pid = tmux.find_pane_running_pid(tmux_sesh)
    if pid is None:
        return (ERR, "DM3k driver did not start. Inspect tmux dm64_drv.")

    # Try to send data to dmXXdispXX and get return in bim188tele
    # TODO: just call dmzero from the control subpackage?
    shm_dmsend = SHM(f'dm{config.DMNUM_ALPAO}disp')
    ctr_tele = shm_dmtele.get_counter()

    shm_dmsend.set_data(np.zeros((64, 64), np.float32))
    shm_dmtele.get_data(True, timeout=0.1)
    if shm_dmtele.get_counter() <= ctr_tele:
        return (ERR, "DM3k driver did not start. Inspect tmux dm64_drv.")

    milk_make_rt('dm188_drv', pid, 40)

    return (OK, "DM3k driver startup complete.")


@cmn.RTS_MODULE.DM3K.register_stop_function
def dm3k_teardown():
    # DM zero --all
    from ..control.dm import DM3kManager

    DM3kManager().zero()  # Eh.

    # Teardown the tmux
    tmux_sesh = tmux.find_or_create('dm64_drv')
    tmux.kill_running(tmux_sesh)

    if not tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
        return (ERR, "DM3k halt error. Inspect tmux dm64_drv.")

    tmux_sesh.send_keys('hwint-alpao64 -R')  # Fire a reset to the HSDL links.
    return (OK,
            "DM3k driver halted successfully. Does NOT comprise a HKL poweroff."
            )
