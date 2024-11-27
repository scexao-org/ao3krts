import os

from aorts.cacao_stuff.loop_manager import CacaoLoopManager


def test_cacaoconfig_fixt(ctfixt_parse_config):

    import glob
    files = glob.glob('/milk/shm/*')
    assert len(files) == 0

    loop_mgr = CacaoLoopManager('ao3k-nirpyr3k-testonly', None,
                                root_all=ctfixt_parse_config)

    loop_mgr.fps_ctrl.rescan_all()
    loop_mgr.confstop_processes(5.0)
    assert all([
            not f.conf_isrunning()
            for f in loop_mgr.fps_ctrl.fps_cache.values()
    ])
    loop_mgr.confstart_processes(5.0)
    assert all([
            f.conf_isrunning() for f in loop_mgr.fps_ctrl.fps_cache.values()
    ])
    loop_mgr.confstop_processes(5.0)
    assert all([
            not f.conf_isrunning()
            for f in loop_mgr.fps_ctrl.fps_cache.values()
    ])

    assert str(loop_mgr.rootdir).startswith('/tmp/pytest')
