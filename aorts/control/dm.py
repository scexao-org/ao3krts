from __future__ import annotations

import typing as typ

import os, pathlib
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
    CONFDIR: str | pathlib.Path | None

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

    def flat(self) -> None:
        assert self.CONFDIR is not None
        self.zero(do_ch_zero=False)

        # force resolution of symlink?
        flat_file: str = os.path.realpath(
                str(self.CONFDIR) + '/current_flat_symlink.fits')

        flat: np.ndarray = fits.getdata(flat_file)  # type: ignore
        assert flat.shape == self.SHAPE
        assert self.dm_shms[0] is not None
        self.dm_shms[0].set_data(flat, check_dt=True)

    def save_0_to_flat(self) -> None:
        new_flat = self.dm_shms[0].get_data()
        self._save_flat_to_file(new_flat)

    def save_agg_to_flat(self) -> None:
        dm_array = np.asarray([dm_chan.get_data() for dm_chan in self.dm_shms])
        new_flat = np.sum(dm_array, axis=0)
        self._save_flat_to_file(new_flat)

    def _save_flat_to_file(self, arr: np.ndarray) -> None:
        assert self.CONFDIR is not None
        assert (arr.ndim == 1 and len(arr) == self.SHAPE) or (arr.shape
                                                              == self.SHAPE)

        # Save cube and flat. Make sure flat is MORE alphabetical than cube...
        import datetime
        timestring = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        new_file = str(self.CONFDIR) + f'/flat_{timestring}.fits'
        fits.writeto(str(new_file), arr)

        symlinkpath = str(self.CONFDIR) + '/current_flat_symlink.fits'
        os.symlink(f'flat_{timestring}.fits', symlinkpath)

        logg.info(f'TT: new flat saved flat_{timestring}.fits.')


class BIM188Manager(DMCombManager):

    SHAPE = 188
    CONFDIR = '/home/rts/conf/bim188_flats'

    def __init__(self) -> None:
        super().__init__(config.DMNUM_BIM188)


class TTManager(DMCombManager):

    SHAPE = 2
    CONFDIR = '/home/rts/conf/tt_flats'

    def __init__(self) -> None:
        super().__init__(config.DMNUM_TT)

    def xset(self, val_x: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None
        vals = shm.get_data()
        vals[0] = val_x
        shm.set_data(vals)

    def yset(self, val_y: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None
        vals = shm.get_data()
        vals[1] = val_y
        shm.set_data(vals)

    def set(self, val_x: float, val_y: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None
        shm.set_data(np.array([val_x, val_y], np.float32),
                     autorelink_if_need=True)

    def xnudge(self, val_x: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None
        vals = shm.get_data()
        vals[0] += val_x
        shm.set_data(vals)

    def ynudge(self, val_y: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None
        vals = shm.get_data()
        vals[1] += val_y
        shm.set_data(vals)

    def nudge(self, val_x: float, val_y: float, chan: int = 0) -> None:
        shm = self.dm_shms[chan]
        assert shm is not None

        shm.set_data(
                np.array([val_x, val_y], np.float32) + shm.get_data(),
                autorelink_if_need=True)


class DM3kManager(DMCombManager):

    SHAPE = (64, 64)
    CONFDIR = '/home/rts/conf/alpao_flats'

    def __init__(self) -> None:
        super().__init__(config.DMNUM_ALPAO)


class WTTManager:

    def __init__(self):
        self.shm = SHM('wtt_value_float')

    def zero(self):
        self.shm.set_data(np.zeros(2, np.float32))

    def flat(self):
        self.shm.set_data(np.zeros(2, np.float32) + 5.0)

    def xset(self, val_x: float) -> None:
        vals = self.shm.get_data()
        vals[0] = val_x
        self.shm.set_data(vals)

    def yset(self, val_y: float) -> None:
        vals = self.shm.get_data()
        vals[1] = val_y
        self.shm.set_data(vals)

    def set(self, val_x: float, val_y: float) -> None:
        assert self.shm is not None
        self.shm.set_data(np.array([val_x, val_y], np.float32),
                          autorelink_if_need=True)

    def xnudge(self, val_x: float) -> None:
        vals = self.shm.get_data()
        vals[0] += val_x
        self.shm.set_data(vals)

    def ynudge(self, val_y: float) -> None:
        vals = self.shm.get_data()
        vals[1] += val_y
        self.shm.set_data(vals)

    def nudge(self, val_x: float, val_y: float) -> None:
        assert self.shm is not None
        self.shm.set_data(
                np.array([val_x, val_y], np.float32) + self.shm.get_data(),
                autorelink_if_need=True)
