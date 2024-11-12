from __future__ import annotations

import typing as typ

from pyMilk.interfacing.fps import SmartAttributesFPS, FPS_type, FPS_flags


class MFilt(SmartAttributesFPS):
    loopON: bool
    loopZERO: bool
    loopgain: float
    loopmult: float
    looplimit: float

    _DICT_METADATA = {
            'loopON': ('loop on/off (off=freeze)', FPS_type.ONOFF,
                       FPS_flags.DEFAULT_INPUT),
            'loopZERO': ('loop zero', FPS_type.ONOFF, FPS_flags.DEFAULT_INPUT),
            'loopgain':
                    ('loop gain', FPS_type.FLOAT32, FPS_flags.DEFAULT_INPUT),
            'loopmult':
                    ('loop mult', FPS_type.FLOAT32, FPS_flags.DEFAULT_INPUT),
            'looplimit':
                    ('loop limit', FPS_type.FLOAT32, FPS_flags.DEFAULT_INPUT),
    }
