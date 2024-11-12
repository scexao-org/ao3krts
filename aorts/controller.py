'''
WIP FILE
'''
from __future__ import annotations

import typing as typ

import enum

from .cacao_stuff.loop_manager import CacaoLoopManager

from . import config
"""

class TOPLEVEL_MODE(enum.Enum):
    UNKNOWN = 'UNKNOWN'
    OFF = 'OFF'
    IRWFS = 'IRWFS'
    NGS_APD = 'NGS_APD'
    LGS_LOWFS_TO_AU1 = 'OLD_LGS'
    LGS_HOWFS_TO_AU1 = 'NEW_LGS'
    TT_ONLY_LOWFS = 'TT_ONLY'

class LOOP_TAG(enum.Enum):
    HOWFS = 'HOWFS'
    LOWFS = 'LOWFS'
    IRPYR = 'IRPYR'
    NLCWFS = 'NLCWFS'
    TTOFFL = 'TTOFFLOAD'



class RtmControlSupervisorBIM188:
    '''
        That's a hairy one... it controls and supervises the initialization

        of the 4 modes?

        Great pre-bundle for the remote control commands tho.
    '''

    def __init__(self) -> None:

        # While the class themselves should not bother too much,
        # We should not forget to manage expectations like conf running, not running, etc,
        self.howfs_loop = CacaoLoopManager(*config.LINFO_HOAPD_BIM188)
        self.lowfs_loop = CacaoLoopManager(*config.LINFO_LOAPD_BIM188)
        self.irpyr_loop = CacaoLoopManager(*config.LINFO_IRPYR_BIM188)
        self.ttoff_loop = CacaoLoopManager(*config.LINFO_BIM2TTOFFLOAD)
        # TODO: nlCWFS

        self.all_loops = {
                LOOP_TAG.HOWFS : self.howfs_loop,
                LOOP_TAG.LOWFS : self.lowfs_loop,
                LOOP_TAG.TTOFFL : self.ttoff_loop,
                LOOP_TAG.IRPYR : self.irpyr_loop,
        }

    def stop_all(self):
        '''
        Stop whatever straggling loop processes are going on.
        '''
        self.ttoff_loop.graceful_stop(reset=False, decay=...)  # Stop loop, no clear
        # Do we even need to clear processes?
        # The more appropriate way for TT is actually for it to run at all times, but the gain is
        # Multiplied by whoever controls the BIM posting.

        # Kill gain, let decay, loopON = OFF, restore gain
        self.howfs_loop.graceful_stop()

        self.lowfs_loop.graceful_stop()  # ?

    def reconfigure_some_mode(self, mode: TOPLEVEL_MODE) -> None:
        match mode:
            case TOPLEVEL_MODE.IRWFS:
                self.reconfigure_irwfs()
            case TOPLEVEL_MODE.NGS_APD:
                self.reconfigure_ngs()
            case TOPLEVEL_MODE.LGS_HOWFS_TO_AU1:
                self.reconfigure_lgs_new()
            case TOPLEVEL_MODE.LGS_LOWFS_TO_AU1:
                self.reconfigure_lgs_old()
            case TOPLEVEL_MODE.TT_ONLY_LOWFS:
                self.reconfigure_ttonly()
            case _:
                raise ValueError('Invalid argument mode to reconfigure_some_mode')

    def reconfigure_irwfs(self):
        ...

    def reconfigure_ngs(self):
        self.howfs_loop.reconfigure_matrices(NGS_MATRIX)
        self.howfs_loop.restart_processes()

    def reconfigure_lgs_old(self):
        self.reconfigure_lgs(OLD)

    def reconfigure_lgs_new(self):
        self.reconfigure_lgs(NEW)

    def reconfigure_lgs(self):
        self.howfs_loop.reconfigure_matrices(NGS_MATRIX)
        self.howfs_loop.restart_processes()

        self.lowfs_loop.reconfigure_matrices(TTF_MATRIX)
        self.lowfs_loop.restart_processes()

        self.spin_up_defocus_offloader(FROM_LO_OR_FROM_HI)
        self.spin_up_HOWFS_to_WTT_controler

    def reconfigure_ttonly(self):
        ...


    # Mark ready to close LGS loop. Perform LOWFS NGS acquisition and mark ready for offload.
    def handover_tt():
        lower_mgain_howfs_tt_incrementally
        increase_gain_lowfs_loop_incrementally
        increase_gain_tt_offloader_incrementally

"""
