from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..server.dispatcher import DocoptDispatchingObject, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class WTTManager(DocoptDispatchingObject):
    NAME = 'WTT'

    DESCR = 'WTT control'

    DOCOPTSTR = '''WTT control
Usage:
    wtt x (set|incr) <x>
    wtt y (set|incr) <y>
    wtt center [-a]
    wtt zero [-a]
    wtt (set|incr) <x> <y>

Options:
    -a      zero all channels (instead of only chan 0)
    <x>     Value for 1st axis (volts) [default: 5]
    <y>     Value for 2nd axis (volts) [default: 5]
'''

    DOCOPTCASTER = {
            '<x>': float,
            '<y>': float,
    }

    def __init__(self):
        ...

    @locking_func_decorator
    def zero(self, zero_all: bool = False) -> None:
        self.set(5, 5)
        ...

    @locking_func_decorator
    def xset(self, val_x: float) -> None:
        ...

    @locking_func_decorator
    def yset(self, val_x: float) -> None:
        ...

    @locking_func_decorator
    def set(self, val_x: float, val_y: float) -> None:
        ...
