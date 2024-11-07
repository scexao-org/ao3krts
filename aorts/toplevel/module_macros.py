from __future__ import annotations

import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux
from swmain.infra.rttools import milk_make_rt

from . import base_module_modes as base
from .. import config

from ..cacao_stuff.loop_manager import CacaoLoopManager

from swmain.network.pyroclient import connect_aorts
from scxconf import pyrokeys

OK = base.MacroRetcode.OK
ERR = base.MacroRetcode.ERR


def general_startup():
    '''
        Cover what's in rts_start.sh

        But be smarter about it.

        FPDP_reset: yes
        APD acq: not in PT mode
        cacao-loop-deploys: yes
        iiwi acq: yes
        Miscellany SHMs for legacy g2if: yes
        g2if: yes but it needs smarts.
    '''
    pass
