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

# for qsocketnotifier
from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer, QCoreApplication
from PyQt4.QtCore import QEventLoop


#------------------------------------------------------------------------------
# class EventLoopSocket_Connected(socket.socket):
#------------------------------------------------------------------------------
class EventLoopSocket_Connected(socket.socket):

    def __init__(s, userdatahandler, family=socket.AF_INET,
                 type=socket.SOCK_STREAM, proto=0, _sock=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        super(EventLoopSocket_Connected, s).__init__(family, type, proto, _sock)

        s.name = None  # Name of listening socket. Optionally set by user.
        s.create_notifier()
        s.userdatahandler = userdatahandler
        s.qobj = QObject()

        # uncomment to map this process's stdout etc to the client
        #sys.stdout = s
        #sys.stdin  = s
        #sys.stderr = s

    #---------------------------------------------------------------------------
    def write(s, text):
        try:
            s.send(text)
        except Exception, exc:
            print("Write socket exception %s" % (exc))
            return False  # !!! check return logic
        return True  # !!! check return logic

    #---------------------------------------------------------------------------
    #def write(s, text):
    #    return s.send(text)
    #---------------------------------------------------------------------------
    def readlines(s):
        return s.recv(2048)

    #---------------------------------------------------------------------------
    def read(s):
        return s.recv(1024)

    #def read(s):
    #    s.databuffer = s.recv(188)
    def create_notifier(s):
        #s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

        # create eventloop socket action notifier
        s.notify_read = SktNtfy(s.fileno(), s, QSocketNotifier.Read)
        s.notify_write = SktNtfy(s.fileno(), s, QSocketNotifier.Write)
        # skt =  s.notify_write.socket()

        # wire handlers to the QSocketNotifer
        # socket-action event handler.
        s.notify_read.event = s.socket_read_ready
        s.notify_write.event = s.socket_write_ready

        # enable the client connect handler
        s.notify_read.setEnabled(True)
        s.notify_write.setEnabled(True)

    def set_databuffer(s, buffer):
        s.databuffer = buffer

    def set_userdatahandler(s, userdatahandler):
        s.userdatahandler = userdatahandler

    # On socket ready to read action, qSocketNotifer will call this method
    # from event-loop.
    def socket_read_ready(s, event):
        #print("socket_read_ready")
        s.notify_read.setEnabled(False)
        notifier = s.notify_read  # our read notifier
        skt = notifier.skt

        if s.userdatahandler(s):  # read socket data
            s.notify_read.setEnabled(True)
            return (True)
        else:
            s.lg.info("<socket_read_ready> SHUTTING DOWN connected socket.")
            s.qobj.emit(SIGNAL('DataSocket'), Kst.DISCONNECTED)

            #s.notify_read.setEnabled  (False)
            #s.notify_write.setEnabled (False)
            s.flushit()
            s.shutdown(socket.SHUT_RD)  # SHUT_RD, SHUT_WR, SHUT_RDWR
            s.close()
            return False

    def flushit(s):
        r = True
        while r:
            r = s.read()

    def socket_write_ready(s, event):
        #event.setAccepted(True)
        #print("socket_write_ready")
        s.notify_write.skt.write("DMGUI:OK")
        s.notify_write.setEnabled(False)
        return True

        #event.accept() # same as setAccepted(True)
        #print("Event           :", event)
        #print("Event type      :", event.Type)
        #print("Event type value:", event.Type())


#^------------------------------------------------------------------------------
# connect via: 'telnet 127.0.0.1 12345'
#-------------------------------------------------------------------------------
class EventLoopSocket_Listen(socket.socket):

    #---------------------------------------------------------------------------
    def __init__(s, userdatahandler, port=None, family=socket.AF_INET,
                 type=socket.SOCK_STREAM, proto=0, _sock=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        super(EventLoopSocket_Listen, s).__init__(family, type, proto, _sock)
        #print("EventLoopSocket_Listen")

        if port is None:
            s.cfg.lg.error("No port specified. Goodbye...")
            sys.exit(-1)
        if port <= Kst.RESERVEDPORTSTOP:
            s.cfg.lg.error(
                    "Error: Illegal port number=%d. Must be > %d. Goodbye..." %
                    (s.port, Kst.RESERVEDPORTSTOP))
            sys.exit(-1)

        s.port = int(port)

        s.Cskt = None  # Connected socket created by accept
        s.Cskt_addr = None  # Address of connected socket
        s.name = None  # Name of this listening socket. Set by user.
        s.EvlSc = None
        s.userdatahandler = userdatahandler
        s.connected_skt = None
        s.qobj = QObject()

    def setConnectObject(s, f):
        s.f = f
        # data-source connect/disconnect signals toolbar connect-button state
        QtCore.QObject.connect(s.qobj, QtCore.SIGNAL('DataSocket'), s.f)

    #---------------------------------------------------------------------------
    # set opts, bind, listen, create event-loop notifier
    def activate(s):

        if s.cfg.debug: print("<EventLoopSocket_Listen>.activate")

        # the SO_REUSEADDR flag tells the kernel to reuse a local socket
        # in TIME_WAIT state, without waiting for its natural timeout to expire.
        # timeout = 2 * Maximum-Segment-Lifetime (MSL). = 4 minutes max.
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, exc:
            s.cfg.lg.error("Problem setting socket opt %s" % (exc))

        try:
            s.bind(('', int(s.port)))  # '' = all available interfaces
        except Exception, exc:
            s.cfg.lg.error("Can't bind socket at port %d:%s" % (s.port, exc))
            if exc.errno == errno.EADDRINUSE:
                s.cfg.lg.warn(
                        "Is another version of this program running at port %d?"
                        % (s.port))
            sys.exit(0)

        # Listen for connection requests
        try:
            rtc = s.listen(1)
        except Exception, exc:
            s.cfg.lg.error("Problem listening at port %d:%s" % (s.port, exc))
            sys.exit(-1)

        # create eventloop socket action notifier to connect listening socket
        try:
            s.notify_connect = SktNtfy(s.fileno(), s, QSocketNotifier.Read)
        except Exception, exc:
            s.cfg.lg.error("Problem creating notifier %d:%s" % (s.port, exc))
            sys.exit(-1)

        # wire our static method 'connect_request as the QSocketNotifer
        # socket-action event handler.
        s.notify_connect.event = s.connect_request

        # enable the client connect handler
        s.notify_connect.setEnabled(True)

    #---------------------------------------------------------------------------
    # On client connection attempt to our initial listening socket,
    # qSocketNotifer will call this method from the pyqt event-loop.
    def connect_request(s, event):
        if s.cfg.debug:
            print("EventLoopSocket_Listen *** connect_request ***")
            print("Event           :", event)
            print("Event type      :", event.Type)
            print("Event type value:", event.Type())
            print("socket:", s.notify_connect.socket)

        if s.connected_skt is not None:
            s.cfg.lg.info("<connect_request> SHUTTING DOWN connected socket.:")
            s.qobj.emit(SIGNAL('DataSocket'), Kst.DISCONNECTED)
            try:
                s.connected_skt.shutdown(2)
            except Exception as exc:
                s.cfg.lg.error(
                        "problem shuting down connected socket number %d:%s" %
                        (s.connected_skt.fileno(), exc))
            else:
                s.cfg.lg.info("Close connected socket for reconnect%d:" %
                              s.connected_skt.fileno())

        sktnotifier = s.notify_connect
        Lskt = sktnotifier.skt
        if Lskt.name:  # say what's happening
            s.cfg.lg.info("Connect request on socket [%s] [%d]:" %
                          (Lskt.name, Lskt.fileno()))
        else:
            s.cfg.lg.info("Connect request on socket number %d" % Lskt.fileno())
        try:
            s.connected_skt = Lskt.accept_client()  # get a new connected socket
            s.qobj.emit(SIGNAL('DataSocket'), Kst.CONNECTED)

        except Exception as exc:
            s.cfg.lg.error("    Connect Error: %s" % exc)
            return (False)

        ## Allow new clients to disconnect current client
        s.notify_connect.setEnabled(True)

        return (True)

    #---------------------------------------------------------------------------
    def write(s, text):
        return s.send(text)

    #---------------------------------------------------------------------------
    #def readlines(s):
    #    return s.recv(2048)
    #---------------------------------------------------------------------------
    def read(s):
        return s.recv(1024)

    #---------------------------------------------------------------------------
    #
    # Accept a connection on our listening socket (self).
    # accept() return value is a pair ( socket, address)
    # where socket is a new connected socket object usable to send and
    # receive data.
    # Address is the address bound to the socket on the other end of
    # the connection.
    #
    # keep
    #
    #---------------------------------------------------------------------------
    def accept_client(s):
        skt, s.Cskt_addr = s.accept()
        #EventLoopSocket_Connected(s.userdatahandler, _sock=skt, )
        s.EvlSc = EventLoopSocket_Connected(
                s.userdatahandler,
                _sock=skt,
        )
        QtCore.QObject.connect(s.EvlSc.qobj, QtCore.SIGNAL('DataSocket'), s.f)
        s.Cskt = skt
        s.cfg.lg.info("Accept client connection. Address:%s Socket number:%d " %
                      (s.Cskt_addr, skt.fileno()))
        return (skt)

    #---------------------------------------------------------------------------
#    def set_connected_socket(s,skt):
#        s.Cskt = EventLoopSocket_Connected(_sock=skt)

#---------------------------------------------------------------------------

    def connected_socket(s):
        return (s.Cskt)

    #---------------------------------------------------------------------------
    def set_userdatahandler(s, userdatahandler):
        s.userdatahandler = userdatahandler

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------


# Class SktNtfy  : QSocketNotifier subclass to allow socket instance to be retrieved
#            from event call
#
# QSocketNotifier allows file-descriptor (including socket) event handling
# from Qt's event loop.
#
# To monitor both reads and writes for the same file-descriptor, you must
# create two socket notifiers.
#
# Cannot install two notifiers of the same type (Read, Write, Exception) on
# the same socket.
#
# Possible notifier type arguements are:
#  QSocketNotifier.Read      : There is data to be read.
#  QSocketNotifier.Write     : Data can be written.
#  QSocketNotifier.Exception : Exception (pyqt doc "recommends" against using this)
#
#  The setEnabled() function allows you to disable as well as enable the
#  socket notifier. It is generally advisable to explicitly enable or
#  disable the socket notifier, especially for write notifiers.
#  A disabled notifier ignores socket events (the same effect as not creating the
#  socket notifier).
#  Use the isEnabled() function to determine the notifier's current status.
#
class SktNtfy(QSocketNotifier):

    # init
    # fno: socket file-number
    # ntfy_type: one of QSocketNotifier.Read|Write|Exception
    # skt: python socket instance
    def __init__(s, fno, skt, ntfy_type, parent=None):
        super(SktNtfy, s).__init__(fno, ntfy_type, parent)
        s.skt = skt
        #print("notifier done")

    # QSocketNotifier funtion s.socket() seems ill-named.
    # Returns socket.fileno()   I prefer this:
    def fileno(s):
        return (s.socket())

    # overwritten by EventLoopSocket
    # Receives events to an object. Should return true if the event was
    # recognized and processed.  Reimplemented from QsocketNotifier.event(),
    # Reimplemented QObject.event()
    # http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qobject.html#eventrom


#    def event(s, event ):
#        print("*** SktNtfy event ***")
#        print("Event:", event)
#
#        s.setEnabled (False)
#
#        #if !s.accepted:
#        #    print("Accept socket connection")
#        #    s.conn, s.addr = s.skt.accept()
#        return True

#
#> the full def of socket.accept():
#>
#>     def accept(self):
#>         sock, addr = self._sock.accept()
#>         return _socketobject(_sock=sock), addr
#>
#> Just change it to
#>
#>     def accept(self):
#>         sock, addr = self._sock.accept()
#>         return MySocket(_sock=sock), addr
