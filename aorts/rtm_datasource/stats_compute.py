from __future__ import annotations

import typing as typ

import threading
import time

import numpy as np

from pyMilk.interfacing.shm import SHM
from pyMilk.errors import AutoRelinkError


class ShmStatisticator:
    # Todo migrate straight to pyMilk?
    '''
        Computes variance and mean with autoregressive filters
        Extremely not thread safe

        Takes in <shm_name> and posts mean and variance
        to <shm_name>_sa and <shm_name>_sv
    '''

    def __init__(self, shm_name: str,
                 allow_autorelink_error: bool = False) -> None:
        self.shm_name = shm_name
        self.allow_autorelink_error = allow_autorelink_error

        self._init_inners()

    def _init_inners(self) -> None:
        # Autosqueeze is False and using shape_c to conserve
        # singleton dims
        self.shm = SHM(self.shm_name, symcode=0, autoSqueeze=False)
        sz, tp = self.shm.shape_c, self.shm.nptype

        # Create SHMs for stats.
        # USE _mean and _var
        # THERE is a name conflict with CACAO with _ave, _rms
        self.shm_ave = SHM(self.shm_name + '_mean', (sz, np.float32), symcode=0)
        self.shm_var = SHM(self.shm_name + '_var', (sz, np.float32), symcode=0)

        # Straight memory pointers to the SHM
        self.data_ave_ptr = self.shm_ave.get_data(copy=False)
        self.data_var_ptr = self.shm_var.get_data(copy=False)

        self.time_constant_stats = 0.2  # seconds
        self.prev_t_update = time.time()
        self.new_t_update = time.time()

    def compute_and_post_stats(self) -> None:
        # Adaptive gain with time interval
        gain = max(
                min((self.new_t_update - self.prev_t_update) /
                    self.time_constant_stats, 1.0), 0.0)
        self.prev_t_update = self.new_t_update

        # In place ops on the pointers
        self.data_ave_ptr += gain * self.data_ptr - gain * self.data_ave_ptr
        self.data_var_ptr += gain * (self.data_ptr**2 - self.data_ave_ptr**
                                     2) - gain * self.data_var_ptr

        self.shm_ave.repost()
        self.shm_var.repost()

    def _get_data_and_raise_aptly(self) -> np.ndarray | None:
        '''
            Helper function to handle or raise autorelink errors
            If the underlying SHM has changed size or data type
        '''
        try:
            return self.shm.get_data(True, timeout=0.05, checkSemAndFlush=False,
                                     copy=False, return_none_on_timeout=True)
        except AutoRelinkError as err:
            if not self.allow_autorelink_error:
                raise
            self._init_inners()  # Re-init buffers and counter and everything.
            return self.shm.get_data(True, timeout=0.05, checkSemAndFlush=False,
                                     copy=False, return_none_on_timeout=True)

        # If any other error, we raise anyway

    def synced_compute_and_post_stats(self) -> None:
        get_data = self._get_data_and_raise_aptly()

        if get_data is None:
            return
        else:
            self.data_ptr = get_data

        self.cnt0 = self.shm.IMAGE.md.cnt0
        self.new_t_update = time.time()

        # TODO compute some stats if missed frames
        # ALSO shouldn't post if we timed out.

        self.compute_and_post_stats()

    def test_me_unthreaded(self, max_it: int | None = None):
        if max_it is None:
            while True:
                self.shm._attempt_autorelink_if_needed()
                self.synced_compute_and_post_stats()
        else:
            for _ in range(max_it):
                self.synced_compute_and_post_stats()


class ThreadedStatisticator(ShmStatisticator):

    def __init__(self, shm_name: str,
                 allow_autorelink_error: bool = False) -> None:
        super().__init__(shm_name, allow_autorelink_error)

        self.thread: threading.Thread | None = None
        self.event: threading.Event | None = None

    def start_thread(self) -> None:
        self.event = threading.Event()
        assert self.thread is None

        self.thread = threading.Thread(target=self.run_thread_with_boilerplate)
        self.thread.start()

    def stop_thread(self) -> None:
        if self.thread is None:
            return

        assert self.event is not None

        if self.thread is not None:
            self.event.set()
            self.thread.join()
            self.thread = None

    def run_thread_with_boilerplate(self) -> None:
        assert self.event is not None

        while True:
            if self.event.is_set():
                break
            self.run_thread_loopcore()

    def run_thread_loopcore(self) -> None:
        self.synced_compute_and_post_stats()


class ThreadStatisticatorPool:

    def __init__(self, names: typ.Sequence[str],
                 allow_autorelink_error: bool = False) -> None:
        self.statobjs = [
                ThreadedStatisticator(name, allow_autorelink_error)
                for name in names
        ]

    def start_threads(self):
        for statobj in self.statobjs:
            statobj.start_thread()

    def stop_threads(self):
        for statobj in self.statobjs:
            statobj.stop_thread()

    # We'll probs want much much more housekeeping here.


import click


@click.command('run_stats_pool')
@click.option('-r', '--size_change_allowed', is_flag=True)
@click.argument('names', nargs=-1)
def start_pool(names: typ.Sequence[str], size_change_allowed: bool):

    from swmain.infra.logger import init_logger_autoname
    init_logger_autoname()
    import logging

    logg = logging.getLogger(__name__)

    if len(names) == 0:
        logg.error('0 SHM names passed to thread pool statisticator.')
        return

    try:
        tpool = ThreadStatisticatorPool(
                names, allow_autorelink_error=size_change_allowed)
        tpool.start_threads()
        while True:
            time.sleep(1.0)  # Check on threads!
    except KeyboardInterrupt:
        pass
    finally:
        tpool.stop_threads()


if __name__ == '__main__':
    '''
        This main is actually used by the APD ctrl from camstack.
        FIXME we'll probably move this to pyMilk of swmain
        as it is a very generic tool.

        Currently it's used straight as python -m aorts.rtm_datasource.stats_compute <args...>
        and there is no configured entrypoint.
    '''
    start_pool()
