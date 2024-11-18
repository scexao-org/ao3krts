from __future__ import annotations

import numpy as np
import time
from dataclasses import dataclass
import multiprocessing

from pyMilk.interfacing.shm import SHM

import pytest  # TODO look at pytest. Right now those tests are valid if we see:
# a - the stats SHMs spinning
# b - the ave SHM going towards 0
# c - the var SHM going towards 1


@dataclass
class ARGS:
    shm_name: str
    shm_shape: tuple[int, ...]
    t_sleep: float = 0.001


@pytest.fixture
def fixt_shm_posting_process(request):

    # defaults
    prm: list[ARGS] = [ARGS('test_shm', (123, 7))]

    if hasattr(request, 'param'):
        if isinstance(request.param, ARGS):
            prm = [request.param]
        elif isinstance(request.param, list):
            assert all([isinstance(x, ARGS) for x in request.param])
            prm = request.param

    shms = [SHM(p.shm_name, (p.shm_shape, np.float32)) for p in prm]

    def post(shm: SHM, t_sleep: float):
        while True:
            time.sleep(t_sleep)  # Will ballpark to ~700 Hz
            shm.set_data(np.random.randn(*shm.shape).astype(np.float32))

    procs = [
            multiprocessing.Process(target=post, args=(shm, p.t_sleep))
            for p, shm in zip(prm, shms)
    ]
    for proc in procs:
        proc.start()

    yield prm, procs

    for proc in procs:
        proc.kill()
        proc.join()


def test_fixt_prep_shm_posting_process(fixt_shm_posting_process):

    args, procs = fixt_shm_posting_process
    shm = SHM('test_shm')
    assert shm.shape == (123, 7)

    now = time.time()
    assert shm.get_data(True, checkSemAndFlush=True, timeout=0.5) is not None
    assert time.time() - now < 0.1


@pytest.mark.parametrize(
        'fixt_shm_posting_process',
        [
                ARGS('y', (123, 7)),
                ARGS('y', (1, 7)),  # Overwrite size ok?
                ARGS('yads', (14, 237))
        ],
        indirect=True)
def test_statisticator(fixt_shm_posting_process) -> None:
    args, procs = fixt_shm_posting_process

    from aorts.rtm_datasource.stats_compute import ShmStatisticator
    stat = ShmStatisticator(args[0].shm_name)

    stat.test_me_unthreaded(max_it=1000)

    # FIXME test something for real.

    assert True


@pytest.mark.parametrize('fixt_shm_posting_process',
                         [ARGS('y', (123, 7)),
                          ARGS('yads', (14, 237))], indirect=True)
def test_threaded_statisticator(fixt_shm_posting_process) -> None:
    args, proc = fixt_shm_posting_process

    from aorts.rtm_datasource.stats_compute import ThreadedStatisticator
    stat = ThreadedStatisticator(args[0].shm_name)
    stat.synced_compute_and_post_stats()
    stat.start_thread()

    start_time = time.time()

    cnt0 = stat.cnt0  # only exists if stat has done 1st it
    while time.time() - start_time < 1.0:
        time.sleep(0.01)
    stat.stop_thread()

    assert stat.thread is None
    assert stat.cnt0 - cnt0 > 100


@pytest.mark.parametrize('fixt_shm_posting_process',
                         [[ARGS('testa', (123, 7), 0.001)],
                          [
                                  ARGS('testa', (14, 237), 0.00123),
                                  ARGS('testb', (1, 23), 0.01)
                          ],
                          [
                                  ARGS('testa', (1, 2), 0.001),
                                  ARGS('testb', (2, 1), 0.0014),
                                  ARGS('testc', (12, 17), 0.0021),
                                  ARGS('testd', (3, 2, 5), 0.1),
                          ]], indirect=True)
def test_threaded_statisticator_pool(fixt_shm_posting_process) -> None:

    args, _ = fixt_shm_posting_process

    from aorts.rtm_datasource.stats_compute import ThreadStatisticatorPool
    stat_tpool = ThreadStatisticatorPool([arg.shm_name for arg in args])

    stat_tpool.start_threads()
    stat_tpool.stop_threads()
