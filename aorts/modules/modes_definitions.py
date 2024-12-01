from __future__ import annotations

import typing as typ

from . import modules_hw as mh
from . import modules_loops as ml
from . import modules_lgs as mlgs

from .base_module_modes import RTS_MODULE_ENUM as RMDE, RTS_MODE_ENUM as RME


class NIR3K_RTSMODE:
    MODE_NAMETAG: RME = RME.NIR3K

    NOPE_MODULES = [
            RMDE.PT_DAC,
            RMDE.HOLOOP,
            RMDE.LOLOOP,
            RMDE.PTLOOP,
            RMDE.KWFSLOOP,
            RMDE.WTTOFF,
    ]
    REQ_MODULES = [RMDE.IIWI, RMDE.DAC40, RMDE.DM3K, RMDE.TTOFFL, RMDE.NIRLOOP]


class APDNGS3K_RTSMODE:
    MODE_NAMETAG: RME = RME.APDNGS3K

    NOPE_MODULES = [
            RMDE.PT_DAC,
            RMDE.LOLOOP,
            RMDE.PTLOOP,
            RMDE.KWFSLOOP,
            RMDE.NIRLOOP,
            RMDE.WTTOFF,
    ]
    REQ_MODULES = [RMDE.APD, RMDE.DAC40, RMDE.DM3K, RMDE.TTOFFL, RMDE.HOLOOP]


class PT3K_RTSMODE:
    MODE_NAMETAG: RME = RME.APDNGS3K

    NOPE_MODULES = [
            RMDE.DAC40,
            RMDE.LOLOOP,
            RMDE.KWFSLOOP,
            RMDE.NIRLOOP,
            RMDE.HOLOOP,
            RMDE.TTOFFL,
            RMDE.WTTOFF,
    ]
    REQ_MODULES = [
            RMDE.PT_DAC,
            RMDE.PTLOOP,
            RMDE.APD,
            RMDE.DM3K,
    ]


class OLGS3K_RTSMODE:
    MODE_NAMETAG: RME = RME.OLGS3K

    NOPE_MODULES = [
            RMDE.PT_DAC,
            RMDE.PTLOOP,
            RMDE.KWFSLOOP,
            RMDE.NIRLOOP,
    ]
    REQ_MODULES = [
            RMDE.APD,
            RMDE.DAC40,
            RMDE.DM3K,
            RMDE.TTOFFL,
            RMDE.
            HOLOOP,  # Reconfigured for LGS # Flip the matrix -- and automatically apply HTT HDF 0.
            RMDE.LOLOOP,  # Have to respect LTT and LDF
            RMDE.
            WTTOFF,  # Have to respect WTT -- need to build LOWFS -> WTT control matrix.
    ]


class NLGS3K_RTSMODE:
    MODE_NAMETAG: RME = RME.OLGS3K

    NOPE_MODULES = [
            RMDE.PT_DAC,
            RMDE.PTLOOP,
            RMDE.KWFSLOOP,
            RMDE.NIRLOOP,
    ]
    REQ_MODULES = [
            RMDE.APD,
            RMDE.DAC40,
            RMDE.DM3K,
            RMDE.TTOFFL,
            RMDE.
            HOLOOP,  # Reconfigured for LGS # Flip the matrix -- and automatically apply ???
            RMDE.LOLOOP,  # Have to respect LTT and LDF
            RMDE.
            WTTOFF,  # Have to respect WTT -- need to build LOWFS -> WTT control matrix.
    ]
