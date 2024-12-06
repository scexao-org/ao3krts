from __future__ import annotations

import typing as typ

from . import modules_hw as mh
from . import modules_loops as ml
from . import modules_lgs as mlgs

from .base_module_modes import RTS_MODULE_ENUM as ModuEn, RTS_MODE_ENUM as ModeEn


class NIR3K_RTSMODE:
    MODE_NAMETAG: ModeEn = ModeEn.NIR3K

    NOPE_MODULES = [
            ModuEn.PT_DAC,
            ModuEn.HOLOOP,
            ModuEn.LOLOOP,
            ModuEn.PTLOOP,
            ModuEn.KWFSLOOP,
            ModuEn.WTTOFF,
    ]
    REQ_MODULES = [
            ModuEn.IIWI, ModuEn.DAC40, ModuEn.DM3K, ModuEn.TTOFFL,
            ModuEn.NIRLOOP
    ]


class APDNGS3K_RTSMODE:
    MODE_NAMETAG: ModeEn = ModeEn.NGS3K

    NOPE_MODULES = [
            ModuEn.PT_DAC,
            ModuEn.LOLOOP,
            ModuEn.PTLOOP,
            ModuEn.KWFSLOOP,
            ModuEn.NIRLOOP,
            ModuEn.WTTOFF,
    ]
    REQ_MODULES = [
            ModuEn.APD, ModuEn.DAC40, ModuEn.DM3K, ModuEn.TTOFFL, ModuEn.HOLOOP
    ]


class PT3K_RTSMODE:
    MODE_NAMETAG: ModeEn = ModeEn.PT3K

    NOPE_MODULES = [
            ModuEn.DAC40,
            ModuEn.LOLOOP,
            ModuEn.KWFSLOOP,
            ModuEn.NIRLOOP,
            ModuEn.HOLOOP,
            ModuEn.TTOFFL,
            ModuEn.WTTOFF,
    ]
    REQ_MODULES = [
            ModuEn.PT_DAC,
            ModuEn.PTLOOP,
            ModuEn.APD,
            ModuEn.DM3K,
    ]


class OLGS3K_RTSMODE:
    MODE_NAMETAG: ModeEn = ModeEn.OLGS3K

    NOPE_MODULES = [
            ModuEn.PT_DAC,
            ModuEn.PTLOOP,
            ModuEn.KWFSLOOP,
            ModuEn.NIRLOOP,
    ]
    REQ_MODULES = [
            ModuEn.APD,
            ModuEn.DAC40,
            ModuEn.DM3K,
            ModuEn.TTOFFL,
            ModuEn.
            HOLOOP,  # Reconfigured for LGS # Flip the matrix -- and automatically apply HTT HDF 0.
            ModuEn.LOLOOP,  # Have to respect LTT and LDF
            ModuEn.
            WTTOFF,  # Have to respect WTT -- need to build LOWFS -> WTT control matrix.
    ]


class NLGS3K_RTSMODE:
    MODE_NAMETAG: ModeEn = ModeEn.NLGS3K

    NOPE_MODULES = [
            ModuEn.PT_DAC,
            ModuEn.PTLOOP,
            ModuEn.KWFSLOOP,
            ModuEn.NIRLOOP,
    ]
    REQ_MODULES = [
            ModuEn.APD,
            ModuEn.DAC40,
            ModuEn.DM3K,
            ModuEn.TTOFFL,
            ModuEn.
            HOLOOP,  # Reconfigured for LGS # Flip the matrix -- and automatically apply ???
            ModuEn.LOLOOP,  # Have to respect LTT and LDF
            ModuEn.
            WTTOFF,  # Have to respect WTT -- need to build LOWFS -> WTT control matrix.
    ]
