from __future__ import annotations
import typing as typ

import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux
from swmain.infra.rttools import milk_make_rt

from . import base_module_modes as base

RME: typ.TypeAlias = base.RTS_MODULE_ENUM  # Alias
from .. import config

from ..cacao_stuff.loop_manager import CacaoLoopManager

from swmain.network.pyroclient import connect_aorts
from scxconf import pyrokeys

OK = base.OkErrEnum.OK
ERR = base.OkErrEnum.ERR


class Iiwi_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.IIWI

    @classmethod
    def start_function(cls) -> base.T_Result:
        '''
        This shouldn't happen much either.
        '''
        from camstack.cam_mains.main import main
        main(cam_name_arg='IIWI')  # TODO this can change
        time.sleep(1)
        tmux_iiwi = tmux.find_or_create('iiwi_ctrl')  # Hope it's not None

        # Wait for the pyro proxy to go live
        now = time.time()
        while time.time() - now < 20.0:
            time.sleep(0.1)
            if tmux.find_pane_running_pid(tmux_iiwi) is None:
                return (ERR, "Iiwi startup failure (iiwi_ctrl crash).")
            try:
                iiwi_proxy = connect_aorts(pyrokeys.IIWI)
                iiwi_proxy.poll_camera_for_keywords()
                return (OK, "Iiwi started successfully.")
            except:
                pass

        return (ERR, "Iiwi startup failure (no pyro proxy after 20 seconds).")

    @classmethod
    def stop_function(cls) -> base.T_Result:
        '''
        This really should not be needed at all.
        '''
        # Teardown the tmux
        tmux_iiwi = tmux.find('iiwi_ctrl')
        if tmux_iiwi is None:
            return (ERR, "Iiwi startup failure (no tmux)")
        tmux.send_keys(tmux_iiwi, 'release(); quit()')

        if not (tmux.expect_no_pid(tmux_iiwi, timeout_sec=15)):
            return (ERR, "IIWI acquisition halt error. Inspect tmux apd_ctrl.")

        return (OK, "Iiwi acquisition halted successfully.")


class DAC40_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.DAC40

    @classmethod
    def start_function(cls) -> base.T_Result:

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

    @classmethod
    def stop_function(cls) -> base.T_Result:
        # DM zero --all

        from ..control.dm import BIM188Manager, TTManager, WTTManager

        try:
            BIM188Manager().zero(do_ch_zero=True, do_other_channels=True)
        except:
            # Expected failure in DM3K mode with no DMComb for dm 00.
            pass

        TTManager().zero(do_ch_zero=True, do_other_channels=True)
        WTTManager().zero()

        if not (np.all(
                SHM(config.SHMNAME_BIM188).get_data(True, timeout=0.1) == 0.0
        ) and np.all(SHM(config.SHMNAME_TT).get_data(True, timeout=0.1) == 0.0)
                and np.all(
                        SHM(config.SHMNAME_WTT).get_data(True, timeout=0.1) ==
                        0.0)):
            return (ERR,
                    "DAC40 halt error during DM/TTs zeroing. Inspect tmux fpdp_dm."
                    )

        # Teardown the tmux
        tmux_sesh = tmux.find_or_create('fpdp_dm')
        tmux.kill_running(tmux_sesh)

        if tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
            return (OK, "DAC40 halted successfully.")

        return (ERR, "DAC40 halt error. Inspect tmux fpdp_dm.")


class APD_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.APD

    @classmethod
    def start_function(cls) -> base.T_Result:
        from camstack.cam_mains.main import main
        main(cam_name_arg='APD')
        time.sleep(1)
        tmux_apd = tmux.find('apd_ctrl')  # Hope it's not None
        if tmux_apd is None:
            return (ERR, "APD acq startup failure (no tmux)")

        # Wait for the pyro proxy to go live
        now = time.time()
        while time.time() - now < 20.0:
            time.sleep(0.1)
            if tmux.find_pane_running_pid(tmux_apd) is None:
                return (ERR, "APD startup failure (apd_ctrl crash).")
            try:
                apd_proxy = connect_aorts(pyrokeys.APD)
                apd_proxy.poll_camera_for_keywords()
                return (OK, "APD acq. started successfully.")
            except:
                pass

        return (ERR, "APD startup failure (no pyro proxy after 20 seconds).")

    @classmethod
    def stop_function(cls) -> base.T_Result:
        '''
        Should only be needed when switching to passthrough.
        '''
        # Teardown the tmux
        tmux_apd = tmux.find_or_create('apd_ctrl')
        tmux.send_keys(tmux_apd, 'release(); quit()')

        if not tmux.expect_no_pid(tmux_apd, timeout_sec=10):
            return (ERR, "APD acquisition halt error. Inspect tmux apd_ctrl.")

        return (OK, "APD acquisition halted successfully.")


class KWFS_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.KWFS

    @classmethod
    def start_function(cls) -> base.T_Result:
        from camstack.cam_mains.main import main
        main(cam_name_arg='ALALA')  # Makes no sense but that's what we got...
        time.sleep(1)
        tmux_kwfs = tmux.find('alala_ctrl')  # Hope it's not None
        if tmux_kwfs is None:
            return (ERR, "KWFS acq startup failure (no tmux)")

        # Wait for the pyro proxy to go live
        now = time.time()
        while time.time() - now < 20.0:
            time.sleep(0.1)
            if tmux.find_pane_running_pid(tmux_kwfs) is None:
                return (ERR, "KWFS startup failure (alala_ctrl crash).")
            try:
                iiwi_proxy = connect_aorts(pyrokeys.ALALA)
                iiwi_proxy.poll_camera_for_keywords()
                return (OK, "KWFS acq. started successfully.")
            except:
                pass

        return (ERR, "KWFS startup failure (no pyro proxy after 20 seconds).")

    @classmethod
    def stop_function(cls) -> base.T_Result:
        '''
        Should only be needed when switching to passthrough.
        '''
        # Teardown the tmux
        tmux_kwfs = tmux.find_or_create('kwfs_ctrl')
        tmux.send_keys(tmux_kwfs, 'release(); quit()')

        if not tmux.expect_no_pid(tmux_kwfs, timeout_sec=10):
            return (ERR, "KWFS acquisition halt error. Inspect tmux kwfs_ctrl.")

        return (OK, "KWFS acquisition halted successfully.")


class PTDAC_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.PT_DAC

    @classmethod
    def start_function(cls) -> base.T_Result:
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
            tmux_dac.send_keys(
                    'hwint-fpdprelay -s dac40_raw -u 3 -t 1 -B 420 -T')

        time.sleep(1)

        pid = tmux.find_pane_running_pid(tmux_dac)
        if pid is None:
            return (ERR,
                    "DAC40 passthrough relay did not start. Inspect tmux pt_dac."
                    )

        loop9.acquWFS.run_start()
        loop9.mvalC2dm.run_start()

        milk_make_rt('dm188_drv', pid, 40)

        return (OK, "FPDP passthrough startup complete.")

    @classmethod
    def stop_function(cls) -> base.T_Result:
        tmux_dac = tmux.find_or_create('pt_dac')
        tmux.kill_running(tmux_dac)

        if not tmux.expect_no_pid(tmux_dac, timeout_sec=3):
            return (ERR, "FPDP DAC passthrough halt error. Inspect tmux pt_dac")

        return (OK, "FPDP DAC passthrough halted successfully.")


class DM3K_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.DM3K

    @classmethod
    def start_function(cls) -> base.T_Result:
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

    @classmethod
    def stop_function(cls) -> base.T_Result:
        # DM zero --all
        from ..control.dm import DM3kManager

        DM3kManager().zero()  # Eh.

        # Teardown the tmux
        tmux_sesh = tmux.find_or_create('dm64_drv')
        tmux.kill_running(tmux_sesh)

        if not tmux.expect_no_pid(tmux_sesh, timeout_sec=3):
            return (ERR, "DM3k halt error. Inspect tmux dm64_drv.")

        tmux_sesh.send_keys(
                'hwint-alpao64 -R')  # Fire a reset to the HSDL links.
        return (OK,
                "DM3k driver halted successfully. Does NOT comprise a HKL poweroff."
                # But actually it should.
                )
