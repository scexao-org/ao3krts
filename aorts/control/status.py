from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..cacao_stuff.mfilt import MFilt

from pyMilk.interfacing.shm import SHM

from .. import config


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

    def __str__(self) -> str:
        s = self
        string = (
                f'LOOP : State = {("OFF", " ON")[self.loop_state]}',
                f'GAIN : DMG = {s.dmg:0.4f} , TTG = {s.ttg:0.4f}',
                f'     : HTT = {s.htt:0.4f} , HDF = {s.hdf:0.4f}',
                f'     : LTT = {s.ltt:0.4f} , LDF = {s.ldf:0.4f}',
                f'     : WTT = {s.wtt:0.4f} , ADF = {s.adf:0.4f}',
                f'TT   : TT_tip = {s.tt_x:0.4f} [V] , TT_tilt = {s.tt_y:0.4f} [V]',
                f'     : WTT_CH1 = {s.wtt_x:0.4f} [V] , WTT_CH2 = {s.wtt_y:0.4f} [V]',
                f'APD  : HOWFS-Ave. = {s.howfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.howfs_rmag:.2f} )',
                f'     : LOWFS-Ave. = {s.lowfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.lowfs_rmag:.2f} )',
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
        self.htt: float = 0.0
        self.hdf: float = 0.0
        self.ltt: float = 0.0
        self.ldf: float = 0.0
        self.wtt: float = 0.0
        self.adf: float = 0.0

        ttval = self.tt_shm.get_data()
        self.tt_x = -ttval[0]
        self.tt_y = ttval[1]
        wttval = self.wtt_shm.get_data()
        self.wtt_x = wttval[0]
        self.wtt_y = wttval[0]

        # Statisticfiers are needed.
        self.howfs_ave: float = 0.0
        self.howfs_rmag: float = -99.0

        self.lowfs_ave: float = 0.0
        self.lowfs_rmag: float = -99.0
