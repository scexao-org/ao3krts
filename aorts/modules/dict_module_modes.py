from __future__ import annotations
import typing as typ

from . import base_module_modes as base

from . import modules_hw as mh
from . import modules_loops as ml
from . import modules_lgs as mlgs
'''
This list definition makes sure all our modules
actually implement the RTS_MODULE protocol
pyright/pylance would throw errors here otherwise.
'''
MODULE_CLASSES: list[type[base.RTS_MODULE]] = [
        # Hardware
        mh.Iiwi_RTSModule,
        mh.DAC40_RTSModule,
        mh.APD_RTSModule,
        mh.PTDAC_RTSModule,
        mh.DM3K_RTSModule,
        mh.KWFS_RTSModule,
        # Loops
        ml.NIRLOOP_RTSModule,
        ml.HOWFSLOOP_RTSModule,
        ml.LOWFSLOOP_RTSModule,
        ml.KWFSLOOP_RTSModule,
        ml.TTOFFLOOP_RTSModule,
        ml.PTLOOP_RTSModule,
        # LGS offloaders
        mlgs.WTTOffloader_RTSModule,
        mlgs.FOCOffloader_RTSModule,
]

_checker: list[type[base.RTS_MODULE_RECONFIGURABLE]] = [
        #ml.HOWFSLOOP_RTSModule,
        #ml.LOWFSLOOP_RTSModule,
        mlgs.FOCOffloader_RTSModule,
]

MODULE_MAPPER: dict[base.RTS_MODULE_ENUM, typ.Type[base.RTS_MODULE]] = {
        klass.MODULE_NAMETAG: klass
        for klass in MODULE_CLASSES
}

if len(MODULE_MAPPER) < len(MODULE_CLASSES):
    inv_mapper = [(klass.__name__, klass.MODULE_NAMETAG)
                  for klass in MODULE_CLASSES]
    raise ValueError('Duplicate RTSModule class key identified?', inv_mapper)

from . import modes_definitions as md

MODE_CLASSES: list[type[base.RTS_MODE]] = [
        md.NIR3K_RTSMODE,
        md.APDNGS3K_RTSMODE,
        md.OLGS3K_RTSMODE,
        md.NLGS3K_RTSMODE,
        md.PT3K_RTSMODE,
]
MODE_MAPPER: dict[base.RTS_MODE_ENUM, typ.Type[base.RTS_MODE]] = {
        klass.MODE_NAMETAG: klass
        for klass in MODE_CLASSES
}

if len(MODE_MAPPER) < len(MODE_CLASSES):
    inv_mapper = [(klass.__name__, klass.MODE_NAMETAG)
                  for klass in MODE_CLASSES]
    raise ValueError('Duplicate RTSMode class key identified?', inv_mapper)
