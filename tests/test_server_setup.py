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


#def test_make_servers_hang_about(rts_server_pair):
#    # This test can only be run with "-s" since it requires stdin
#    input('THIS IS BLOCKING THE SERVERS')
