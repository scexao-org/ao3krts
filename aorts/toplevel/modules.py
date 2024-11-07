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

OK = base.MacroRetcode.OK
ERR = base.MacroRetcode.ERR


class Iiwi_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.IIWI

    @classmethod
    def start_function(cls) -> base.T_RetCodeMessage:
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
    def stop_function(cls) -> base.T_RetCodeMessage:
        '''
        This really should not be needed at all.
        '''
        # Teardown the tmux
        tmux_iiwi = tmux.find_or_create('iiwi_ctrl')
        tmux.send_keys(tmux_iiwi, 'release(); quit()')

        if not (tmux.expect_no_pid(tmux_iiwi, timeout_sec=15)):
            return (ERR, "IIWI acquisition halt error. Inspect tmux apd_ctrl.")

        return (OK, "Iiwi acquisition halted successfully.")


class DAC40_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.DAC40

    @classmethod
    def start_function(cls) -> base.T_RetCodeMessage:

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
    def stop_function(cls) -> base.T_RetCodeMessage:
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
    def start_function(cls) -> base.T_RetCodeMessage:
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
                iiwi_proxy = connect_aorts(pyrokeys.APD)
                iiwi_proxy.poll_camera_for_keywords()
                return (OK, "APD acq. started successfully.")
            except:
                pass

        return (ERR, "APD startup failure (no pyro proxy after 20 seconds).")

    @classmethod
    def stop_function(cls) -> base.T_RetCodeMessage:
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
    def start_function(cls) -> base.T_RetCodeMessage:
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
    def stop_function(cls) -> base.T_RetCodeMessage:
        '''
        Should only be needed when switching to passthrough.
        '''
        # Teardown the tmux
        tmux_kwfs = tmux.find_or_create('kwfs_ctrl')
        tmux.send_keys(tmux_kwfs, 'release(); quit()')

        if not tmux.expect_no_pid(tmux_kwfs, timeout_sec=10):
            return (ERR, "KWFS acquisition halt error. Inspect tmux kwfs_ctrl.")

        return (OK, "KWFS acquisition halted successfully.")


class PTAPD_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.PT_APD

    @classmethod
    def start_function(cls) -> base.T_RetCodeMessage:
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

    @classmethod
    def stop_function(cls) -> base.T_RetCodeMessage:
        '''
        Teardown for passthrough (no conversion) mode.
        '''
        # Teardown the tmux
        tmux_apd = tmux.find_or_create('pt_apd')
        tmux.kill_running(tmux_apd)

        if not tmux.expect_no_pid(tmux_apd, timeout_sec=3):
            return (ERR, "FPDP APD passthrough halt error. Inspect tmux pt_apd")

        return (OK, "FPDP DAC passthrough halted successfully.")


class PTDAC_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.PT_DAC

    @classmethod
    def start_function(cls) -> base.T_RetCodeMessage:
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
    def stop_function(cls) -> base.T_RetCodeMessage:
        tmux_dac = tmux.find_or_create('pt_dac')
        tmux.kill_running(tmux_dac)

        if not tmux.expect_no_pid(tmux_dac, timeout_sec=3):
            return (ERR, "FPDP DAC passthrough halt error. Inspect tmux pt_dac")

        return (OK, "FPDP DAC passthrough halted successfully.")


class DM3K_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.DM3K

    @classmethod
    def start_function(cls) -> base.T_RetCodeMessage:
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
    def stop_function(cls) -> base.T_RetCodeMessage:
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


#class CACAOLOOP_RTSModule(abc.ABC): # implements RTS_MODULE Protocol

from ..cacao_stuff.loop_manager import CacaoLoopManager


class CACAOLOOP_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME
    LOOP_FULL_NAME: str

    @classmethod
    def start_function(cls, loop_mode: str = None) -> base.T_RetCodeMessage:

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)

        # Just in case?
        #loop_mgr.runstop_aorun()
        loop_mgr.mfilt.loop_open()

        loop_mgr.pre_run_reconfigure_loop_matrices(
                loop_mode
        )  # Should this toggle symlinks? call cacao-aorun-042 ? Load the default one and then algebraically manipulate it to adapt to OLGS/NLGS modes?
        loop_mgr.pre_run_reload_cms_to_shm(
        )  # I suppose this should just call cacao-aorun-042 (which)

        # Can probably do better? By checking that e.g. tmuxes, confs, etc are live.
        loop_mgr.runstart_aorun()

        loop_mgr.post_startup_config_change_given_mode_reconfigure(loop_mode)

        time.sleep(1.0)

        if not (loop_mgr.acquWFS.run_isrunning() and
                loop_mgr.wfs2cmodeval.run_isrunning() and
                loop_mgr.mfilt.run_isrunning() and
                loop_mgr.mvalC2dm.run_isrunning()):
            return (ERR,
                    f'Error starting loop {cls.LOOP_FULL_NAME} from rootdir {loop_mgr.rootdir}'
                    )

        return (OK, f'Started processes for loop {cls.LOOP_FULL_NAME}')

    @classmethod
    def stop_function(cls) -> base.T_RetCodeMessage:

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)

        loop_mgr.mfilt.loop_open()
        loop_mgr.runstop_aorun(stop_acqWFS=True)

        time.sleep(1.0)

        if (loop_mgr.acquWFS.run_isrunning() or
                    loop_mgr.wfs2cmodeval.run_isrunning() or
                    loop_mgr.mfilt.run_isrunning() or
                    loop_mgr.mvalC2dm.run_isrunning()):
            return (ERR,
                    f'Error stopping loop {cls.LOOP_FULL_NAME} from rootdir {loop_mgr.rootdir}'
                    )

        return (OK, f'Stopped processes for loop {cls.LOOP_FULL_NAME}')


class NIRLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.NIRLOOP
    LOOP_FULL_NAME: str = config.LINFO_IRPYR_3K.full_name


class HOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.HOLOOP
    LOOP_FULL_NAME: str = config.LINFO_HOAPD_3K.full_name


class LOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.LOLOOP
    LOOP_FULL_NAME: str = config.LINFO_LOAPD_3K.full_name


class PTLOOP_RTSModule(CACAOLOOP_RTSModule):
    # WARNING THIS IS AN INCOMPLETE LOOP!!!!!
    # IT DOESN'T HAVE THE 4 AO MAIN MEMBERS
    MODULE_NAMETAG: RME = RME.PTLOOP
    LOOP_FULL_NAME: str = config.LINFO_BIM3KTRANSLATION.full_name


class KWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.KWFSLOOP
    LOOP_FULL_NAME: str = config.LINFO_NLCWFS_3K.full_name


class TTOFFLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.TTOFFL
    LOOP_FULL_NAME: str = config.LINFO_NLCWFS_3K.full_name
