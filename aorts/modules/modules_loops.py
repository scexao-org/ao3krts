from __future__ import annotations
import typing as typ

import time

from . import base_module_modes as base

RME: typ.TypeAlias = base.RTS_MODULE_ENUM  # Alias
from .. import config

from ..cacao_stuff.loop_manager import CacaoLoopManager

OK = base.OkErrEnum.OK
ERR = base.OkErrEnum.ERR

from ..cacao_stuff.loop_manager import CacaoLoopManager


class CACAOLOOP_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME
    LOOP_FULL_NAME: str

    @classmethod
    def start_function(cls) -> base.T_Result:

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)

        # Just in case?
        #loop_mgr.runstop_aorun()
        loop_mgr.mfilt.loopON = False

        # TODO TODO TODO
        loop_mgr.pre_run_reconfigure_loop_matrices(
        )  # Should this toggle symlinks? call cacao-aorun-042 ? Load the default one and then algebraically manipulate it to adapt to OLGS/NLGS modes? # type: ignore
        loop_mgr.pre_run_reload_cms_to_shm(
        )  # I suppose this should just call cacao-aorun-042 (which) # type: ignore # FIXME TEMP

        # Can probably do better? By checking that e.g. tmuxes, confs, etc are live.
        loop_mgr.runstart_aorun()

        # TODO TODO TODO
        loop_mgr.post_startup_config_change_given_mode_reconfigure(
                loop_mode)  # type: ignore

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
    def stop_function(cls) -> base.T_Result:

        loop_mgr = CacaoLoopManager(cls.LOOP_FULL_NAME, None)

        loop_mgr.mfilt.loopON = False
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

    @classmethod
    def reconfigure(cls, mode: base.CONFIG_SUBMODES_ENUM) -> base.T_Result:
        ...

    @classmethod
    def start_and_configure(cls, mode: base.CONFIG_SUBMODES_ENUM | None = None
                            ) -> base.T_Result:
        ...


class NIRLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.NIRLOOP
    LOOP_FULL_NAME: str = config.LINFO_IRPYR_3K.full_name


class HOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.HOLOOP
    LOOP_FULL_NAME: str = config.LINFO_HOAPD_3K.full_name
    CFG_NAMES: typ.Iterable[base.CONFIG_SUBMODES_ENUM] = (
            base.CONFIG_SUBMODES_ENUM.NGS, base.CONFIG_SUBMODES_ENUM.OLGS,
            base.CONFIG_SUBMODES_ENUM.NLGS)  # What about TT?


class LOWFSLOOP_RTSModule(CACAOLOOP_RTSModule):
    MODULE_NAMETAG: RME = RME.LOLOOP
    LOOP_FULL_NAME: str = config.LINFO_LOAPD_3K.full_name
    CFG_NAMES: typ.Iterable[base.CONFIG_SUBMODES_ENUM] = (
            base.CONFIG_SUBMODES_ENUM.OLGS, base.CONFIG_SUBMODES_ENUM.NLGS,
            base.CONFIG_SUBMODES_ENUM.TT)


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
