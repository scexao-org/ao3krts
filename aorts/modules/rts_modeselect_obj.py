from __future__ import annotations

import typing as typ

from .base_module_modes import RTS_MODE_ENUM, RTS_MODULE_ENUM, OkErrEnum
from .dict_module_modes import MODULE_MAPPER
from . import modules_hw as mh

if typ.TYPE_CHECKING:
    from .base_module_modes import T_Result, T_ResFunction


def invoke_sequence_pretty_noninteractive(seq: list[T_ResFunction],
                                          stdout: bool = True) -> None:
    for func in seq:
        if stdout:
            print(f'invoking {func.__name__}')
        retcode, message = func()

        if retcode == OkErrEnum.OK:
            print(f'    YAY!    {message}')
        else:
            print(f'    OOPS!   {message}')
            RTS_MODE_ENUM.write_rtsmode(RTS_MODE_ENUM.UNKNOWN)
            return  # ???


def invoke_sequence_pretty(seq: list[T_ResFunction]) -> OkErrEnum:
    import rich

    any_fail = False

    for func in seq:
        print(f'invoking {func.__name__}')
        retcode, message = func()

        if retcode == OkErrEnum.OK:
            print(f'    YAY!    {message}')
        else:
            any_fail = True
            print(f'    OOPS!   {message}')
            print(f'Press Enter when ready to continue - Ctrl + C to abort.')
            try:
                input('')
            except KeyboardInterrupt:
                RTS_MODE_ENUM.write_rtsmode(RTS_MODE_ENUM.UNKNOWN)
                return OkErrEnum.ERR

    return OkErrEnum.ERR if any_fail else OkErrEnum.OK


def set_mode_in_obcp(mode: str) -> None:
    OBCP_CONF_FILE = "/home/ao/ao188/conf/rts_mode.conf"

    from swmain.network.ssh import single_use_paramiko_call

    single_use_paramiko_call('ao188-2', username='ao',
                             command=f'echo {mode} > {OBCP_CONF_FILE}')


def get_mode_from_obcp() -> str:
    OBCP_CONF_FILE = "/home/ao/ao188/conf/rts_mode.conf"
    from swmain.network.ssh import single_use_paramiko_call
    (stdout, stderr) = single_use_paramiko_call('ao188-2', username='ao',
                                                command=f'cat {OBCP_CONF_FILE}')
    return stdout.strip()


class RTSModeSwitcher:

    def module_start_command(self, _module: RTS_MODULE_ENUM):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        module_class = MODULE_MAPPER[module_tag]

        print('rts-modeselect STARTMODULE:', _module, module_tag, module_class)

        (c, s) = module_class.start_function()

        if c == OkErrEnum.OK:
            print(f'    YAY!    {s}')
        else:
            print(f'    OOPS!   {s}')

    def module_stop_command(self, _module: RTS_MODULE_ENUM):
        module_tag = RTS_MODULE_ENUM(_module.upper())
        module_class = MODULE_MAPPER[module_tag]

        print('rts-modeselect STOPMODULE:', _module, module_tag, module_class)

        (c, s) = module_class.stop_function()
        if c == OkErrEnum.OK:
            print(f'    YAY!    {s}')
        else:
            print(f'    OOPS!   {s}')

    def some_method(self) -> None:
        print('HA THIS IS SOME_METHOD!')

    def switch_pt_to_nir(self):
        retcode = invoke_sequence_pretty([
                mh.PTAPD_RTSModule.stop_function,
                mh.PTDAC_RTSModule.stop_function,
                mh.DAC40_RTSModule.start_function,
                mh.APD_RTSModule.start_function,
        ])
        RTS_MODE_ENUM.write_rtsmode(RTS_MODE_ENUM.NIR3K)
        set_mode_in_obcp('rts23-nirwfs')
        return 'pt'

    def switch_nir_to_pt(self):
        retcode = invoke_sequence_pretty([
                mh.APD_RTSModule.stop_function,
                mh.DAC40_RTSModule.stop_function,
                mh.PTDAC_RTSModule.start_function,
                mh.PTAPD_RTSModule.start_function,
        ])
        set_mode_in_obcp('pass-through')
        RTS_MODE_ENUM.write_rtsmode(RTS_MODE_ENUM.PT3K)
        return 'nir'

    def query(self) -> None:
        obcp_thinks = get_mode_from_obcp()
        from ..modules.base_module_modes import RTS_MODE_ENUM
        rts_thinks = RTS_MODE_ENUM.read_rtsmode()
        print(f'[RTS23 mode] OBCP: {obcp_thinks} - RTS: {rts_thinks}')
