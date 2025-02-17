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

from ..control.wtt_offloader import WTTOffloaderFPS

WTT_TO_NGSMODE_MATRIX = np.array([[-0.3, -0.3], [-0.3, +0.3]], dtype=np.float32)
NGSMODEVAL_TO_WTT_MATRIX = np.linalg.inv(WTT_TO_NGSMODE_MATRIX)

WTT_TO_LGSMODE_MATRIX = np.array([[+0.3, +0.3], [+0.3, -0.3]], dtype=np.float32)
LGSMODEVAL_TO_WTT_MATRIX = np.linalg.inv(WTT_TO_LGSMODE_MATRIX)


@click.command('main_wtt_offloader')
@click.argument('fps_name', type=str, default='wtt_offl')
def main_wtt_offloader(fps_name: str = 'wtt_offl'):

    # For logging
    init_logger_autoname()

    # For badsystemd
    auto_register_to_watchers('WTTOFFL', 'Focus offloader')

    # Expect custom FPS
    fps = WTTOffloaderFPS(fps_name)

    # Parse correct mode / input from FPS
    # Initialize a few things

    shm_input = SHM(fps.in_stream)
    shm_output = SHM('wtt_value_float')
    shm_output_antiwindup = SHM('wtt_telemetry')

    last_print_time = time.time()
    last_data_time = time.time()

    while True:

        if (time.time() - last_print_time) > 5.0:
            print("I'm alive!!")
            print("Here's an FPS dump:")
            for k in fps.key_types:
                print(f'{k:<12}:         {fps[k]:>20}')
            print("--" * 12)

            last_print_time = time.time()

        if fps.loopZERO:
            fps.out_tip = 5.0
            fps.out_til = 5.0
            fps.loopZERO = False

        if not fps.loopON:
            time.sleep(.01)  # Relieve CPU
            continue

        buffer = shm_input.get_data(True, timeout=0.1,
                                    return_none_on_timeout=True)
        if buffer is None:
            continue

        tip, til = LGSMODEVAL_TO_WTT_MATRIX @ buffer[:2]

        frate_gain = 0.001

        _now = time.time()
        interval = _now - last_data_time
        last_data_time = _now

        # Integrator
        # output = shm_output_antiwindup.get_data() # change to shm_output by YO 2025/02/16
        output = shm_output.get_data()

        out_tip, out_til = output[0], output[1]

        out_tip = out_tip * fps.loopmult + tip * fps.loopgain
        out_til = out_til * fps.loopmult + til * fps.loopgain

        # Remember to offset by 5 because this is WTT!!!
        out_tip = np.clip(out_tip, -fps.looplimit, fps.looplimit)
        out_til = np.clip(out_til, -fps.looplimit, fps.looplimit)

        fps.out_tip, fps.out_til = out_tip, out_til
        fps.m_frate = fps.m_frate * (1 - frate_gain) + frate_gain / interval

        shm_output.set_data(np.array([out_tip, out_til], dtype=np.float32))

        # exit cleanly on keyboard interrupt (atexit?)


if __name__ == '__main__':
    main_wtt_offloader()
