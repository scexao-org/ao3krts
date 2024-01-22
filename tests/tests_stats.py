from __future__ import annotations

import numpy as np
import time
import random
import multiprocessing

from pyMilk.interfacing.shm import SHM

import pytest  # TODO look at pytest. Right now those tests are valid if we see:
# a - the stats SHMs spinning
# b - the ave SHM going towards 0
# c - the var SHM going towards 1


def _prep_posting_process(shm_name: str = 'test_shm',
                          tsleep: float = 0.001) -> multiprocessing.Process:
    shm = SHM(shm_name,
              ((random.randint(100, 200), random.randint(1, 3)), np.float32))

    def post():
        while True:
            time.sleep(tsleep)  # Will ballpark to ~700 Hz
            shm.set_data(np.random.randn(*shm.shape).astype(np.float32))

    return multiprocessing.Process(target=post)


def test_statisticator() -> None:
    shm_name = 'test_shm'
    proc = _prep_posting_process(shm_name)

    from aorts.rtm_datasource.stats_compute import ShmStatisticator
    stat = ShmStatisticator(shm_name)

    proc.start()

    try:
        stat.test_me_unthreaded()
    except KeyboardInterrupt:
        pass

    proc.kill()


def test_threaded_statisticator() -> None:
    shm_name = 'test_shm'
    proc = _prep_posting_process(shm_name)

    from aorts.rtm_datasource.stats_compute import ThreadedStatisticator
    stat = ThreadedStatisticator(shm_name)

    proc.start()
    stat.start_thread()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stat.stop_thread()

    proc.kill()


def test_threaded_statisticator_pool() -> None:
    shm_names = ['testa', 'testb', 'testc', 'testd']
    tsleeps = [0.001, 0.0014, 0.0021, 0.0011]
    procs = [
            _prep_posting_process(name, tsleep)
            for (name, tsleep) in zip(shm_names, tsleeps)
    ]

    from aorts.rtm_datasource.stats_compute import ThreadStatisticatorPool
    stat_tpool = ThreadStatisticatorPool(shm_names)

    for p in procs:
        p.start()

    stat_tpool.start_threads()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stat_tpool.stop_threads()

    for p in procs:
        p.kill()
