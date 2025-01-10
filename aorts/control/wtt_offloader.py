from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from pyMilk.interfacing.fps import (SmartAttributesFPS, FPS_type, FPS_flags,
                                    FPSDoesntExistError)

from ..cacao_stuff.mfilt import MFilt


class WTTOffloaderFPS(MFilt):
    in_stream: str  #= ('Input stream', FPS_type.STREAMNAME, FPS_flags.DEFAULT_INPUT_STREAM)

    # Prepare outputs for the underlying runtime
    m_frate: float  #= ('Measured framerate', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)
    out_tip: float  #= ('av_tip', 'av. tip', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)
    out_til: float  #= ('av. tilt', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)

    # yapf: disable
    _DICT_METADATA = {
            'in_stream': ('Input stream', FPS_type.STREAMNAME,
                          FPS_flags.DEFAULT_INPUT_STREAM),
            'm_frate': ('Measured framerate', FPS_type.FLOAT64,
                        FPS_flags.DEFAULT_OUTPUT),
            'out_tip': ('out. tip', FPS_type.FLOAT64,
                       FPS_flags.DEFAULT_OUTPUT),
            'out_til': ('out. tilt', FPS_type.FLOAT64,
                        FPS_flags.DEFAULT_OUTPUT),
    }
    _DICT_METADATA.update(MFilt._DICT_METADATA)
    # yapf: enable

    def post_create_set_defaults(self):
        super().post_create_set_defaults()
        self.in_stream = ''
        self.m_frate = 1.0
        self.out_tip = 0.0
        self.out_til = 0.0

        # Override superclass specifically because this is WTT
        self.looplimit = 5.0


class WTTOffloaderControl:
    '''
    This is the control class for lgsoffloadermains.wtt

    We're going to instantiate a custom FPS and talk to it through this class.
    '''
    FPS_NAME = 'wtt_offl'

    def __init__(self, allow_creation: bool = True) -> None:
        try:
            self.fps = WTTOffloaderFPS(self.FPS_NAME)
        except FPSDoesntExistError:
            if allow_creation:
                self.fps = self._force_recreate_fps()
            else:
                raise

    def _force_recreate_fps(self) -> WTTOffloaderFPS:

        fps = WTTOffloaderFPS.create(self.FPS_NAME, force_recreate=True)

        return fps

    def loop_close(self):
        self.fps.loopON = True

    def loop_open(self):
        self.fps.loopON = False

    def set_input_stream(self, stream_name: str):
        '''
        Can we even change this at runtime??? Probs deffo not.
        '''
        self.fps.in_stream = stream_name

    def set_gain(self, gain: float):
        self.fps.loopgain = gain

    def set_mult(self, mult: float):
        self.fps.loopmult = mult

    def set_limit(self, limit: float):
        self.fps.looplimit = limit

    def reset(self):
        '''
        Reset the outputs.
        IF the real-time statistics are running and they see this flag, it should
        reset the outputs to zero.
        BUT if they're not running, might as well reset from this side.
        '''
        self.fps.loopZERO = True

        self.fps.out_tip = 0.0
        self.fps.out_til = 0.0
