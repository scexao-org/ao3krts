from __future__ import annotations

import typing as typ

import logging

logg = logging.getLogger(__name__)

from pyMilk.interfacing.fps import (SmartAttributesFPS, FPS_type, FPS_flags,
                                    FPSDoesntExistError)


# Let's be crazy.
class FocusLGSOffloaderFPS(SmartAttributesFPS):
    in_stream: str  #= ('Input stream', FPS_type.STREAMNAME, FPS_flags.DEFAULT_INPUT_STREAM)
    on_off: bool  #= ('On/off toggle', FPS_type.ONOFF, FPS_flags.DEFAULT_INPUT)
    gain: float  #= ('Averaging gain', FPS_type.FLOAT64, FPS_flags.DEFAULT_INPUT)
    reset: bool  #= ('Reset ave. value', FPS_type.ONOFF, FPS_flags.DEFAULT_INPUT)

    # Prepare outputs for the underlying runtime
    m_frate: float  #= ('Measured framerate', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)
    av_tip: float  #= ('av_tip', 'av. tip', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)
    av_tilt: float  #= ('av. tilt', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)
    av_focus: float  #=('av. focus', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT)

    _DICT_METADATA = {
            'in_stream': ('Input stream', FPS_type.STREAMNAME,
                          FPS_flags.DEFAULT_INPUT_STREAM),
            'on_off':
                    ('On/off toggle', FPS_type.ONOFF, FPS_flags.DEFAULT_INPUT),
            'gain': ('Averaging gain', FPS_type.FLOAT64, FPS_flags.DEFAULT_INPUT
                     ),
            'reset': ('Reset ave. value', FPS_type.ONOFF,
                      FPS_flags.DEFAULT_INPUT),
            'm_frate': ('Measured framerate', FPS_type.FLOAT64,
                        FPS_flags.DEFAULT_OUTPUT),
            'av_tip': ('av. tip', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT),
            'av_tilt': ('av. tilt', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT),
            'av_focus':
                    ('av. focus', FPS_type.FLOAT64, FPS_flags.DEFAULT_OUTPUT),
    }


class FocusLGSOffloader:
    '''
    This is the control class for lgsoffloadermains.wtt

    We're going to instantiate a custom FPS and talk to it through this class.
    '''
    FPS_NAME = 'foc_offl'

    def __init__(self, allow_creation: bool = True) -> None:
        try:
            self.fps = FocusLGSOffloaderFPS(self.FPS_NAME)
        except FPSDoesntExistError:
            if allow_creation:
                self.fps = self._force_recreate_fps()
            else:
                raise

    def _force_recreate_fps(self) -> FocusLGSOffloaderFPS:

        fps = FocusLGSOffloaderFPS.create(self.FPS_NAME, force_recreate=True)

        fps.on_off = False
        fps.gain = 0.0

        return fps

    def enable(self):
        self.fps['on_off'] = True

    def disable(self):
        self.fps['on_off'] = False

    def set_input_stream(self, stream_name: str):
        self.fps['in_stream'] = stream_name

    def set_ave_gain(self, gain: float):
        self.fps['gain'] = gain

    def reset(self):
        '''
        Reset the outputs.
        IF the real-time statistics are running and they see this flag, it should
        reset the outputs to zero.
        BUT if they're not running, might as well reset from this side.
        '''
        self.fps['reset'] = True

        self.fps['av_tip'] = 0.0
        self.fps['av_tilt'] = 0.0
        self.fps['av_focus'] = 0.0
