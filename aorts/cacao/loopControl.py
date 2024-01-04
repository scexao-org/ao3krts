from __future__ import annotations

import time

import logging
# Check bindings to swmain for logging.

import typing as typ

from pyMilk.interfacing.fps import FPS, FPSManager


def cacao_locate_all_mfilts() -> list[FPS]:
    pass


def cacao_locate_mfilt(loop_index: int) -> FPS:
    pass


def cacao_open_one_loop(clean_decay: bool = True) -> None:
    cacao_prep_open_one_loop()
    time.sleep(5.0)
    cacao_finalize_open_one_loop()


def cacao_prep_open_one_loop():
    pass


def cacao_finalize_open_one_loop():
    pass


def cacao_open_all_loops(clean_decay: bool = True) -> None:
    # Scan mfilt FPS
    # Save gain and leak
    # Set gain to 0 and leak to appropriate value (from framerate?) 0.995
    # Wait
    # Send dmzero to mfilt
    # runstop mfilt
    #

    mfilts = cacao_locate_all_mfilts()
