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

    def post_create_set_defaults(self):
        super().post_create_set_defaults()
        self.loopON = False
        self.loopZERO = False
        self.loopgain = 0.0
        self.loopmult = 1.0
        self.looplimit = 1.0  # Arbitrary
