from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

import numpy as np

from ..cacao_stuff.mfilt import MFilt
from ..control.loop import GlobalLoopGainController

from pyMilk.interfacing.shm import SHM

from .. import config

# Constants for magnitude calcs
# units is -0.4 Log10 (kcounts/sec/elem)
HOWFS_ZP = 15.7
LOWFS_ZP = 18.7

# Make a FOCUS projector for the DM... just for the sake of computing the projection.
x = np.arange(64) - 31.5
PREP_FOCUS = x[None, :]**2 + x[:, None]**2
pixels_to_norm = np.sum(PREP_FOCUS**.5
                        < 28)  # slightly undersize to avoid edge effects
pupil = PREP_FOCUS**.5 < 28
PREP_FOCUS -= np.mean(PREP_FOCUS[pupil])
PREP_FOCUS /= np.mean(PREP_FOCUS[pupil]**2)**.5
PREP_FOCUS /= 3228
PREP_FOCUS *= pupil


class StatusObj:

    def __init__(self):

        self.loop_gain_state_watcher = GlobalLoopGainController()

        # Begin report variables
        self.rts_mode: str = 'Unknown'

        self.loop_state: int = 0  # 0, 1, 2 for off, on, weird.

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

        self.lowfs_data_ave_shm = SHM('lowfs_data_ave')
        self.lowfs_data_ave = self.lowfs_data_ave_shm.get_data(
        )  # 11-element numpy array

        self.ngs_defoc: float = 0.0  # Should come from stats of aol5_modevalWFS
        self.nir_defoc: float = 0.0  # Should come from stats of aol7_modevalWFS
        self.dm_defoc: float = 0.0  # Should come from stats of dm64out

    def __str__(self) -> str:
        s = self
        string = (
                f'MODE : {s.rts_mode}',
                f'LOOP : State = {("OFF", " ON", "???")[self.loop_state]}',
                f'GAIN : DMG = {s.dmg:0.4f} , TTG = {s.ttg:0.4f}',
                f'     : HTT = {s.htt:0.4f} , HDF = {s.hdf:0.4f}',
                f'     : LTT = {s.ltt:0.4f} , LDF = {s.ldf:0.4f}',
                f'     : WTT = {s.wtt:0.4f} , ADF = {s.adf:0.4f}',
                f'TT   : TT_tip = {s.tt_x:0.4f} [V] , TT_tilt = {s.tt_y:0.4f} [V]',
                f'     : WTT_CH1 = {s.wtt_x:0.4f} [V] , WTT_CH2 = {s.wtt_y:0.4f} [V]',
                f'     : CTT_CH1 = {s.ctt_x:0.4f} [V] , CTT_CH2 = {s.ctt_y:0.4f} [V]',
                f'APD  : HOWFS-Ave. = {s.howfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.howfs_rmag:.2f} )',
                f'     : LOWFS-Ave. = {s.lowfs_ave:.2f} [kcnt/sec/elem] , ( Rmag = {s.lowfs_rmag:.2f} )',
                f'Eval : DMdefocus = {s.dm_defoc:.3f} , CVdefocus = {s.ngs_defoc:.3f}',  # units? Mean value.
                f'     : LWdefocus = {s.lowfs_data_ave[10]:.3f} , NIRdefocus = {s.nir_defoc:.3f}',
                # TT x and y from LOWFS mean value. # Swapped to match the axes of HOWFS first 2 modes (will probs change again...).
                f'     : LWttx = {-s.lowfs_data_ave[9]:.3f} , LWtty = {+s.lowfs_data_ave[8]:.3f}',
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
        last_state = self.loop_gain_state_watcher.get_loop_and_gain_states()

        self.rts_mode = self.loop_gain_state_watcher.rts_mode

        self.loop_state = last_state.loop_state

        self.dmg = last_state.dmg
        self.ttg = last_state.ttg

        # Should these be the rel gains on HTT? i.e. on top of DMG.
        self.htt: float = last_state.htt
        self.hdf: float = last_state.hdf

        # Idem.
        self.ltt: float = last_state.ltt
        self.ldf: float = last_state.ldf

        # Little more specific.
        self.wtt: float = last_state.wtt
        self.adf: float = -1.0  # Not our business! OBCP in charge.

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

        self.lowfs_data_ave = self.lowfs_data_ave_shm.get_data()

        try:
            with SHM('aol5_modevalWFS_ave') as s:
                self.ngs_defoc = s.get_data()[2]
                assert isinstance(self.ngs_defoc, float)
        except AssertionError:
            self.ngs_defoc: float = 0.0

        try:
            with SHM('aol7_modevalWFS_ave') as s:
                self.nir_defoc = s.get_data()[2]
                assert isinstance(self.nir_defoc, float)
        except AssertionError:
            self.nir_defoc: float = 0.0

        with SHM('dm64out_ave') as s:
            dm_map = s.get_data()
        with SHM('dm64disp00') as s:
            dm_flat = s.get_data()

        self.dm_defoc = np.sum((dm_map - dm_flat) * PREP_FOCUS)  # type: ignore
