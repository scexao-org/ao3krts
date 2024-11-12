import pytest

import subprocess as sproc
import time

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer

from aorts.server.test_command import ActualInterestingTestObject

from scxconf import PYRONSAO_PORT


def test_rts_server_pair_works(ctfixt_server_pair):
    pyro_server, tcp_server = ctfixt_server_pair

    assert isinstance(pyro_server, PyroServer)
    assert isinstance(tcp_server, ObjectDispatchingServer)


def test_smartfps_in_pyroserver(ctfixt_server_w_smartfps):
    pyro_server, tcp_server = ctfixt_server_w_smartfps

    ps, ts = ctfixt_server_w_smartfps
    assert 'FPS' in ps.currentNames
    assert 'fps' in ts.registered_objects

    from swmain.network.pyroclient import connect_generic

    # No errors
    fps_proxy = connect_generic('FPS', *pyro_server.nsAddress)

    #assert fps_proxy.looplimit == 0.0
