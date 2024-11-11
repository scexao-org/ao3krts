import pytest

import subprocess as sproc
import time

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer

from aorts.server.test_command import ActualInterestingTestObject

from scxconf import PYRONSAO_PORT


# ConfTest.py FIXTture == ctfixt_
@pytest.fixture(scope='session')
def ctfixt_server_pair(request):

    ns_proc = sproc.Popen(f'pyro4-ns -p 63445'.split())
    time.sleep(0.5)

    CMD_OBJS = [
            ActualInterestingTestObject(),
    ]

    pyro_server = PyroServer(bindTo=('localhost', 0),
                             nsAddress=('localhost', 63445))
    tcp_server = ObjectDispatchingServer(('localhost', 63446), objs=[])

    for cmd_obj in CMD_OBJS:
        pyro_server.add_device(device=cmd_obj, deviceName=cmd_obj.NAME)
        tcp_server.add_device(key=cmd_obj.NAME, obj=cmd_obj)

    pyro_server.start()
    tcp_server.start()

    yield pyro_server, tcp_server

    #def teardown():
    pyro_server.stop()
    tcp_server.stop()
    ns_proc.kill()
    ns_proc.communicate()

    #request.addfinalizer(teardown)


@pytest.fixture
def ctfixt_server_w_status_command(ctfixt_server_pair):
    pyro_server: PyroServer = ctfixt_server_pair[0]
    tcp_server: ObjectDispatchingServer = ctfixt_server_pair[1]

    from aorts.server.device_commands import StatusCommand
    s = StatusCommand()

    pyro_server.add_device(s.CALLEE, s.NAME)
    tcp_server.add_device(key=s.NAME, obj=s)

    yield pyro_server, tcp_server

    pyro_server.remove_device_by_name(s.NAME)
    tcp_server.remove_device_by_name(s.NAME)
