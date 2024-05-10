from __future__ import annotations

import typing as typ

import click

# We're gonna need a setup and a teardown for all the modes defined
# in config.AORTS_MODES
from .common import RTS_MODE, RTS_MODULE, MacroRetcode
if typ.TYPE_CHECKING:
    from .common import T_RetCodeMessage, T_MacroFunction

from . import mode_macros, module_macros

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
        type=click.Choice(RTS_MODULE._member_names_, case_sensitive=False),
)
def module_start_command(_module: RTS_MODULE):
    module: RTS_MODULE = RTS_MODULE(_module.upper())

    print('rts-modeselect STARTMODULE:', _module, module, type(module))

    RTS_MODULE.START_FUNC_DICT[module]()


@main.command('stopmodule')
@click.argument(
        '_module',
        type=click.Choice(RTS_MODULE._member_names_, case_sensitive=False),
)
def module_stop_command(_module: RTS_MODULE):
    module: RTS_MODULE = RTS_MODULE(_module.upper())

    print('rts-modeselect STOPMODULE:', _module, module, type(module))

    RTS_MODULE.STOP_FUNC_DICT[module]()


@main.group('switch')
def switch_command():
    pass


@switch_command.command('nir')
def switch_pt_to_nir():
    invoke_sequence_pretty([
            module_macros.pt_apd_teardown, module_macros.pt_dac_teardown,
            module_macros.dac40_startup, module_macros.apd_startup
    ])


@switch_command.command('pt')
def switch_nir_to_pt():
    invoke_sequence_pretty([
            module_macros.apd_teardown,
            module_macros.dac40_teardown,
            module_macros.pt_dac_startup,
            module_macros.pt_apd_startup,
    ])


def invoke_sequence_pretty(seq: list[T_MacroFunction]):
    import rich

    for func in seq:
        print(f'invoking {func.__name__}')
        retcode, message = func()

        if retcode == MacroRetcode.SUCCESS:
            print(f'    YAY!    {message}')
        else:
            print(f'    OOPS!   {message}')
            print(f'Press Enter when ready to continue - Ctrl + C to abort.')
            try:
                input('')
            except KeyboardInterrupt:
                RTS_MODE.write_rtsmode(RTS_MODE.UNKNOWN)
                return


if __name__ == '__main__':
    main()
