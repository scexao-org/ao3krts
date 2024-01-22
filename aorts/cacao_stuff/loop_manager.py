from __future__ import annotations

import os
import time
import re
import glob
import pathlib

import logging
# Check bindings to swmain for logging. Duh.

import typing as typ

from pyMilk.interfacing.fps import FPS, FPSManager

from .cacaovars_reader import load_cacao_environment


class CacaoLoopManager:

    def __init__(self, loop_full_name: str, loop_number: int | None) -> None:

        self.loop_full_name = loop_full_name

        self.conf_folder = pathlib.Path(
                os.environ['HOME']) / 'AOloop' / f'{self.loop_full_name}-conf'

        self.cacao_environment = load_cacao_environment(self.conf_folder /
                                                        'cacaovars.bash')
        # Sanity check
        if loop_number is None:
            self.loop_number = int(self.cacao_environment['CACAO_LOOPNUMBER'])
        else:
            self.loop_number = loop_number
            assert int(self.cacao_environment['CACAO_LOOPNUMBER']) ==\
                       self.loop_number

        self.loop_name = self.cacao_environment['CACAO_LOOPNAME']

        self.rootdir = pathlib.Path(
                os.environ['HOME']) / 'AOloop' / f'{self.loop_name}-rootdir'

        self.fps_ctrl = FPSManager(
                f'*-{loop_number}')  # We should DISCARD any DM we'd get in here
        assert len(self.fps_ctrl.fps_cache) > 0,\
            f"FPSCtrl cache is suspiciously empty for regex {self.fps_ctrl.fps_name_glob}.fps.shm"

    def __str__(self) -> str:
        self.fps_ctrl.rescan_all()
        return '\n'.join([
                'CacaoLoopManager @ cacao_stuff.loop_manager',
                f'loop_full_name: {self.loop_full_name}',
                f'loop_name: {self.loop_name} | loop_number: {self.loop_number}',
                f'conf_folder: {self.conf_folder} | root_dir: {self.rootdir}'
        ]) + '\n' + '\n'.join(
                ['    ' + fps.__str__() for fps in self.fps_ctrl.fps_cache])

    @property
    def acquWFS(self) -> FPS:
        return self.fps_ctrl.find_fps(f'acquWFS-{self.loop_number}')

    @property
    def wfs2cmodeval(self) -> FPS:
        return self.fps_ctrl.find_fps(f'wfs2cmodeval-{self.loop_number}')

    @property
    def mfilt(self) -> FPS:
        return self.fps_ctrl.find_fps(f'mfilt-{self.loop_number}')

    @property
    def mvalC2dm(self) -> FPS:
        return self.fps_ctrl.find_fps(f'mvalC2dm-{self.loop_number}')

    def init_input_symlink(self, sim: bool = False):
        pass

    def confstart_processes(self) -> bool:
        ...

    def confstop_processes(self) -> bool:
        ...

    def runstart_processes(self) -> bool:
        ...

    def runstop_processes(self) -> bool:
        ...

    def graceful_stop(self, do_runstop: bool) -> None:
        # assume the loop is running
        # perform a graceful fade-out of the mfilt
        # the open the loop, then stop the processes

        if do_runstop:
            self.runstart_processes()


def cacao_locate_all_mfilts() -> dict[int, FPS]:
    ...


def cacao_locate_mfilt(loop_index: int) -> FPS:
    ...


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


def guess_loops() -> list[CacaoLoopManager]:
    aoloop_folder = pathlib.Path(os.environ['HOME'] + '/AOloop/')
    assert aoloop_folder.is_dir()

    conf_folders = glob.glob(str(aoloop_folder / '*-conf'))
    conf_folders.sort()

    loop_managers: list[CacaoLoopManager] = []
    regex_conf = '(.*)-conf'
    for pathstr in conf_folders:
        fold_name = str(pathlib.Path(pathstr).name)
        loop_full_name = re.match(regex_conf, fold_name).group()
        loop_managers.append(CacaoLoopManager(loop_full_name, None))

    return loop_managers
