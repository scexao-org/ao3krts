'''
This file is basic sanity to make sure the implemented fixtures
in
    - conftest.py
    - conftestaux/*.py
actually do their job.
'''
import os
import Pyro4

from swmain.network.pyroclient import connect_generic

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer


def test_pyrons(ctfixt_server_pair):
    # This should not error
    ns = Pyro4.locateNS(host='localhost', port=63445)
    # We can play by opening a proxy to itself
    proxy_ns = connect_generic('Pyro.NameServer', 'localhost', 63445)

    assert proxy_ns.ping() is None

    objs = proxy_ns.list()
    assert isinstance(objs, dict)
    assert 'Pyro.NameServer' in objs

    uri_tail = lambda x: x.split(':', maxsplit=1)[1]  # split after the first :
    # URIs should be identical except for PYRO: / PYRONAME:
    assert uri_tail(proxy_ns._pyroUri.asString()) == uri_tail(
            objs['Pyro.NameServer'])


def test_rts_server_pair_works(ctfixt_server_pair):
    pyro_server, tcp_server = ctfixt_server_pair

    assert isinstance(pyro_server, PyroServer)
    assert isinstance(tcp_server, ObjectDispatchingServer)


def test_smartfps_in_server(ctfixt_server_w_smartfps):

    ps, ts = ctfixt_server_w_smartfps
    assert 'FPS' in ps.currentNames
    assert 'fps' in ts.registered_objects

    fps_obj = ps.get_device_by_name('FPS')

    # No errors
    fps_proxy = connect_generic('FPS', *ps.nsAddress)

    assert fps_proxy.looplimit == 0.0
    fps_obj.looplimit = 1.0
    assert fps_obj.looplimit == 1.0
    assert fps_proxy.looplimit == 1.0


def test_smartfps_not_in_server(ctfixt_server_pair):
    '''
    Testing that
        ctfixt_server_pair
    does not contain a 'fps' object
    '''
    ps, ts = ctfixt_server_pair
    assert 'FPS' not in ps.currentNames
    assert 'fps' not in ts.registered_objects


def test_milk_shm_dir_fixture():
    # fixture from milk.py and is autouse.
    MILK_SHM_DIR_SPOOF = '/tmp/milk_shm_dir_pytest'

    assert os.path.isdir(MILK_SHM_DIR_SPOOF)
    assert os.environ['MILK_SHM_DIR'] == MILK_SHM_DIR_SPOOF


def test_cwd_to_temp_fixture():
    cwd = os.getcwd()

    assert cwd.startswith('/tmp')
    # last dir made by the fixture...
    # if other fixtures change cwd further, they should also revert and also not be autouse.
    assert cwd.endswith('pytest_dont_use_for_anything0')
