'''
WIP FILE
'''
from __future__ import annotations

import typing as typ


class CacaoLoopManagerObj:
    '''
        SHOULD BE AT LEAST IN ANOTHER FILE, POSSIBLY IN ANOTHER PACKAGE ENTIRELY.
    '''

    def __init__(self, loop_number: int) -> None:
        self.loop_number = loop_number

    def graceful_stop(self) -> None:
        pass


class RtmControlSupervisor:
    '''
        That's a hairy one... it controls and supervises the initialization

        of the 4 modes?

        Great pre-bundle for the remote control commands tho.
    '''

    def __init__(self) -> None:

        # While the class themselves should not bother too much,
        # We should not forget to manage expectations like conf running, not running, etc,
        self.howfs_loop = CacaoLoopManagerObj(1)
        self.lowfs_loop = CacaoLoopManagerObj(2)
        self.ttoff_loop = CacaoLoopManagerObj(4)

    def stop_all(self):
        '''
        Stop whatever straggling loop processes are going on.
        '''
        self.ttoff_loop.graceful_stop()  # Stop loop, no clear
        # Do we even need to clear processes?
        # The more appropriate way for TT is actually for it to run at all times, but the gain is
        # Multiplied by whoever controls the BIM posting.

        self.howfs_loop.graceful_stop(
        )  # Kill gain, let decay, loopON = OFF, restore gain
        self.lowfs_loop.graceful_stop()  # ?

    def reconfigure_ngs(self):
        self.howfs_loop.reconfigure_matrices(NGS_MATRIX)
        self.howfs_loop.restart_processes()

    def reconfigure_lgsold(self):
        self.reconfigure_lgs(OLD)

    def reconfigure_lgsnew(self):
        self.reconfigure_lgs(NEW)

    def reconfigure_lgs(self):
        self.howfs_loop.reconfigure_matrices(NGS_MATRIX)
        self.howfs_loop.restart_processes()

        self.lowfs_loop.reconfigure_matrices(TTF_MATRIX)
        self.lowfs_loop.restart_processes()

        self.spin_up_defocus_offloader(FROM_LO_OR_FROM_HI)
        self.spin_up_HOWFS_to_WTT_controler

        # Mark ready to close LGS loop. Perform LOWFS NGS acquisition and mark ready for offload.

        def handover_tt():
            lower_mgain_howfs_tt_incrementally
            increase_gain_lowfs_loop_incrementally
            increase_gain_tt_offloader_incrementally

    def reconfigure_ttonly(self):
        pass
