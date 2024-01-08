####!/usr/bin/python
#^==============================================================================
# File: connections.py
#===============================================================================
from __future__ import absolute_import
from __future__ import print_function, division
from PyQt4 import QtCore, QtGui, QtSql
from PyQt4.QtGui import (QApplication, QDateEdit, QFrame, QGridLayout,
                         QHBoxLayout, QLabel, QLineEdit, QPushButton,
                         QRegExpValidator, QWidget)

import sys, time, select
import socket
import Constants as Kst
import os, errno
import Configuration

import socket


def rtd_command(s, host, port, command):

    skt = socket.socket()

    #skt.create_connection( host,port)
    #skt.send(command)

    rtc = skt.sendto((host, port), command)
    print("rtd_command rtc:%d", rtc)
