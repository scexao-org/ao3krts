from __future__ import annotations

import typing as typ

import os, sys, atexit
import logging
from swmain.infra.logger import init_logger_autoname

from swmain.network.pyroserver_registerable import PyroServer
from swmain.network.tcpserver import ObjectDispatchingServer

from .dispatcher import global_click_invokator

import threading

import time

# Collection of control objects
from .test_command import ActualInterestingTestObject
from .device_commands import DM3k, TT, Status, DM3kHKL
from .ao_commands import Loop, Gain
from .system_commands import ModeSwitcher


def main_g2if():
    init_logger_autoname()
    logg = logging.getLogger()
    logg.setLevel(logging.DEBUG)
    for h in logg.handlers:
        h.setLevel(logging.DEBUG)

    # Define command objects
    '''
    CMD_OBJS = {
            'AOCMD_TT': cmd.TTCmd(),
            'AOCMD_LOOP': cmd.LoopCmd(),
            'AOCMD_BIM188': cmd.Bim188Cmd(),
    }
    '''

    # Create singleton control objects -- actually should check of a running instance to avoid dupletons
    CMD_OBJS = {
            'x': ActualInterestingTestObject(),
            'dm': DM3k(),
            'dmc': DM3kHKL(),
            'tt': TT(),
            'loop': Loop(),
            'gain': Gain(),
            'status': Status(),
            'modes': ModeSwitcher(),
    }

    from scxconf import PYRONSAO_HOST, PYRONSAO_PORT, IP_AORTS_SUMMIT
    pyro_server = PyroServer(bindTo=('localhost', 0),
                             nsAddress=(PYRONSAO_HOST, PYRONSAO_PORT))
    # Fixme G2IF_SERVER_PORT
    tcp_server = ObjectDispatchingServer((IP_AORTS_SUMMIT, 18826), objs=[])
    for cmd_obj in CMD_OBJS.values():
        pyro_server.add_device(device=cmd_obj, deviceName=cmd_obj.NAME)
        tcp_server.add_device(key=cmd_obj.NAME, obj=cmd_obj)

    # CMD_OBJS['x'].invoke_call('--help')
    # CMD_OBJS['x'].invoke_call('efgh 1')

    #return CMD_OBJS['TEST']

    atexit.register(pyro_server.stop)
    atexit.register(tcp_server.stop)

    pyro_server.start()
    tcp_server.start()

    while True:
        '''
        for obj in CMD_OBJS.values():
            print('obj', obj.NAME)
            #obj.ensure_sanity()
            pass
        '''
        time.sleep(5.0)


if __name__ == "__main__":
    test = main_g2if()
