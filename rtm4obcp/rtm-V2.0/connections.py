####!/usr/bin/python
#^==============================================================================
# File: connections.py
#===============================================================================
from __future__ import absolute_import, print_function, division

import socket


def rtd_command(s, host, port, command):

    skt = socket.socket()

    #skt.create_connection( host,port)
    #skt.send(command)

    rtc = skt.sendto((host, port), command)
    print("rtd_command rtc:%d", rtc)
