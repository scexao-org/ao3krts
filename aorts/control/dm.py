from __future__ import annotations

import typing as typ

import os
import time
import logging

logg = logging.getLogger(__name__)

import numpy as np
from astropy.io import fits

from pyMilk.interfacing.shm import SHM
from pyMilk.interfacing.fps import FPS

from .. import config


class DMCombManager:

    SHAPE: int | tuple[int, int]

    def __init__(self, dm_number: str) -> None:

        self.dm_number: str = dm_number

        self.fps: FPS | None = None
        try:
            self.fps = FPS(f'DMch2disp-{dm_number}')
        except RuntimeError:
            pass

        if self.fps:
            self.ensure_running()

        self.dm_shm_out = SHM(f'dm{dm_number}disp')

        self.dm_shms: list[SHM | None] = [
                self._find_shm_or_None(ii) for ii in range(12)
        ]

    def _find_shm_or_None(self, ii: int) -> SHM | None:
        try:
            return SHM(f'dm{self.dm_number}disp{ii:02d}')
        except FileNotFoundError:
            return None

    def ensure_running(self) -> None:
        assert self.fps
        if not self.fps.conf_isrunning():
            self.fps.conf_start()
            time.sleep(2.0)
        if not self.fps.run_isrunning():
            self.fps.run_start()
            time.sleep(5.0)

        assert self.fps.conf_isrunning() and self.fps.run_isrunning()

    def zero(self, do_ch_zero: bool = True,
             do_other_channels: bool = True) -> None:
        if do_ch_zero and self.dm_shms[0] is not None:
            self.dm_shms[0].set_data(np.zeros(self.SHAPE, np.float32),
                                     autorelink_if_need=True)

        if do_ch_zero and do_other_channels:
            for dm_shm_chan in self.dm_shms:
                if dm_shm_chan is not None:
                    dm_shm_chan.set_data(np.zeros(self.SHAPE, np.float32),
                                         autorelink_if_need=True)


class BIM188Manager(DMCombManager):

    SHAPE = 188

    def __init__(self) -> None:
        super().__init__(config.DMNUM_BIM188)

    def flat(self) -> None:
        self.zero(do_ch_zero=False)
        # force resolution of symlink?
        flat_file: str = os.path.realpath(
                os.environ['HOME'] +
                '/conf/bim188_flats/current_flat_symlink.fits')

        flat: np.ndarray = fits.getdata(flat_file)  # type: ignore

        assert flat.shape == (self.SHAPE, )
        assert self.dm_shms[0] is not None
        self.dm_shms[0].set_data(flat, check_dt=True)


class TTManager(DMCombManager):

    SHAPE = 2

    def __init__(self) -> None:
        super().__init__(config.DMNUM_TT)

    '''
    THOSE WERE NICE WE PROBABLY WANT TO KEEP THEM

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
    '''


class DM3kManager(DMCombManager):

    SHAPE = (64, 64)

    def __init__(self) -> None:
        super().__init__(config.DMNUM_ALPAO)

    def flat(self) -> None:
        self.zero(do_ch_zero=False)

        # force resolution of symlink?
        flat_file: str = os.path.realpath(
                os.environ['HOME'] +
                '/conf/alpao_flats/current_flat_symlink.fits')

        flat: np.ndarray = fits.getdata(flat_file)  # type: ignore
        assert flat.shape == self.SHAPE
        assert self.dm_shms[0] is not None
        self.dm_shms[0].set_data(flat, check_dt=True)


class WTTManager:

    def __init__(self):
        self.shm = SHM('wtt_value_float')

    def zero(self):
        self.shm.set_data(np.zeros(2, np.float32))

    def flat(self):
        self.shm.set_data(np.zeros(2, np.float32) + 5.0)
