'''
This is just a test in another file to make
sure the "package" level fixture defined in that
other file ./test_server_setup.py
is behaved ok?
'''


def test_this_test(ctfixt_server_pair):
    '''
    This test is just a play on the
        ctfixt_server_pair
    fixture that is served from conftest.py
    '''
    from swmain.network.pyroserver_registerable import PyroServer
    from swmain.network.tcpserver import ObjectDispatchingServer

    pyro_server, tcp_server = ctfixt_server_pair
    assert isinstance(pyro_server, PyroServer)
    assert isinstance(tcp_server, ObjectDispatchingServer)


def test_status_not_in_server(ctfixt_server_pair):
    '''
    Testing that
        ctfixt_server_pair
    does not contain a 'status' object
    '''
    ps, ts = ctfixt_server_pair
    assert 'STATUS' not in ps.currentNames
    assert 'status' not in ts.registered_objects


def test_status_in_server(ctfixt_server_w_status_command):
    '''
    Testing that
        ctfixt_server_w_status_command
    which is a sub-fixture of
        ctfixt_server_pair
    does indeed contain a 'status' object
    '''
    ps, ts = ctfixt_server_w_status_command
    assert 'STATUS' in ps.currentNames
    assert 'status' in ts.registered_objects
