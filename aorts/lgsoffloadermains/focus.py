from __future__ import annotations

import typing as typ

import time
import click
import numpy as np

import logging

logg = logging.getLogger(__name__)

from swmain.infra.logger import init_logger_autoname
from swmain.infra.badsystemd.aux import auto_register_to_watchers

from pyMilk.interfacing.shm import SHM

from ..control.foc_offloader import FocusLGSOffloaderFPS


@click.command('main_foc_offloader')
def main_foc_offloader(fps_name: str = 'foc_offl'):

    # For logging
    init_logger_autoname()

    # For badsystemd
    auto_register_to_watchers('FOFFL', 'Focus offloader')

    # Expect custom FPS
    fps = FocusLGSOffloaderFPS(fps_name)

    # Parse correct mode / input from FPS
    # Initialize a few things

    shm_input = SHM(fps.in_stream)

    shm_output = SHM('focoff_ttf_stats', np.zeros(3, np.float32))

    last_print_time = time.time()
    last_data_time = time.time()

    while True:

        if (time.time() - last_print_time) > 4.0:
            print("I'm alive!!")
            print("Here's an FPS dump:")
            for k in fps.key_types:
                print(f'{k:<12}:         {fps[k]:>20}')
            print("--" * 12)

            last_print_time = time.time()

        if fps.reset:
            fps.av_tip = 0.0
            fps.av_tilt = 0.0
            fps.av_focus = 0.0
            fps.reset = False

        if not fps['on_off']:
            time.sleep(.01)  # Relieve CPU
            continue

        # Re-get per-loop FPS parameters.
        # WHAT is needed??? not much. We're not even in charge of the ADF gain.

        # compute HDF or LDF stats
        # post that number... somewhere????
        # probably FPS output + SHM is the best choice.

        tip, tilt, focus = np.random.randn(3) * 0.0 + 4

        frate_gain = 0.001

        _now = time.time()
        interval = _now - last_data_time
        last_data_time = _now

        g = fps.gain
        fps.av_tip = fps.av_tip * (1 - g) + tip * g
        fps.av_tilt = fps.av_tilt * (1 - g) + tilt * g
        fps.av_focus = fps.av_focus * (1 - g) + focus * g

        fps.m_frate = fps.m_frate * (1 - frate_gain) + frate_gain / interval

        # exit cleanly on keyboard interrupt (atexit?)


if __name__ == '__main__':
    main_foc_offloader()
