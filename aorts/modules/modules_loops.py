from __future__ import annotations
import typing as typ

import os
import time

from . import base_module_modes as base

from .base_module_modes import RTS_MODULE_ENUM as ModuEn  # Alias
from .base_module_modes import RTS_MODE_ENUM as ModeEn  # Alias

from .. import config

from ..cacao_stuff.loop_manager import CacaoLoopManager, cacao_loop_deploy, CacaoConfigReader

OK = base.OkErrEnum.OK
ERR = base.OkErrEnum.ERR

from pyMilk.interfacing.fps import FPSDoesntExistError, FPS


class CACAOLOOP_RTSModule:  # implements RTS_MODULE_RECONFIGURABLE Protocol
    MODULE_NAMETAG: ModuEn
    LOOP_FULL_NAME: str

    CFG_MODE_DEFAULT: ModeEn
    CFG_NAMES: list[ModeEn]

    @classmethod
    def start_function(cls) -> base.T_Result:
        return cls.start_and_configure(None)

    @classmethod
    def start_and_configure(cls, mode: ModeEn | None = None) -> base.T_Result:
        if mode is None:
            mode = cls.CFG_MODE_DEFAULT

        (ret, msg) = cls._pre_configure_start()
        if ret == ERR:
            return ret, msg

        (ret, msg) = cls.reconfigure(mode)
        if ret == ERR:
            return ret, msg

        (ret, msg) = cls._post_configure_start()
        if ret == ERR:
            return ret, msg

        return OK, f'start_and_configure OK {cls.MODULE_NAMETAG}, {mode}.'

    @classmethod
    def _pre_configure_start(cls) -> base.T_Result:

        # In case loop is alive somehow
        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)
        loop_mgr.runstop_processes(timeout_each=3.0)
        loop_mgr.confstop_processes(timeout_each=3.0)

        cacao_loop_deploy(cls.LOOP_FULL_NAME, delete_logdir=True)

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)
        loop_mgr.confstart_processes()

        aorun_fps = cls._expected_aorun_fps(loop_mgr)
        if any(x is None for x in aorun_fps):
            return (ERR,
                    f'_pre_configure_start for loop {cls.LOOP_FULL_NAME} -- missing core AO pipe FPS.'
                    )

        return (OK, f'_pre_configure_start for loop {cls.LOOP_FULL_NAME}')

        # INFO for subclasses: the tail end of _pre_configure_start is a perfect place to re-route custom symlinks

    @classmethod
    def _expected_aorun_fps(cls, loop_mgr: CacaoLoopManager
                            ) -> typ.Sequence[FPS | None]:
        '''
        Raises FPSDoesntExistError if one of these is missing.
        '''
        return (loop_mgr.acquWFS, loop_mgr.wfs2cmodeval, loop_mgr.mfilt,
                loop_mgr.mvalC2dm)

    @classmethod
    def _post_configure_start(cls) -> base.T_Result:

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)
        loop_mgr.runstart_aorun()

        time.sleep(1.0)

        run_states = (loop_mgr.acquWFS is None or
                      loop_mgr.acquWFS.run_isrunning(), loop_mgr.wfs2cmodeval
                      is None or loop_mgr.wfs2cmodeval.run_isrunning(),
                      loop_mgr.mfilt is None or loop_mgr.mfilt.run_isrunning(),
                      loop_mgr.mvalC2dm is None or
                      loop_mgr.mvalC2dm.run_isrunning())

        if not all(run_states):
            return (ERR,
                    f'Error in _post_configure_start loop {cls.LOOP_FULL_NAME} from rootdir {loop_mgr.rootdir}'
                    f'Process runstates are {run_states}.')

        return (OK, f'_post_configure_start for loop {cls.LOOP_FULL_NAME}')

    @classmethod
    def stop_function(cls) -> base.T_Result:

        # In case loop is alive somehow
        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)
        loop_mgr.runstop_processes(timeout_each=3.0)
        loop_mgr.confstop_processes(timeout_each=3.0)

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)

        if loop_mgr.mfilt:
            loop_mgr.mfilt.loopON = False

        loop_mgr.runstop_aorun(stop_acqWFS=True)

        time.sleep(1.0)

        if ((loop_mgr.acquWFS and loop_mgr.acquWFS.run_isrunning()) or
            (loop_mgr.wfs2cmodeval and loop_mgr.wfs2cmodeval.run_isrunning()) or
            (loop_mgr.mfilt and loop_mgr.mfilt.run_isrunning()) or
            (loop_mgr.mvalC2dm and loop_mgr.mvalC2dm.run_isrunning())):
            return (ERR,
                    f'Error stopping loop {cls.LOOP_FULL_NAME} from rootdir {loop_mgr.rootdir}'
                    )

        return (OK, f'Stopped processes for loop {cls.LOOP_FULL_NAME}')

    @classmethod
    def reconfigure(cls, mode: ModeEn) -> base.T_Result:
        '''
        In case the loop described by this class doesn't really require a reconfiguration
        We just call milk-FITS2shm on the default FITS path
        And we get going.
        '''
        import subprocess as sproc

        cfg = CacaoConfigReader(cls.LOOP_FULL_NAME, None)

        file = str(cfg.rootdir / 'conf' / 'CMmodesWFS' / 'CMmodesWFS.fits')
        shm = f'aol{cfg.loop_number}_CMmodesWFS'
        sproc.run(f'milk-FITS2shm {file} {shm}'.split())

        file = str(cfg.rootdir / 'conf' / 'CMmodesDM' / 'CMmodesDM.fits')
        shm = f'aol{cfg.loop_number}_CMmodesDM'
        sproc.run(f'milk-FITS2shm {file} {shm}'.split())

        return OK, 'Loaded default RM paths.'


class NIRLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: ModuEn = ModuEn.NIRLOOP
    LOOP_FULL_NAME: str = config.LINFO_IRPYR_3K.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.NIR3K
    CFG_NAMES = []


class HOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: ModuEn = ModuEn.HOLOOP
    LOOP_FULL_NAME: str = config.LINFO_HOAPD_3K.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.NGS3K
    CFG_NAMES = [ModeEn.NGS3K, ModeEn.OLGS3K, ModeEn.NLGS3K]  # What about TT?

    @classmethod
    def reconfigure(cls, mode: ModeEn) -> base.T_Result:
        import subprocess as sproc
        cfg = CacaoConfigReader(cls.LOOP_FULL_NAME, None)

        if mode == ModeEn.NGS3K:
            file = str(cfg.rootdir / 'conf' / 'CMmodesWFS' / 'CMmodesWFS.fits')
        elif mode == ModeEn.OLGS3K or mode == ModeEn.NLGS3K:
            file = str(cfg.rootdir / 'conf' / 'CMmodesWFS' /
                       'CMmodesWFS_LGS.fits')
        else:
            return (ERR,
                    f'Mode {mode} not OK to configure for HOWFSLOOP_RTSModule')

        shm = f'aol{cfg.loop_number}_CMmodesWFS'
        sproc.run(f'milk-FITS2shm {file} {shm}'.split())

        file = str(cfg.rootdir / 'conf' / 'CMmodesDM' / 'CMmodesDM.fits')
        shm = f'aol{cfg.loop_number}_CMmodesDM'
        sproc.run(f'milk-FITS2shm {file} {shm}'.split())

        return OK, f'Loaded HOWFSLOOP_RTSModule CMs for mode {mode}'


class LOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: ModuEn = ModuEn.LOLOOP
    LOOP_FULL_NAME: str = config.LINFO_LOAPD_3K.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.NLGS3K
    CFG_NAMES = [ModeEn.OLGS3K, ModeEn.NLGS3K, ModeEn.TT3K]

    @classmethod
    def reconfigure(cls, mode: ModeEn) -> base.T_Result:
        return (OK, 'BYPASS reconfigure @ LOWFSLOOP_RTSModule')
        1 / 0  # MHHHHH
        ...

    @classmethod
    def _expected_aorun_fps(cls, loop_mgr: CacaoLoopManager
                            ) -> typ.Sequence[FPS | None]:
        '''
        Raises FPSDoesntExistError if one of these is missing.
        '''
        # FIXME must reconf symlink directly from
        return (loop_mgr.acquWFS, loop_mgr.mfilt, loop_mgr.mvalC2dm)


class PTLOOP_RTSModule(CACAOLOOP_RTSModule):
    # WARNING THIS IS AN INCOMPLETE LOOP!!!!!
    # IT DOESN'T HAVE THE 4 AO MAIN MEMBERS
    MODULE_NAMETAG: ModuEn = ModuEn.PTLOOP
    LOOP_FULL_NAME: str = config.LINFO_BIM3KTRANSLATION.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.PT3K
    CFG_NAMES = []

    @classmethod
    def _expected_aorun_fps(cls, loop_mgr: CacaoLoopManager
                            ) -> typ.Sequence[FPS | None]:
        return (loop_mgr.mvalC2dm, loop_mgr.acquWFS)

    @classmethod
    def _pre_configure_start(cls):
        (ret, msg) = super()._pre_configure_start()

        loop_cfg = CacaoConfigReader(cls.LOOP_FULL_NAME, None)
        targ = os.environ[
                'MILK_SHM_DIR'] + f'/aol{loop_cfg.loop_number}_mC.im.shm'
        if os.path.exists(targ):
            os.remove(targ)
        os.symlink('dm64disp07.im.shm', targ)
        # This is an example -- assuming this particular loop would like to do symlink shenanigans post-deployment of the FPSs

        return ret, msg


class KWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: ModuEn = ModuEn.KWFSLOOP
    LOOP_FULL_NAME: str = config.LINFO_NLCWFS_3K.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.UNKNOWN
    CFG_NAMES = []


class TTOFFLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: ModuEn = ModuEn.TTOFFL
    LOOP_FULL_NAME: str = config.LINFO_3KTTOFFLOAD.full_name
    CFG_MODE_DEFAULT: ModeEn = ModeEn.NIR3K
    CFG_NAMES = []
