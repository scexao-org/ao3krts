from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..cacao_stuff.mfilt import MFilt

from pyMilk.interfacing.shm import SHM

from .. import config

# Constants for magnitude calcs
# units is -0.4 Log10 (kcounts/sec/elem)
HOWFS_ZP = 15.7
LOWFS_ZP = 18.7


class StatusObj:

    def __init__(self):

        # Begin report variables
        self.loop_state: bool = False

        self.dmg: float = 0.0
        self.ttg: float = 0.0
        self.htt: float = 0.0
        self.hdf: float = 0.0
        self.ltt: float = 0.0
        self.ldf: float = 0.0
        self.wtt: float = 0.0
        self.adf: float = 0.0

        self.tt_x: float = 0.0
        self.tt_y: float = 0.0
        self.wtt_x: float = 0.0
        self.wtt_y: float = 0.0
        self.ctt_x: float = 0.0
        self.ctt_y: float = 0.0

        self.howfs_ave: float = 0.0
        self.howfs_rmag: float = -99.0

        self.lowfs_ave: float = 0.0
        self.lowfs_rmag: float = -99.0

        # End report variables

        # Reporting objects
        self.mfilt_nir3kloop = MFilt(f'mfilt-{config.LOOPNUM_IRPYR_ALPAO}')
        self.mfilt_ttoffload = MFilt(f'mfilt-{config.LOOPNUM_ALPAO2TT_OFFLOAD}')

        self.tt_shm = SHM('tt_telemetry')
        self.wtt_shm = SHM('wtt_telemetry')
        self.ctt_shm = SHM('ctt_telemetry')

        self.apd_ave_shm = SHM('apd_ave')  # Warning 2 x 216
        assert self.apd_ave_shm.shape == (
                2, 216)  # Never too sure, one transpose away...

    def __str__(self) -> str:
        s = self
        X1 = X2 = X3 = Y1 = Y2 = 0
        string = (
                f'LOOP : State = {("OFF", " ON")[self.loop_state]}',
                f'GAIN : DMG = {s.dmg:0.4f} , TTG = {s.ttg:0.4f}',
                f'     : HTT = {s.htt:0.4f} , HDF = {s.hdf:0.4f}',
                f'     : LTT = {s.ltt:0.4f} , LDF = {s.ldf:0.4f}',
                f'     : WTT = {s.wtt:0.4f} , ADF = {s.adf:0.4f}',
                f'TT   : TT_tip = {s.tt_x:0.4f} [V] , TT_tilt = {s.tt_y:0.4f} [V]',
                f'     : WTT_CH1 = {s.wtt_x:0.4f} [V] , WTT_CH2 = {s.wtt_y:0.4f} [V]',
                f'     : CTT_CH1 = {s.ctt_x:0.4f} [V] , CTT_CH2 = {s.ctt_y:0.4f} [V]',
                f'APD  : HOWFS-Ave. = {s.howfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.howfs_rmag:.2f} )',
                f'     : LOWFS-Ave. = {s.lowfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.lowfs_rmag:.2f} )',
                f'Eval : DMdefocus = {X1:.3f} , CVdefocus = {X2:.3f} , LWdefocus = {X3:.3f}',  # units? Mean value.
                f'     : LWttx = {Y1:.3f} , LWtty = {Y2:.3f}',  # TT x and y from LOWFS mean value.
                #f'     : WFE = 0.000',
                #f'     : DMvar = 0.000 , DMtvar = 0.000 , DMfvar = 0.000', # No idea.
                #f'     : TTvar = 0.000 , TTtvar = 0.000 , TTfvar = 1.791',
                #f'     : CVvar = 0.000 , CVtvar = 0.000 , CVfvar = 0.000',
        )

        return '\n'.join(string)

    def status_report(self) -> str:
        self.update_status()
        return self.__str__()

    def update_status(self) -> None:
        '''
            This function performs the internal polling necessary to have an up-to-date status
        '''
        self.loop_state = self.mfilt_nir3kloop.loopON

        self.dmg = self.mfilt_nir3kloop.loopgain
        self.ttg = self.mfilt_ttoffload.loopgain

        # Should these be the rel gains on HTT? i.e. on top of DMG.
        self.htt: float = 0.0
        self.hdf: float = 0.0

        # Idem.
        self.ltt: float = 0.0
        self.ldf: float = 0.0

        # Little more specific.
        self.wtt: float = 0.0
        self.adf: float = 0.0

        ttval = self.tt_shm.get_data()
        self.tt_x = -ttval[0]  # ACHTUNG! From TT mount position flip.
        self.tt_y = ttval[1]

        self.wtt_x, self.wtt_y = self.wtt_shm.get_data()
        self.ctt_x, self.ctt_y = self.ctt_shm.get_data()

        # Statisticfiers are needed.
        apd_data = self.apd_ave_shm.get_data(False, autorelink_if_need=True)
        # * 2 converts count/frame/elem to kcount/sec/elem -- or does it??
        self.howfs_ave: float = np.mean(
                apd_data[:, :188]) * 2 + 1e-7  # type: ignore
        self.howfs_rmag: float = HOWFS_ZP - 0.4 * np.log10(self.howfs_ave)

        self.lowfs_ave: float = np.mean(
                apd_data[:, 188:204]) * 2 + 1e-7  # type: ignore
        self.lowfs_rmag: float = LOWFS_ZP - 0.4 * np.log10(self.howfs_ave)
