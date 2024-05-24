from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..server.dispatcher import DocoptDispatchingObject, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class TipTiltManager(DocoptDispatchingObject):
    NAME = 'TT'

    DESCR = 'Tip-tilt control'

    DOCOPTSTR = '''Tip-tilt control
Usage:
    tt x (set|incr) <x>
    tt y (set|incr) <y>
    tt zero [-a]
    tt (set|incr) <x> <y>

Options:
    -a      zero all channels (instead of only chan 0)
    <x>     Value for 1st axis (volts) [default: 0]
    <y>     Value for 2nd axis (volts) [default: 0]
'''

    DOCOPTCASTER = {
            '<x>': float,
            '<y>': float,
    }

    def __init__(self):

        self.tt_shm_0 = SHM(f'dm{config.DMNUM_TT}disp00')
        self.tt_shm_out = SHM(f'dm{config.DMNUM_TT}disp')

        self.tt_shms = [
                SHM(f'dm{config.DMNUM_TT}disp{ii:02d}') for ii in range(12)
        ]

    @locking_func_decorator
    def zero(self, zero_all: bool = False) -> None:
        self.set(0, 0)

        if zero_all:
            for ii in range(12):
                self.tt_shms[ii].set_data(np.array([0, 0], np.float32),
                                          autorelink_if_need=True)

    @locking_func_decorator
    def xset(self, val_x: float) -> None:
        vals = self.tt_shm_0.get_data()
        vals[0] = val_x
        self.tt_shm_0.set_data(vals)

    @locking_func_decorator
    def yset(self, val_x: float) -> None:
        vals = self.tt_shm_0.get_data()
        vals[1] = val_x
        self.tt_shm_0.set_data(vals)

    @locking_func_decorator
    def set(self, val_x: float, val_y: float) -> None:
        self.tt_shm_0.set_data(np.array([val_x, val_y], np.float32),
                               autorelink_if_need=True)
