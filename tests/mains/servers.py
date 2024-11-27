import pytest

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer


def test_setup_server_and_handover(ctfixt_server_pair):
    '''
    How do I even invoke this?
    '''
    pyro_server: PyroServer = ctfixt_server_pair[0]
    tcp_server: ObjectDispatchingServer = ctfixt_server_pair[1]

    input('Hold it here. You may now use the TCP server and Pyro server on localhost.'
          )

    return
