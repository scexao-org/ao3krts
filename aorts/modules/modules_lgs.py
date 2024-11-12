from __future__ import annotations
import typing as typ

import time

from pyMilk.interfacing.shm import SHM
from swmain.infra import tmux
from swmain.infra.rttools import milk_make_rt

from . import base_module_modes as base

RME: typ.TypeAlias = base.RTS_MODULE_ENUM  # Alias
CSE: typ.TypeAlias = base.CONFIG_SUBMODES_ENUM  # Alias
OK = base.OkErrEnum.OK
ERR = base.OkErrEnum.ERR

from .. import config
from ..control.foc_offloader import FocusLGSOffloader


class WTTOffloader_RTSModule:  # implements RTS_MODULE Protocol
    MODULE_NAMETAG: RME = RME.WTTOFF

    @classmethod
    def start_function(cls) -> base.T_Result:
        ...

    @classmethod
    def stop_function(cls) -> base.T_Result:
        ...


class FOCOffloader_RTSModule:  # implements RTS_MODULE_CONFIGURABLE Protocol
    MODULE_NAMETAG: RME = RME.FOCOFF

    CFG_NAMES: list[CSE] = [CSE.OLGS, CSE.NLGS]

    last_requested_mode: CSE | None = None

    @classmethod
    def start_function(cls) -> base.T_Result:

        # Open a control object (ensures the FPS is created)
        ctrl = FocusLGSOffloader(allow_creation=False)

        # Turn computations off for when starting
        ctrl.set_ave_gain(0.0)
        ctrl.disable()

        tmux_foc = tmux.find_or_create('foc_offloader')

        # NEED TO RUN THE MAIN # TODO
        tmux_foc.send_keys("python -m aorts.lgsoffloadermains.focus")

        now = time.time()
        while time.time() - now < 20.0:
            time.sleep(0.1)
            if tmux.find_pane_running_pid(tmux_foc) is None:
                return (ERR,
                        "Focus offloader startup failure (foc_offloader tmux crash)."
                        )
            try:
                ttf_ave_shm = SHM('focoff_ttf_stats')
                ttf_ave_shm.check_sem_trywait()
                return (OK, "Focus offloader started successfully.")
            except:
                pass

        return (ERR,
                "Focus offloader startup failure (no SHM focoff_ttf_starts after 20 seconds)."
                )

    @classmethod
    def stop_function(cls) -> base.T_Result:
        # Open a control object (ensures the FPS)
        # In case the offloader is still running...
        ctrl = FocusLGSOffloader(allow_creation=True)
        ctrl.disable()
        ctrl.reset()  # Reset to avoid runaway integrator somewhere

        tmux_foc = tmux.find('foc_offloader')
        if tmux_foc is None:
            return (ERR, "Focus offloader startup failure (no tmux)")

        tmux.kill_running(tmux_foc)

        if not (tmux.expect_no_pid(tmux_foc, timeout_sec=5)):
            return (ERR,
                    "Focus offloader halt error. Inspect tmux foc_offloader.")

        return (OK, "Focus offloader halted successfully.")

    @classmethod
    def reconfigure(cls, mode: CSE) -> base.T_Result:
        if mode not in cls.CFG_NAMES:
            return (ERR,
                    f'FOCOffloader_RTSModule mode {mode} is invalid. Valid modes are: {cls.CFG_NAMES}'
                    )

        # Ensure the FPS exists by instantiating a controller
        # AND stop existing instance if any.

        # C style error passing gwahahaha
        if (ret := cls.stop_function())[0] == ERR:
            return ret

        ctrl = FocusLGSOffloader(allow_creation=False)
        if mode == CSE.OLGS:
            input_stream = f'aol{config.LINFO_HOAPD_3K.n}_modevalWFS'
        elif mode == CSE.NLGS:
            input_stream = f'aol{config.LINFO_LOAPD_3K.n}_modevalWFS'
        else:
            return (ERR,
                    f'FOCOffloader_RTSModule does not know what to do with mode {mode}'
                    )

        ctrl.set_input_stream(input_stream)

        import os
        if not os.path.isfile(os.environ['MILK_SHM_DIR'] +
                              f'/{input_stream}.im.shm'
                              ):  # I hate this. pymilk should do that for me.
            return (ERR,
                    f'FOCOffloader_RTSModule reconfigure: SHM {input_stream} does not exist.'
                    )

        return (OK, f'FOCOffloader reconfigured mode: {mode}')

    @classmethod
    def configure_and_start(cls, mode: CSE | None = None) -> base.T_Result:
        if mode is None:
            mode = cls.CFG_NAMES[0]

        if (ret := cls.reconfigure(mode))[0] == ERR:
            return ret

        return cls.start_function()
