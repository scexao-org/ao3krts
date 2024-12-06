from __future__ import annotations

import typing as typ

import os
import subprocess as sproc
import time
import re
import glob
import pathlib

import logging

logg = logging.getLogger(__name__)

# Check bindings to swmain for logging. Duh.

from pyMilk.interfacing.fps import FPS, FPSManager, FPSDoesntExistError

from .mfilt import MFilt
from .cacaovars_reader import load_cacao_environment

# TODO I can actually make a big fat test fixture with an entire CACAO loop deployment???

AOLOOP_ROOT = pathlib.Path(os.environ['HOME']) / 'AOloop'


class CacaoConfigReader:

    def __init__(self, loop_full_name: str, loop_number: int | None,
                 root_all: str | pathlib.Path = AOLOOP_ROOT) -> None:

        self.loop_full_name = loop_full_name

        if isinstance(root_all, str):
            root_all = pathlib.Path(root_all)

        self.conf_folder = root_all / f'{self.loop_full_name}-conf'

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

        self.rootdir = root_all / f'{self.loop_name}-rootdir'
        self.rundir = root_all / f'{self.loop_name}-rootdir' / f'{self.loop_name}-rundir'


class CacaoLoopManager(CacaoConfigReader):

    def __init__(self, loop_full_name: str, loop_number: int | None,
                 root_all: str | pathlib.Path = AOLOOP_ROOT) -> None:

        super().__init__(loop_full_name, loop_number, root_all=root_all)

        # FIXME MUST FILTER BY KEYWORD.
        self.fps_ctrl = FPSManager('*', f'aol{self.loop_number}')
        if len(self.fps_ctrl.fps_cache) == 0:
            logg.warning(
                    f"FPSCtrl cache is suspiciously empty for regex {self.fps_ctrl.fps_name_glob}.fps.shm"
            )

    def __str__(self) -> str:
        self.fps_ctrl.rescan_all()
        return '\n'.join([
                'CacaoLoopManager @ cacao_stuff.loop_manager',
                f'{self.loop_full_name:20s} | {self.loop_name:16s} | {self.loop_number}',
                f'conf_folder: {self.conf_folder}',
                f'root_dir:    {self.rootdir}'
        ]) + '\n' + '\n'.join([
                '    ' + fps.__str__()
                for fps in self.fps_ctrl.fps_cache.values()
        ])

    def obtain_tmux_handles(self):
        from swmain.infra import tmux
        self.fps_ctrl.rescan_all()
        self.tmux_handles: dict[str, tuple[tmux.Pane_T, tmux.Pane_T,
                                           tmux.Pane_T]] = {}
        for fps_name in self.fps_ctrl.fps_cache:
            tmux_triplet = (tmux.find(fps_name, window_name='ctrl'),
                            tmux.find(fps_name, window_name='conf'),
                            tmux.find(fps_name, window_name='run'))
            assert all(t is not None
                       for t in tmux_triplet)  # CANNOT do with a "in".
            self.tmux_handles[fps_name] = tmux_triplet  # type: ignore

    @property
    def acquWFS(self) -> FPS | None:
        try:
            return self.fps_ctrl.find_fps(f'acquWFS-{self.loop_number}')
        except FPSDoesntExistError:
            return None

    @property
    def wfs2cmodeval(self) -> FPS | None:
        try:
            return self.fps_ctrl.find_fps(f'wfs2cmodeval-{self.loop_number}')
        except FPSDoesntExistError:
            return None

    @property
    def mfilt(self) -> MFilt | None:
        try:
            return MFilt.smartfps_downcast(
                    self.fps_ctrl.find_fps(f'mfilt-{self.loop_number}'))
        except FPSDoesntExistError:
            return None

    @property
    def mvalC2dm(self) -> FPS | None:
        try:
            return self.fps_ctrl.find_fps(f'mvalC2dm-{self.loop_number}')
        except FPSDoesntExistError:
            return None

    def init_input_symlink(self, sim: bool = False):
        pass

    def confstart_processes(self, timeout_each: float | None = None) -> None:
        self.fps_ctrl.rescan_all()
        for fps in self.fps_ctrl.fps_cache.values():
            fps.conf_start(timeout_each)

    def confstop_processes(self, timeout_each: float | None = None) -> None:
        self.fps_ctrl.rescan_all()
        for fps in self.fps_ctrl.fps_cache.values():
            fps.conf_stop(timeout_each)

    def runstop_processes(self, timeout_each: float | None = None) -> None:
        self.fps_ctrl.rescan_all()
        for fps in self.fps_ctrl.fps_cache.values():
            fps.run_stop(timeout_each)

    '''
    # Not implemented - it's dangerous to just fire everything at once, including mlat and
    # cals and all... makes no sense.
    def runstart_processes(self):
        ...
    def runstop_processes(self):
        ...
    '''

    def runstart_aorun(self) -> None:
        '''
        # TODO
        Use synchronous waits instead
        On a cold start, each process allocates necessary inputs for the next one,
        it could
        take time
        '''
        if self.acquWFS and not self.acquWFS.run_isrunning():
            self.acquWFS.run_start(timeoutsync=3.0)
        if self.wfs2cmodeval and not self.wfs2cmodeval.run_isrunning():
            self.wfs2cmodeval.run_start(timeoutsync=3.0)
        if self.mfilt and not self.mfilt.run_isrunning():
            self.mfilt.run_start(timeoutsync=3.0)
        if self.mvalC2dm and not self.mvalC2dm.run_isrunning():
            self.mvalC2dm.run_start(timeoutsync=3.0)

    def runstop_aorun(self, stop_acqWFS: bool = False) -> None:
        if self.mvalC2dm:
            self.mvalC2dm.run_stop(timeoutsync=1.0)
        if self.mfilt:
            self.mfilt.run_stop(timeoutsync=1.0)
        if self.wfs2cmodeval:
            self.wfs2cmodeval.run_stop(timeoutsync=1.0)

        if self.acquWFS and stop_acqWFS:
            time.sleep(.3)
            self.acquWFS.run_stop()

    def graceful_stop(self, do_runstop: bool) -> None:
        # assume the loop is running
        # perform a graceful fade-out of the mfilt
        # the open the loop, then stop the processes

        if self.mfilt:
            saved_gain = self.mfilt.loopgain
            saved_mult = self.mfilt.loopmult
            self.mfilt.loopgain = 0.0
            self.mfilt.loopmult = 0.98
            time.sleep(1.0)

            self.mfilt.loopON = False
            self.mfilt.loopgain = saved_gain
            self.mfilt.loopmult = saved_mult

        if do_runstop:
            self.runstop_aorun()

    def set_cwd_to_rootdir(self) -> None:
        os.chdir(self.rootdir)

    def exec_in_rootdit(self, command: str) -> None:
        sproc.run(command.split(), cwd=self.rootdir)

    def tui(self) -> None:
        self.exec_in_rootdit('cacao-fpsctrl-TUI')


'''
    A few global functions
'''


def cacao_locate_all_mfilts() -> dict[int, MFilt]:
    fps_ctrl = FPSManager(
            'mfilt-*'
    )  # We should DISCARD any DM we'd get in here, but there should be any.
    return {
            int(fps.get_param('AOloopindex')): MFilt.smartfps_downcast(fps)
            for fps in fps_ctrl.fps_cache.values()
    }


def cacao_locate_mfilt(loop_index: int) -> MFilt:
    return MFilt(f'mfilt-{loop_index}')


def guess_loops() -> list[CacaoLoopManager]:
    '''
    Look for folders in $HOME/AOloop and guess what loops may be hanging around the system.
    '''
    aoloop_folder = pathlib.Path(os.environ['HOME'] + '/AOloop/')
    assert aoloop_folder.is_dir()

    conf_folders = glob.glob(str(aoloop_folder / '*-conf'))
    conf_folders.sort()

    loop_managers: list[CacaoLoopManager] = []
    regex_conf = '(.*)-conf'
    for pathstr in conf_folders:
        fold_name = str(pathlib.Path(pathstr).name)
        match = re.match(regex_conf, fold_name)
        assert match is not None
        loop_full_name = match.groups()[0]
        loop_managers.append(CacaoLoopManager(loop_full_name, None))

    return loop_managers


def cacao_loop_deploy(loop_full_name: str, root_aodir: str |
                      pathlib.Path = os.environ['HOME'] + '/AOloop',
                      delete_logdir: bool = False):
    cfg_reader = CacaoConfigReader(loop_full_name, loop_number=None,
                                   root_all=root_aodir)

    root_aodir = pathlib.Path(root_aodir)
    if delete_logdir:
        cacao_deploy_folder = root_aodir / f'.{cfg_reader.loop_name}.cacaotaskmanager-log'
        import shutil
        shutil.rmtree(cacao_deploy_folder)

    from swmain.infra import tmux
    fpsCTRL_tmux = tmux.find_or_create(cfg_reader.loop_name + '_fpsCTRL')
    # Well now, deploy.
    # The -r is CRITICAL
    proc = sproc.Popen(f'cacao-loop-deploy -r {loop_full_name}'.split(),
                       cwd=root_aodir)
    proc.wait()
