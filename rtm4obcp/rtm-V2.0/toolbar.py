#!/usr/bin/python
#===============================================================================
# File : toolbar.py
# Notes:
#
#===============================================================================
from __future__ import absolute_import, print_function, division
import configuration

from PyQt5.QtCore import (Qt, QPoint)
from PyQt5.QtWidgets import (QToolBar, QPushButton, QMenu, QWidget,
                             QColorDialog)
from PyQt5.QtGui import QIcon

import constants as Kst

import editConfig
import socket


#-------------------------------------------------------------------------------
# toolbar
#-------------------------------------------------------------------------------
class Toolbar(QToolBar):

    def __init__(self, parent=None):
        #....................................................
        super(Toolbar, self).__init__(parent)
        self.cfg = configuration.cfg
        if self.cfg.debug: print("<Menubar.__init__>")
        self.parent = parent

        # Menus
        self.fileMenu = QMenu(self)
        self.fileMenu.addAction("Save configuration", self.saveConfig)
        self.fileMenu.addAction("Edit configuration File", self.editConfig)
        #s.fileMenu.addAction("Reset Plots",      s.clearPlotHistory)

        #s.fileMenu.addAction("Set  RealTime Host",      s.setHost)

        # Icons
        #
        self.IconDisconnected = QIcon(self.cfg.execdir +
                                      '/icons/leds/red-on-64.png')
        self.IconConnected = QIcon(self.cfg.execdir +
                                   '/icons/leds/green-on-64.png')

        # Buttons
        # make a connect Button
        self.conBtn = QPushButton(self.IconDisconnected, 'Connect', self)
        self.menuBtn = QPushButton('Menu', )  # make a menu  Button

        # Button  Handlers
        self.menuBtn.setMenu(self.fileMenu)  # set menu on button

        # Add widgets to toolbar
        self.addWidget(self.conBtn)
        self.addWidget(self.menuBtn)

        # connect buttons to handlers
        self.conBtn.clicked.connect(self.conBtnHandler)

        # preload edit popup window
        self.editConfigWindow = editConfig.editConfigWindowMwin()
        self.editConfigWindow.setWindowModality(Qt.NonModal)
        self.editConfigWindow.setGeometry(20, 80, 500, 900)

        # Tooltips
        self.conBtn.setToolTip('Connect/Disconnect data source')

        # set conBtn text,LED, state = disconnected
        self.set_conBtnState(Kst.DISCONNECTED)

    #...........................................................................
    # connect-button handler: toggle connect/disconnect data source
    def conBtnHandler(self):
        #print("conBtnHandler State:", s.rtDataState)
        if self.rtDataState == Kst.DISCONNECTED:
            self.cfg.lg.info("Connecting to data source...")
            if self.startRealtimeData():
                self.rtDataState = Kst.CONNECTED
        else:
            self.cfg.lg.info("Disconnecting data source...")
            if self.stopRealtimeData():
                self.rtDataState = Kst.DISCONNECTED

    #...........................................................................
    # state is Kst.CONNECTED or Kst.DISCONNECTED
    def set_conBtnState(self, state):
        #print("set_conBtnState State:", state)

        if state == Kst.DISCONNECTED:
            self.conBtn.setIcon(self.IconDisconnected)
            self.conBtn.setText("Connect")
        elif state == Kst.CONNECTED:
            self.conBtn.setIcon(self.IconConnected)
            self.conBtn.setText("Disconnect")
        else:
            self.cfg.lg.error(
                    "<toolbar.set_conBtnState> Bad connection state:%d" % state)

        self.rtDataState = state

    #...........................................................................
    def startRealtimeData(self):
        return (self.rtdCommand(Kst.RTD_CONNECT_CMD))

    #...........................................................................
    def stopRealtimeData(self):
        return (self.rtdCommand(Kst.RTD_DISCONNECT_CMD))

    #...........................................................................
    # Realtime data command. Send command to realtime data host
    def rtdCommand(self, command):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.settimeout(5)
        print("Set socket timeout:", skt.gettimeout())
        host = self.cfg.cfgD['gen']['rtDataHost']['value']
        port = self.cfg.cfgD['gen']['rtDataPort']['value']

        # Connect to realtime data server
        self.cfg.lg.info("** Connecting to host:%s port:%d" % (host, port))
        try:
            skt.connect((host, int(port)))
        except Exception as e:
            print("** Connect exception. Host:%s port:%d %s" % (host, port, e))
            skt.close()
            return (False)
        else:
            print("** Connected to %s:%d" % (host, port))

        # Send command to realtime data server
        self.cfg.lg.info("Sending Command:'%s' ==> rtData server %s:%d "% \
                       (command, host, port))
        try:
            skt.send(command + '\r')
        except Exception as e:
            print("** Socket Write Exception:", e)
            skt.close()
            return (False)

        skt.close()
        return (True)

    #....................................................
    def colorSelected(self, color):
        print("ColorSelected", color)
        print("Hue:", color.hsvHue())
        print("Sat:", color.saturation())
        print("Val:", color.value())

    #...........................................................................


#...........................................................................
#  Good for later versions of pyqt
#...........................................................................

    def raise_hsvWindow(self):
        print("* hsv ")
        QColorDialog(self).show()  # early pyqt

    #...........................................................................
    def editConfig(self):

        #s.editConfigWindow  = editConfig.editConfigWindowMwin()
        #s.editConfigWindow.setWindowModality(Qt.NonModal)
        #s.editConfigWindow.setGeometry(20,80, 500,900)

        qp = QWidget.mapToGlobal(self, QPoint(0, 0))  # where to pop up
        self.editConfigWindow.move(qp.x(), qp.y())
        self.editConfigWindow.setValues()
        self.editConfigWindow.show()

    #...........................................................................
    def saveConfig(self):
        self.editConfigWindow.saveDict()  # Perfrom a shelve sync

    #...........................................................................
    def colorPicker(self):
        QColorDialog(self).show()  # early pyqt

    def setPlotFrame(self, plotFrame):
        self.chf = plotFrame

    def clearPlotHistory(self, chf=None):
        self.chf.clearPlotHistory()

    def setPlotMinutes(self, chf=None):
        self.chf.setPlotRange(1)

    def setPlotHours(self, chf=None):
        self.chf.setPlotRange(2)
