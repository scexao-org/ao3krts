from __future__ import annotations
import typing as typ

from . import base_module_modes as base

if typ.TYPE_CHECKING:
    RME: typ.TypeAlias = base.RTS_MODULE_ENUM  # Alias
    CSE: typ.TypeAlias = base.CONFIG_SUBMODES_ENUM  # Alias
    OK = base.OkErrEnum.OK
    ERR = base.OkErrEnum.ERR


class WTTOffloader_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.WTTOFF

    @classmethod
    def start_function(cls) -> base.T_Result:
        ...

    @classmethod
    def stop_function(cls) -> base.T_Result:
        ...


class FOCOffloader_RTSModule:  # implements RTS_MODULE_CONFIGURABLE Protocol
    MODULE_NAMETAG: RME = RME.FOCOFF

    CFG_NAMES: list[CSE] = [CSE.OLGS, CSE.NLGS]

    last_requested_mode: CSE | None = None

    @classmethod
    def start_function(cls) -> base.T_Result:
        '''
        if fps_exists:
            open_fps
        else:
            create_fps_w/_reconfigure(last_requested_mode)


        bla bla tmux, open session, clean it, spawn rts_offloader:main_au1
        '''
        # TODO
        ...

    @classmethod
    def stop_function(cls) -> base.T_Result:
        # TODO
        ...

    @classmethod
    def reconfigure(cls, mode: CSE) -> base.T_Result:
        '''
        if running:
        or straight up:
        cls.stop_function()
            # Am I even in charge of checking that?
            decline()
        nuke_fps()
        re_make_fps as we want it.
        '''
        # TODO
        ...

    @classmethod
    def start_and_configure(cls, mode: CSE | None = None) -> base.T_Result:
        # TODO
        ...
