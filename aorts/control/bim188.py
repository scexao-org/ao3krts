from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..server.dispatcher import DocoptDispatchingObject, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class Bim188Manager(DocoptDispatchingObject):
    NAME = 'DM'

    DESCR = 'BIM188 control'

    DOCOPTSTR = '''BIM188 control
Usage:
    dm zero [-a]

Options:
    -a      zero all channels (instead of only chan 0)
'''

    DOCOPTCASTER = {}

    def __init__(self) -> None:
        super().__init__()

        self.TCP_CALLS = {
                'zero': self.zero,
        }

        try:
            self.dm_shm_0 = SHM(f'dm{config.DMNUM_BIM188}disp00')
        except FileNotFoundError:
            self.dm_shm_0 = SHM(f'dm{config.DMNUM_BIM188}disp00',
                                np.zeros(188, np.float32))
        try:
            self.dm_shm_out = SHM(f'dm{config.DMNUM_BIM188}disp')
        except:
            self.dm_shm_out = SHM(f'dm{config.DMNUM_BIM188}disp',
                                  np.zeros(188, np.float32))

        self.dm_shms: list[SHM | None] = [
                self._find_shm_or_None(ii) for ii in range(12)
        ]

    def _find_shm_or_None(self, ii: int) -> SHM | None:
        try:
            return SHM(f'dm{config.DMNUM_BIM188}disp{ii:02d}')
        except FileNotFoundError:
            return None

    @locking_func_decorator
    def zero(self, zero_all: bool = False) -> None:
        self.dm_shm_0.set_data(np.zeros(188, np.float32),
                               autorelink_if_need=True)

        if zero_all:
            for ii in range(12):
                s = self.dm_shms[ii]
                if s is not None:
                    s.set_data(np.zeros(188, np.float32),
                               autorelink_if_need=True)
