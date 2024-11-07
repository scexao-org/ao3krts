from __future__ import annotations
import typing as typ

from . import base_module_modes as base

from . import modules as m
'''
This list definition makes sure all our modules
actually implement the RTS_MODULE protocol
pyright/pylance would throw errors here otherwise.
'''
MODULE_CLASSES: list[type[base.RTS_MODULE]] = [
        # Hardware
        m.Iiwi_RTSModule,
        m.DAC40_RTSModule,
        m.APD_RTSModule,
        m.PTAPD_RTSModule,
        m.PTDAC_RTSModule,
        m.DM3K_RTSModule,
        m.KWFS_RTSModule,
        # Loops
        m.NIRLOOP_RTSModule,
        m.HOWFSLOOP_RTSModule,
        m.LOWFSLOOP_RTSModule,
        m.KWFSLOOP_RTSModule,
        m.TTOFFLOOP_RTSModule,
        m.PTLOOP_RTSModule,
        # LGS offloaders
]

MODULE_MAPPER: dict[base.RTS_MODULE_ENUM, typ.Type[base.RTS_MODULE]] = {
        klass.MODULE_NAMETAG: klass
        for klass in MODULE_CLASSES
}

if len(MODULE_MAPPER) < len(MODULE_CLASSES):
    inv_mapper = [(klass.__name__, klass.MODULE_NAMETAG)
                  for klass in MODULE_CLASSES]
    raise ValueError('Duplicate RTSModule class key identified?', inv_mapper)
