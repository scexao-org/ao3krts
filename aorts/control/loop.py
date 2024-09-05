from __future__ import annotations

import typing as typ

import os
import time
import logging

logg = logging.getLogger(__name__)

from ..cacao_stuff.loop_manager import CacaoLoopManager
from .. import config


class AO3kNIRLoopObject:
    '''
    Loop manager object for loop on / loop off in NIR mode
    '''

    def __init__(self) -> None:
        self.nir_loop = CacaoLoopManager(*config.LINFO_IRPYR_3K)
        self.tt_loop = CacaoLoopManager(*config.LINFO_3KTTOFFLOAD)

        self.nir_loop.confstart_processes()  # start ALL confs
        self.nir_loop.runstart_aorun()  # Start the AO 4 processes

        self.tt_loop.confstart_processes()  # start ALL confs
        self.tt_loop.runstart_aorun()  # Start the AO 4 processes

    def loop_open(self) -> None:
        self.tt_loop.mfilt.loop_open()
        self.nir_loop.mfilt.loop_open()

    def loop_close(self) -> None:
        self.nir_loop.mfilt.loop_zero()
        self.tt_loop.mfilt.loop_zero()
        self.nir_loop.mfilt.loop_close()
        self.tt_loop.mfilt.loop_close()

    def set_dmgain(self, gain: float) -> None:
        self.nir_loop.mfilt.set_gain(gain)

    def set_ttgain(self, gain: float) -> None:
        self.tt_loop.mfilt.set_gain(gain)
