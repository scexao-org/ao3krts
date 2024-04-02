from __future__ import annotations

import typing as typ

import os, sys, atexit
import logging
from swmain.infra.logger import init_logger_autoname

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer

import threading

from . import command_objs as cmd

import time


def main_g2if():
    init_logger_autoname()
    logg = logging.getLogger()

    # Define command objects
    '''
    CMD_OBJS = {
            'AOCMD_TT': cmd.TTCmd(),
            'AOCMD_LOOP': cmd.LoopCmd(),
            'AOCMD_BIM188': cmd.Bim188Cmd(),
    }
    '''
    CMD_OBJS = {'TEST': cmd.TestCmd()}

    GLOBAL_LOCK = threading.RLock()

    from scxconf import PYRONSAO_HOST, PYRONSAO_PORT, IP_AORTS_SUMMIT
    pyro_server = PyroServer(bindTo=('localhost', 0),
                             nsAddress=(PYRONSAO_HOST, PYRONSAO_PORT))
    tcp_server = ObjectDispatchingServer(('localhost', 19826), objs=[])
    for key, cmd_obj in CMD_OBJS.items():
        cmd_obj.set_lock_obj(GLOBAL_LOCK)
        pyro_server.add_device(device=cmd_obj, deviceName=key)
        tcp_server.add_device(key=key, obj=cmd_obj)

    atexit.register(pyro_server.stop)
    atexit.register(tcp_server.stop)

    pyro_server.start()
    tcp_server.start()

    while True:
        for obj in CMD_OBJS.values():
            obj.ensure_sanity()
        time.sleep(1.0)


if __name__ == "__main__":
    main_g2if()
