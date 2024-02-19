from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import abc
import docopt

import numpy as np

from .. import config

from pyMilk.interfacing.shm import SHM


class ArgumentTypeError(Exception):
    pass


class TCPAndMainServable(typ.Protocol):

    DOC: str
    NAME: str

    TCP_CALLS: dict[str, typ.Callable[..., str]]

    # TODO: synchronization primitive for TCP-strings + Pyro?
    # MUTEX:

    def tcp_dispatch(self, args: list[str]) -> str:
        try:
            argdict = docopt.docopt(self.DOC, args)
        except docopt.DocoptExit:
            return self.DOC

        return self.TCP_CALLS[args[0]](**argdict)


class TipTiltManager(TCPAndMainServable):
    DOC = '''
   Tip-tilt manager for AO188

   Usage:
        tt x set <val>
        tt y set <val>
        tt zero [-a]
        tt set <a> <b>
'''

    NAME = 'tt'

    def __init__(self) -> None:
        super().__init__()

        self.TCP_CALLS = {
                'zero': self.zero,
                'x': self.xset,
                'y': self.yset,
                'set': self.set,
        }

        self.tt_shm_0 = SHM(f'dm{config.DMNUM_TT}disp00')
        self.tt_shm_out = SHM(f'dm{config.DMNUM_TT}disp')

        self.tt_shms = [
                SHM(f'dm{config.DMNUM_TT}disp{ii:02d}') for ii in range(12)
        ]

    def zero(self, zero_all: bool = False) -> None:
        self.set(0, 0)

        if zero_all:
            for ii in range(12):
                self.tt_shms[ii].set_data(np.array([0, 0], np.float32),
                                          autorelink_if_need=True)

    def xset(self, val_x: float) -> None:
        vals = self.tt_shm_0.get_data()
        vals[0] = val_x
        self.tt_shm_0.set_data(vals)

    def yset(self, val_x: float) -> None:
        vals = self.tt_shm_0.get_data()
        vals[1] = val_x
        self.tt_shm_0.set_data(vals)

    def set(self, val_x: float, val_y: float) -> None:
        self.tt_shm_0.set_data(np.array([val_x, val_y], np.float32),
                               autorelink_if_need=True)


class Bim188Manager(TCPAndMainServable):
    DOC = '''
   Bim188 manager for AO188

   Usage:
        dm zero
'''

    NAME = 'dm'

    def __init__(self) -> None:
        super().__init__()

        self.TCP_CALLS = {
                'zero': self.zero,
        }

        self.dm_shm_0 = SHM(f'dm{config.DMNUM_BIM188}disp00')
        self.dm_shm_out = SHM(f'dm{config.DMNUM_BIM188}disp')

        self.dm_shms = [
                SHM(f'dm{config.DMNUM_BIM188}disp{ii:02d}') for ii in range(12)
        ]

    def zero(self, zero_all: bool = False) -> None:
        self.dm_shm_0.set_data(np.array([0, 0], np.float32),
                               autorelink_if_need=True)

        if zero_all:
            for ii in range(12):
                self.dm_shms[ii].set_data(np.array([0, 0], np.float32),
                                          autorelink_if_need=True)


if __name__ == '__main__':
    tt = TipTiltManager()
    dm = Bim188Manager()
