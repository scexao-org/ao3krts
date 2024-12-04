from __future__ import annotations

import typing as typ

import os
import time
import logging

logg = logging.getLogger(__name__)

from ..cacao_stuff.loop_manager import CacaoLoopManager
from .. import config


class AO3kNIRLoopControllerObject:
    '''
    Loop manager object for loop on / loop off in NIR mode

    This is really the binding for the loop on / off control from gen2.
    '''

    def __init__(self) -> None:
        self.nir_loop = CacaoLoopManager(*config.LINFO_IRPYR_3K)
        self.tt_loop = CacaoLoopManager(*config.LINFO_3KTTOFFLOAD)

        self.nir_loop.confstart_processes()  # start ALL confs
        self.nir_loop.runstart_aorun()  # Start the AO 4 processes

        self.tt_loop.confstart_processes()  # start ALL confs
        self.tt_loop.runstart_aorun()  # Start the AO 4 processes

    def loop_open(self) -> None:
        self.tt_loop.mfilt.loopON = False
        self.nir_loop.mfilt.loopON = False

    def loop_close(self) -> None:
        self.nir_loop.mfilt.loopZERO = True
        self.tt_loop.mfilt.loopZERO = True
        self.nir_loop.mfilt.loopON = True
        self.tt_loop.mfilt.loopON = True

    def set_dmgain(self, gain: float) -> None:
        self.nir_loop.mfilt.loopgain = gain

    def set_ttgain(self, gain: float) -> None:
        self.tt_loop.mfilt.loopgain = gain
