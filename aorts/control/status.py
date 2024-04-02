from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from .dispatcher import DocoptDispatchingObject, locking_func_decorator

from pyMilk.interfacing.shm import SHM

from .. import config


class StatusObj(DocoptDispatchingObject):

    NAME = 'STATUS'

    DESCR = 'RTS Status report'

    DOCOPTSTR = '''RTS Status report
Usage:
    status gen2     # Ask for status message. On a fresh instance, this will result in a 1-second poll.

Options:

'''

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

        self.TCP_CALLS = {'gen2': self.status_report}

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

    def status_report(self):
        self.update_status()
        return self.__str__()
