import os, shutil, pathlib

import pytest

from importlib.resources import files
import subprocess as sproc

import tests  # should be the pytest file tree root

from swmain.infra import tmux

from aorts.cacao_stuff.loop_manager import CacaoConfigReader, CacaoLoopManager


# ConfTest.py FIXTture == ctfixt_
@pytest.fixture(scope='session')
def ctfixt_parse_config(request, tmpdir_factory):

    loop_full_name: str = 'ao3k-nirpyr3k-testonly'

    if hasattr(request, 'loop_full_name'):
        loop_full_name = request.loop_full_name

    confdir = pathlib.Path(
            files(tests) / 'conftestaux' / (loop_full_name + '-conf'))
    targetdir = pathlib.Path(tmpdir_factory.mktemp('AOloop'))

    # Move
    shutil.copytree(confdir, targetdir / confdir.name)

    cfg_reader = CacaoConfigReader(loop_full_name, loop_number=None,
                                   root_all=targetdir)
    # spoof one more terminal
    nir3ktest_fpsCTRL_tmux = tmux.find_or_create(cfg_reader.loop_name +
                                                 '_fpsCTRL')
    nir3ktest_fpsCTRL_tmux.send_keys(
            f'export MILK_SHM_DIR={os.environ["MILK_SHM_DIR"]}')

    # Well now, deploy.
    proc = sproc.Popen(f'cacao-loop-deploy -r {loop_full_name}'.split(),
                       cwd=targetdir)
    proc.wait()

    # So here we have an insane problem with tmuxes... we need to spoof the bashrc in all of them!!
    loop_mgr = CacaoLoopManager('ao3k-nirpyr3k-testonly', None,
                                root_all=targetdir)

    loop_mgr.obtain_tmux_handles()
    for ctrl_tmux, conf_tmux, run_tmux in loop_mgr.tmux_handles.values():
        assert ctrl_tmux is not None
        assert conf_tmux is not None
        assert run_tmux is not None

    yield targetdir

    # Now clean up the whole thing
    loop_mgr.runstop_processes(1.0)
    loop_mgr.confstop_processes(1.0)

    for ctrl_tmux, _, _ in loop_mgr.tmux_handles.values():
        tmux.TMUX_SERVER.kill_session(ctrl_tmux.session_name)

    tmux.TMUX_SERVER.kill_session('nir3ktest_fpsCTRL')
