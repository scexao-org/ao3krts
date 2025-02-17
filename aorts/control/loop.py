from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from dataclasses import dataclass

from pyMilk.interfacing.shm import SHM

from ..cacao_stuff.loop_manager import CacaoLoopManager, CacaoLoopManagerWithMFilt
from .. import config
from ..modules.base_module_modes import RTS_MODE_ENUM as ModeEn


@dataclass
class LoopGainStatusReportStruct:
    # Sentinel values, the we can use the constructor with partial kwargs.
    loop_state: int = 2
    dmg: float = -1.0
    ttg: float = -1.0

    htt: int = -1
    hdf: int = -1

    ltt: float = -1.0
    ldf: float = -1.0
    wtt: float = -1.0

    # adf is OBCP business, not ours.


class LoopGainBaseController:
    Singleton: typ.ClassVar[None | LoopGainBaseController] = None
    Mode: typ.ClassVar[ModeEn]

    _msg_tail = 'on generic superclass or unimplemented subclass.'

    def loop_open(self) -> None:
        raise NotImplementedError(f'loop_open() {self._msg_tail}')

    def loop_close(self) -> None:
        raise NotImplementedError(f'loop_close() {self._msg_tail}')

    def set_dm_gain(self, gain: float) -> None:
        raise NotImplementedError(f'set_dm_gain({gain}) {self._msg_tail}')

    def set_tt_gain(self, gain: float) -> None:
        raise NotImplementedError(f'set_tt_gain({gain}) {self._msg_tail}')

    def set_htt_flag(self, flag: bool) -> None:
        raise NotImplementedError(f'set_htt_gain({flag}) {self._msg_tail}')

    def set_hdf_flag(self, flag: bool) -> None:
        raise NotImplementedError(f'set_hdf_gain({flag}) {self._msg_tail}')

    def set_ltt_gain(self, gain: float) -> None:
        raise NotImplementedError(f'set_ltt_gain({gain}) {self._msg_tail}')

    def set_ldf_gain(self, gain: float) -> None:
        raise NotImplementedError(f'set_ldf_gain({gain}) {self._msg_tail}')

    def set_wtt_gain(self, gain: float) -> None:
        raise NotImplementedError(f'set_wtt_gain({gain}) {self._msg_tail}')

    # This really should be an abstract method? It MUST be subclassed
    # It's used by the status object
    # See aorts.control.status
    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        ...
        raise NotImplementedError(
                f'get_loop_and_gain_states() {self._msg_tail}')


class LoopGainPT3KController(LoopGainBaseController):
    Mode = ModeEn.PT3K

    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        # Spit out defaults -- we know nothing about the system since
        # RTS06 is in charge
        return LoopGainStatusReportStruct()


class LoopGain_NGS_AND_NIR_Controller(LoopGainBaseController):

    def __init__(self) -> None:
        self.dm_loop: CacaoLoopManagerWithMFilt
        self.tt_loop: CacaoLoopManagerWithMFilt
        raise NotImplementedError('Use a subclass.')

    def loop_open(self) -> None:
        self.tt_loop.mfilt.loopON = False
        self.dm_loop.mfilt.loopON = False

    def loop_close(self) -> None:
        self.dm_loop.mfilt.loopZERO = True
        self.tt_loop.mfilt.loopZERO = True

        self.dm_loop.mfilt.loopON = True
        self.tt_loop.mfilt.loopON = True

    def set_dm_gain(self, gain: float) -> None:
        self.dm_loop.mfilt.loopgain = gain

    def set_tt_gain(self, gain: float) -> None:
        self.tt_loop.mfilt.loopgain = gain

    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        return LoopGainStatusReportStruct(
                loop_state=self._figure_out_loop_state(),
                dmg=self.dm_loop.mfilt.loopgain,
                ttg=self.tt_loop.mfilt.loopgain, htt=1, hdf=1)

    def _figure_out_loop_state(self) -> int:
        if self.dm_loop.mfilt.loopON and \
           self.tt_loop.mfilt.loopON:
            return 1  # ON
        elif (not self.dm_loop.mfilt.loopON) and \
             (not self.tt_loop.mfilt.loopON):
            return 0  # OFF
        return 2  # Unknown


class LoopGainNIR3KController(LoopGain_NGS_AND_NIR_Controller):
    Mode = ModeEn.NIR3K

    def __init__(self) -> None:
        self.dm_loop = CacaoLoopManagerWithMFilt(*config.LINFO_IRPYR_3K)
        self.tt_loop = CacaoLoopManagerWithMFilt(*config.LINFO_3KTTOFFLOAD)


class LoopGainNGS3KController(LoopGain_NGS_AND_NIR_Controller):
    Mode = ModeEn.NGS3K

    def __init__(self) -> None:
        self.dm_loop = CacaoLoopManagerWithMFilt(*config.LINFO_HOAPD_3K)
        self.tt_loop = CacaoLoopManagerWithMFilt(*config.LINFO_3KTTOFFLOAD)


class LoopGain_BOTH_OLD_NEW_LGS_3KController(LoopGainBaseController):

    def __init__(self) -> None:
        self.ho_loop = CacaoLoopManagerWithMFilt(*config.LINFO_HOAPD_3K)
        self.lo_loop = CacaoLoopManagerWithMFilt(*config.LINFO_LOAPD_3K)
        self.tt_loop = CacaoLoopManagerWithMFilt(*config.LINFO_3KTTOFFLOAD)

        self.wtt_mgr = None  # TODO

    def loop_open(self) -> None:
        self.ho_loop.mfilt.loopON = False
        self.lo_loop.mfilt.loopON = False
        self.tt_loop.mfilt.loopON = False

    def loop_close(self) -> None:
        self.ho_loop.mfilt.loopZERO = True
        self.lo_loop.mfilt.loopZERO = True

        # Initialize LTT gain, LDF gain
        self.lo_loop.mfilt.loopgain = 1.0
        self.set_ltt_gain(0.0)
        self.set_ldf_gain(0.0)

        self.tt_loop.mfilt.loopZERO = True

        self.ho_loop.mfilt.loopON = True
        self.lo_loop.mfilt.loopON = True
        self.tt_loop.mfilt.loopON = True

    def set_dm_gain(self, gain: float) -> None:
        self.ho_loop.mfilt.loopgain = gain

    def set_tt_gain(self, gain: float) -> None:
        self.tt_loop.mfilt.loopgain = gain

    def set_htt_flag(self, flag: bool) -> None:
        # We proceed by setting the mode limit for tip-tilt.
        # Since the SHM is overwritten on mfilt runstart
        # We MUST expect that mfilt is running (but then this entire class expects this)
        with SHM(f'aol{self.ho_loop.loop_number}_mlimitfact') as ho_lims_shm:
            ho_lims_data = ho_lims_shm.get_data()
            ho_lims_data[:2] = float(flag)  # TT
            ho_lims_shm.set_data(ho_lims_data)

    def set_hdf_flag(self, flag: bool) -> None:

        with SHM(f'aol{self.ho_loop.loop_number}_mlimitfact') as ho_lims_shm:
            ho_lims_data = ho_lims_shm.get_data()
            ho_lims_data[2] = float(flag)  # Focus
            ho_lims_shm.set_data(ho_lims_data)

    def set_ltt_gain(self, gain: float) -> None:

        with SHM(f'aol{self.lo_loop.loop_number}_mgainfact') as lo_gains_shm:
            lo_gains_data = lo_gains_shm.get_data()
            lo_gains_data[:2] = gain  # TT
            lo_gains_shm.set_data(lo_gains_data)

    def set_ldf_gain(self, gain: float) -> None:
        with SHM(f'aol{self.lo_loop.loop_number}_mgainfact') as lo_gains_shm:
            lo_gains_data = lo_gains_shm.get_data()
            lo_gains_data[2] = gain  # Focus
            lo_gains_shm.set_data(lo_gains_data)

    def set_wtt_gain(self, gain: float) -> None:
        from ..control.wtt_offloader import WTTOffloaderControl
        wtt_controller = WTTOffloaderControl(allow_creation=False)
        wtt_controller.set_gain(gain)

    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        from ..control.wtt_offloader import WTTOffloaderControl
        wtt_controller = WTTOffloaderControl(allow_creation=False)

        with SHM(f'aol{self.ho_loop.loop_number}_mlimitfact') as s:
            ho_lims_data = s.get_data()
        with SHM(f'aol{self.lo_loop.loop_number}_mgainfact') as s:
            lo_gains_data = s.get_data()

        return LoopGainStatusReportStruct(
                loop_state=self._figure_out_loop_state(),
                dmg=self.ho_loop.mfilt.loopgain,
                ttg=self.tt_loop.mfilt.loopgain, htt=ho_lims_data[0],
                hdf=ho_lims_data[2], ltt=lo_gains_data[0], ldf=lo_gains_data[2],
                wtt=wtt_controller.fps.loopgain)

    def _figure_out_loop_state(self) -> int:
        if self.ho_loop.mfilt.loopON and \
           self.lo_loop.mfilt.loopON and \
           self.tt_loop.mfilt.loopON:
            return 1  # ON
        elif (not self.ho_loop.mfilt.loopON) and \
             (not self.lo_loop.mfilt.loopON) and \
             (not self.tt_loop.mfilt.loopON):
            return 0  # OFF
        return 2  # Unknown


class LoopGainOLGS3KController(LoopGain_BOTH_OLD_NEW_LGS_3KController):
    Mode = ModeEn.OLGS3K


class LoopGainNLGS3KController(LoopGain_BOTH_OLD_NEW_LGS_3KController):
    Mode = ModeEn.NLGS3K


class TestController(LoopGainBaseController):
    Mode = ModeEn.NONE

    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        return LoopGainStatusReportStruct(2, 0.123, 0.456)


_klasses: list[type[LoopGainBaseController]] = [
        LoopGainNGS3KController,
        LoopGainNIR3KController,
        LoopGainNLGS3KController,
        LoopGainOLGS3KController,
        LoopGainPT3KController,
        TestController,
]

SINGLETON_CONTROLLERS_CLASS: dict[ModeEn, type[LoopGainBaseController]] = {
        klass.Mode: klass
        for klass in _klasses
}


def get_singleton_controller_per_mode(mode: ModeEn) -> LoopGainBaseController:
    klass = SINGLETON_CONTROLLERS_CLASS[mode]  # Might raise if mode missing.

    if not klass.Singleton:
        klass.Singleton = klass()

    return klass.Singleton


class GlobalLoopGainController:
    '''
    Loop manager object for loop on / loop off in NIR mode

    This is really the binding for the loop on / off control from gen2.

    E.g this is called by (for setters):

        aorts.server.ao_commands.LoopCommand (>$ rts23 loop ...)
        aorts.server.ao_commands.GainCommand (>$ rts23 gain ...)

    And by (for getter):

        aorts.control.status.StatusObj
        which is itself called by:
            aorts.command.device_commands.StatusCommand (>$ rts23 status ...)
    '''

    def __init__(self) -> None:
        self.refresh_rts_mode()

    def refresh_rts_mode(self) -> None:
        self.rts_mode: ModeEn = ModeEn.read_rtsmode()
        self.inner_controller: LoopGainBaseController =\
            get_singleton_controller_per_mode(self.rts_mode)

    def open_all_loops(self) -> None:
        for klass in SINGLETON_CONTROLLERS_CLASS.values():
            if klass.Singleton:
                try:
                    klass.Singleton.loop_open()
                except:
                    pass

    '''
    Of course all the functions below could be metaprogrammed from
    just a list of function names to pass down to inner_controller.
    '''

    def loop_open(self):
        self.refresh_rts_mode()
        return self.inner_controller.loop_open()

    def loop_close(self):
        self.refresh_rts_mode()
        return self.inner_controller.loop_close()

    def set_dm_gain(self, gain: float):
        self.refresh_rts_mode()
        return self.inner_controller.set_dm_gain(gain)

    def set_tt_gain(self, gain: float):
        self.refresh_rts_mode()
        return self.inner_controller.set_tt_gain(gain)

    def set_htt_flag(self, flag: bool):
        self.refresh_rts_mode()
        return self.inner_controller.set_htt_flag(flag)

    def set_hdf_flag(self, flag: bool):
        self.refresh_rts_mode()
        return self.inner_controller.set_hdf_flag(flag)

    def set_ltt_gain(self, gain: float):
        self.refresh_rts_mode()
        return self.inner_controller.set_ltt_gain(gain)

    def set_ldf_gain(self, gain: float):
        self.refresh_rts_mode()
        return self.inner_controller.set_ldf_gain(gain)

    def set_wtt_gain(self, gain: float):
        self.refresh_rts_mode()
        return self.inner_controller.set_wtt_gain(gain)

    def get_loop_and_gain_states(self) -> LoopGainStatusReportStruct:
        self.refresh_rts_mode()
        return self.inner_controller.get_loop_and_gain_states()
