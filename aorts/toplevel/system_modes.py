from __future__ import annotations

import typing as typ

import click

# We're gonna need a setup and a teardown for all the modes defined
# in config.AORTS_MODES
from .common import RTS_MODE, MacroRetcode
if typ.TYPE_CHECKING:
    from .common import T_RetCodeMessage, T_MacroFunction

from . import mode_macros

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
def start(_mode: str, stop: bool = True):
    mode: RTS_MODE = RTS_MODE(_mode.upper())

    print(mode, type(mode), stop)

    if mode in [RTS_MODE.TEST, RTS_MODE.UNKNOWN, RTS_MODE.NONE]:
        raise ValueError(f'Cannot set mode {mode}.')

    if stop:
        teardown_current_mode()

    startup_sequence = mode_macros.get_startup_call_sequence(mode)

    invoke_sequence_pretty(startup_sequence)

    RTS_MODE.write_rtsmode(mode)


@main.command('stop', short_help="Force stop any mode.")
def stop(mode: RTS_MODE):
    pass


@main.command('stopcurr',
              short_help="Stop current mode [per /tmp/RTS_CURRENTMODE.txt]")
def teardown_current_mode():
    # dispatch
    current_rts_mode = RTS_MODE.read_rtsmode()

    # mode must not be TEST, UNKNOWN, NONE
    if current_rts_mode in [RTS_MODE.TEST, RTS_MODE.UNKNOWN, RTS_MODE.NONE]:
        raise ValueError(f'Invalid current mode file {current_rts_mode}!')

    teardown_sequence = mode_macros.get_teardown_call_sequence(current_rts_mode)

    invoke_sequence_pretty(teardown_sequence)


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


if __name__ == '__main__':
    main()
