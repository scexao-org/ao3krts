from __future__ import annotations

import typing as typ

import sys


def modeselect():
    from ..server.system_commands import ModeSwitcher
    return ModeSwitcher.DISPATCHER.click_dispatch_cli_calls(sys.argv[1:])


if __name__ == '__main__':
    modeselect()
