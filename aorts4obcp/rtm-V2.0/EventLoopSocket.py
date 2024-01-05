####!/usr/bin/python
#^==============================================================================
#
# A socket subclass providing event-driven socket action handling from the
# Qt-event-loop. Uses socket and QSocketNotifer
#
# connect via: telnet 127.0.0.1 12345
#
# http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qsocketnotifier.html
# Modified for python 2.7
#===============================================================================
from __future__ import absolute_import, print_function, division

import sys
import zmq
import socket
import errno

import Constants as Kst
import Configuration

# for qsocketnotifier
from PyQt4 import QtCore
from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL


class EventLoopDataRecvMgr:

    def __init__(self, bytes_message_handler, host: str, port: int):
        '''
            Host: the RTC
            Port: the port on the RTC that's gonna feed us.
        '''
        self.config = Configuration.cfg
        self.logger = self.config.lg

        self.host = host
        self.port = int(port)

        zmq_context = zmq.Context()
        self.zmq_socket = zmq_context.socket(zmq.SUB)
        # Subscribed messages should start with "AORTS"
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, b'AORTS')
        # Connect for a SUB socket will pass even if the upstream is not alive yet.
        # No need to care.

        self.logger.info(f'Connecting ZMQ SUB socket to {host}, {port}')
        self.zmq_socket.connect(f"tcp://{self.host}:{self.port}")

        self.bytes_message_handler = bytes_message_handler
        self.qobj = QObject()  # To bind signals and slots to.

        self.read_notifier = QSocketNotifier(self.zmq_socket.getsockopt(zmq.FD),
                                             QSocketNotifier.Read, self.qobj)

        self.timeout_timer = QtCore.QTimer()

        # TODO
        # bind the connect button
        # add a qtimer to detect disconnect (e.g. 5 seconds stale)
        # also, set connected and reset the timer upon message received.

        self.read_notifier.activated.connect(self.upon_recv_message)
        # Purge the socket
        self.upon_recv_message(None, no_callback=True)

    def setConnectObject(self, connect_call):
        self.connect_call = connect_call

        def connect_call_disable():
            connect_call(False)

        self.timeout_timer.timeout.connect(connect_call_disable)
        # data-source connect/disconnect signals toolbar connect-button state

    def set_byteshandler(self, byteshandler):
        self.bytes_message_handler = byteshandler

    def upon_recv_message(self, _, no_callback=False):
        # From
        # https://stackoverflow.com/questions/52826595/pyzmq-with-qt-event-loop
        print('Upon recv.')

        self.read_notifier.setEnabled(False)

        if self.zmq_socket.getsockopt(zmq.EVENTS) & zmq.POLLIN:
            while self.zmq_socket.getsockopt(zmq.EVENTS) & zmq.POLLIN:
                topic, data = self.zmq_socket.recv_multipart()
                print('Receiving traffic!!', topic, data[:30])
            # Confirm connected state
            self.connect_call(True)
            self.timeout_timer.stop()

            # Call data_handler # Explicit or yet another signal?
            self.bytes_message_handler(data)

            # Restart timeout timer
            self.timeout_timer.start(3000)

        elif self.zmq_socket.getsockopt(zmq.EVENTS) & zmq.POLLOUT:
            self.logger.warning("[Socket] zmq.POLLOUT")
        elif self.zmq_socket.getsockopt(zmq.EVENTS) & zmq.POLLERR:
            self.logger.warning("[Socket] zmq.POLLERR")

        self.read_notifier.setEnabled(True)

        return 0
