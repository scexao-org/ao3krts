from __future__ import annotations

import typing as typ

import click

# We're gonna need a setup and a teardown for all the modes defined
# in config.AORTS_MODES
from .base_module_modes import RTS_MODE, RTS_MODULE, RTS_MODULE_ENUM, MacroRetcode
from .dict_module_modes import MODULE_MAPPER
if typ.TYPE_CHECKING:
    from .base_module_modes import T_RetCodeMessage, T_MacroFunction

from . import modules

DOC = '''
    System-wide AO mode manager

Usage:
    rts-modeselect start [-f] <mode>
    rts-modeselect stop <mode>
'''


@click.group('rts-modeselect')
def main():
    pass


@main.command('start', short_help="Start any mode")
@click.argument(
        '_mode',
        type=click.Choice(RTS_MODE._member_names_, case_sensitive=False),
)
@click.option('--stop/--no-stop', default=True, help="Stop current mode first.")
def start_command(_mode: str, stop: bool = True):
    mode: RTS_MODE = RTS_MODE(_mode.upper())

    print('rts-modeselect START:', mode, type(mode), stop)

    if mode in [RTS_MODE.TEST, RTS_MODE.UNKNOWN, RTS_MODE.NONE]:
        raise ValueError(f'Cannot set mode {mode}.')

    if stop:
        current_mode_stop()

    startup_sequence = mode_macros.get_startup_call_sequence(mode)

    invoke_sequence_pretty(startup_sequence)

    RTS_MODE.write_rtsmode(mode)


@main.command('stop', short_help="Force stop any mode.")
@click.argument(
        '_mode',
        type=click.Choice(RTS_MODE._member_names_, case_sensitive=False),
)
def stop_command(_mode: RTS_MODE):
    mode: RTS_MODE = RTS_MODE(_mode.upper())

    print('rts-modeselect STOP:', _mode, mode, type(mode))

    if mode in [RTS_MODE.TEST, RTS_MODE.UNKNOWN, RTS_MODE.NONE]:
        raise ValueError(f'Cannot stop mode {mode}.')

    halt_sequence = mode_macros.get_teardown_call_sequence(mode)
    invoke_sequence_pretty(halt_sequence)

    RTS_MODE.write_rtsmode(mode)


@main.command('stopcurr',
              short_help="Stop current mode [per /tmp/RTS_CURRENTMODE.txt]")
def current_mode_stop_command():
    current_mode_stop()


def current_mode_stop():
    current_rts_mode = RTS_MODE.read_rtsmode()

    # mode must not be TEST, UNKNOWN, NONE
    if current_rts_mode in [RTS_MODE.TEST, RTS_MODE.UNKNOWN, RTS_MODE.NONE]:
        raise ValueError(f'Invalid current mode file {current_rts_mode}!')

    teardown_sequence = mode_macros.get_teardown_call_sequence(current_rts_mode)

    invoke_sequence_pretty(teardown_sequence)


@main.command('startmodule')
@click.argument(
        '_module',
        type=click.Choice(RTS_MODULE_ENUM._member_names_, case_sensitive=False),
)
def module_start_command(_module: str):
    module_tag = RTS_MODULE_ENUM(_module.upper())
    module_class = MODULE_MAPPER[module_tag]

    print('rts-modeselect STARTMODULE:', _module, module_tag, module_class)

    (c, s) = module_class.start_function()

    if c == MacroRetcode.SUCCESS:
        print(f'    YAY!    {s}')
    else:
        print(f'    OOPS!   {s}')


@main.command('stopmodule')
@click.argument(
        '_module',
        type=click.Choice(RTS_MODULE_ENUM._member_names_, case_sensitive=False),
)
def module_stop_command(_module: str):
    module_tag = RTS_MODULE_ENUM(_module.upper())
    module_class = MODULE_MAPPER[module_tag]

    print('rts-modeselect STOPMODULE:', _module, module_tag, module_class)

    (c, s) = module_class.start_function()
    if c == MacroRetcode.SUCCESS:
        print(f'    YAY!    {s}')
    else:
        print(f'    OOPS!   {s}')


@main.group('switch')
def switch_command():
    pass


@switch_command.command('nir')
def switch_pt_to_nir():
    retcode = invoke_sequence_pretty([
            modules.PTAPD_RTSModule.stop_function,
            modules.PTDAC_RTSModule.stop_function,
            modules.DAC40_RTSModule.start_function,
            modules.APD_RTSModule.start_function,
    ])


@switch_command.command('pt')
def switch_nir_to_pt():
    retcode = invoke_sequence_pretty([
            modules.APD_RTSModule.stop_function,
            modules.DAC40_RTSModule.stop_function,
            modules.PTDAC_RTSModule.start_function,
            modules.PTAPD_RTSModule.start_function,
    ])


def invoke_sequence_pretty_noninteractive(seq: list[T_MacroFunction],
                                          stdout: bool = True):
    for func in seq:
        if stdout:
            print(f'invoking {func.__name__}')
        retcode, message = func()

        if retcode == MacroRetcode.SUCCESS:
            print(f'    YAY!    {message}')
        else:
            print(f'    OOPS!   {message}')
            RTS_MODE.write_rtsmode(RTS_MODE.UNKNOWN)
            return


def invoke_sequence_pretty(seq: list[T_MacroFunction]) -> MacroRetcode:
    import rich

    any_fail = False

    for func in seq:
        print(f'invoking {func.__name__}')
        retcode, message = func()

        if retcode == MacroRetcode.SUCCESS:
            print(f'    YAY!    {message}')
        else:
            any_fail = True
            print(f'    OOPS!   {message}')
            print(f'Press Enter when ready to continue - Ctrl + C to abort.')
            try:
                input('')
            except KeyboardInterrupt:
                RTS_MODE.write_rtsmode(RTS_MODE.UNKNOWN)
                return MacroRetcode.FAILURE

    return MacroRetcode.FAILURE if any_fail else MacroRetcode.SUCCESS


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


if __name__ == '__main__':
    main()
