#!/usr/bin/python
#===============================================================================
# File : toolbar.py
# Notes:
#
#===============================================================================
from __future__ import absolute_import, print_function, division
import Configuration
from PyQt4 import (QtCore, QtGui)
from PyQt4.QtCore import (Qt, SIGNAL, SLOT, QString, QPoint)
from PyQt4.QtGui import  (QToolBar,QPushButton, QToolButton, QSpacerItem, \
     QIcon, QMenu, QWidget)

import Constants as Kst
import util
#from PyKDE4.kdeui import KLed
import editConfig
import socket


#-------------------------------------------------------------------------------
# toolbar
#-------------------------------------------------------------------------------
class toolbar(QToolBar):

    def __init__(s, parent=None):
        #....................................................
        super(toolbar, s).__init__(parent)
        s.cfg = Configuration.cfg
        if s.cfg.debug: print("<Menubar.__init__>")
        s.parent = parent

        # Menus
        s.fileMenu = QMenu(s)
        s.fileMenu.addAction("Save Configuration", s.saveConfig)
        s.fileMenu.addAction("Edit Configuration File", s.editConfig)
        #s.fileMenu.addAction("Reset Plots",      s.clearPlotHistory)

        #s.fileMenu.addAction("Set  RealTime Host",      s.setHost)

        # Icons
        #
        s.IconDisconnected = QIcon(s.cfg.execdir + '/icons/leds/red-on-64.png')
        s.IconConnected = QIcon(s.cfg.execdir + '/icons/leds/green-on-64.png')

        # Buttons
        # make a connect Button
        s.conBtn = QPushButton(s.IconDisconnected, 'Connect', s)
        s.menuBtn = QPushButton('Menu', )  # make a menu  Button

        # Button  Handlers
        s.menuBtn.setMenu(s.fileMenu)  # set menu on button

        # Add widgets to toolbar
        s.addWidget(s.conBtn)
        s.addWidget(s.menuBtn)

        # connect buttons to handlers
        s.conBtn.connect(s.conBtn, SIGNAL('clicked()'), s.conBtnHandler)

        # preload edit popup window
        s.editConfigWindow = editConfig.editConfigWindowMwin()
        s.editConfigWindow.setWindowModality(Qt.NonModal)
        s.editConfigWindow.setGeometry(20, 80, 500, 900)

        # Tooltips
        s.conBtn.setToolTip(QString('Connect/Disconnect data source'))

        # set conBtn text,LED, state = disconnected
        s.set_conBtnState(Kst.DISCONNECTED)

    #...........................................................................
    # connect-button handler: toggle connect/disconnect data source
    def conBtnHandler(s):
        #print("conBtnHandler State:", s.rtDataState)
        if s.rtDataState == Kst.DISCONNECTED:
            s.cfg.lg.info("Connecting to data source...")
            if s.startRealtimeData():
                s.rtDataState = Kst.CONNECTED
        else:
            s.cfg.lg.info("Disconnecting data source...")
            if s.stopRealtimeData():
                s.rtDataState = Kst.DISCONNECTED

    #...........................................................................
    # state is Kst.CONNECTED or Kst.DISCONNECTED
    def set_conBtnState(s, state):
        #print("set_conBtnState State:", state)

        if state == Kst.DISCONNECTED:
            s.conBtn.setIcon(s.IconDisconnected)
            s.conBtn.setText("Connect")
        elif state == Kst.CONNECTED:
            s.conBtn.setIcon(s.IconConnected)
            s.conBtn.setText("Disconnect")
        else:
            s.cfg.lg.error("<toolbar.set_conBtnState> Bad connection state:%d" %
                           state)

        s.rtDataState = state

    #...........................................................................
    def startRealtimeData(s):
        return (s.rtdCommand(Kst.RTD_CONNECT_CMD))

    #...........................................................................
    def stopRealtimeData(s):
        return (s.rtdCommand(Kst.RTD_DISCONNECT_CMD))

    #...........................................................................
    # Realtime data command. Send command to realtime data host
    def rtdCommand(s, command):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.settimeout(5)
        print("Set socket timeout:", skt.gettimeout())
        host = s.cfg.cfgD['gen']['rtDataHost']['value']
        port = s.cfg.cfgD['gen']['rtDataPort']['value']

        # Connect to realtime data server
        s.cfg.lg.info("** Connecting to host:%s port:%d" % (host, port))
        try:
            skt.connect((host, int(port)))
        except Exception, e:
            print("** Connect exception. Host:%s port:%d %s" % (host, port, e))
            skt.close()
            return (False)
        else:
            print("** Connected to %s:%d" % (host, port))

        # send command to realtime data server
        s.cfg.lg.info("Sending Command:'%s' ==> RtData server %s:%d "% \
                       (command, host, port))
        try:
            skt.send(command + '\r')
        except Exception, e:
            print("** Socket Write Exception:", e)
            skt.close()
            return (False)

        skt.close()
        return (True)

    def saveConfig(s):
        s.editConfigWindow.saveDict()  # Perfrom a shelve sync

    #...........................................................................
    def editConfig(s):

        #s.editConfigWindow  = editConfig.editConfigWindowMwin()
        #s.editConfigWindow.setWindowModality(Qt.NonModal)
        #s.editConfigWindow.setGeometry(20,80, 500,900)

        qp = QWidget.mapToGlobal(s, QPoint(0, 0))  # where to pop up
        s.editConfigWindow.move(qp.x(), qp.y())
        s.editConfigWindow.setValues()
        s.editConfigWindow.show()

    #....................................................
    def colorSelected(s, color):
        print("ColorSelected", color)
        print("Hue:", color.hsvHue())
        print("Sat:", color.saturation())
        print("Val:", color.value())

    #...........................................................................
#    def colorChoice(s,color):
#        print("ColorChoice")
#        print("Hue:", color.hsvHue())
#        print("Sat:", color.saturation())
#        print("Val:", color.value())

#...........................................................................
#  Good for later versions of pyqt
#...........................................................................

    def raise_hsvWindow(s):
        print("* hsv ")

        #s.connect (s.colordlg, QtCore.SIGNAL('currentColorChanged(QColor)'),
        #           s.colorChoice)

        #s.connect (s.colordlg, QtCore.SIGNAL('colorSelected(QColor)'),
        #           s.colorSelected)

        #s.colordlg.show()

        QColorDialog(s).show()  # early pyqt

    #...........................................................................
    #  raise color picker window.
    #  >>> No good for ao188.  Needs pyqt update
    #...........................................................................
    def later_raise_hsvWindow(s):
        print("* hsv ")

        #s.connect (s.colordlg, QtCore.SIGNAL('currentColorChanged(QColor)'),
        #           s.colorChoice)

        #s.connect (s.colordlg, QtCore.SIGNAL('colorSelected(QColor)'),
        #           s.colorSelected)

        #s.colordlg.show()

    #...........................................................................
    def editConfig(s):

        #s.editConfigWindow  = editConfig.editConfigWindowMwin()
        #s.editConfigWindow.setWindowModality(Qt.NonModal)
        #s.editConfigWindow.setGeometry(20,80, 500,900)

        qp = QWidget.mapToGlobal(s, QPoint(0, 0))  # where to pop up
        s.editConfigWindow.move(qp.x(), qp.y())
        s.editConfigWindow.setValues()
        s.editConfigWindow.show()

    #...........................................................................
    def saveConfig(s):
        s.editConfigWindow.saveDict()  # Perfrom a shelve sync

    #...........................................................................
    def colorPicker(s):
        QColorDialog(s).show()  # early pyqt

    def setPlotFrame(s, plotFrame):
        s.chf = plotFrame

    def clearPlotHistory(s, chf=None):
        s.chf.clearPlotHistory()

    def setPlotMinutes(s, chf=None):
        s.chf.setPlotRange(1)

    def setPlotHours(s, chf=None):
        s.chf.setPlotRange(2)

    #menubar.fileMenu.addAction("Set HSV",mrrcolorBar.colorDialog.show())
    #menubar.connect (QColorDialog(menubar),
    #    QtCore.SIGNAL('colorSelected(QColor)'), Dmf1.mrr.colorChoice)

    #s.rtDataLed = KLed()                  # Connect indicator LED
    #s.addWidget(s.rtDataLed)
    #from PyKDE4.kdeui import KColorPatch


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
#class Menubar(QMenuBar):
#
#    def __init__(s,parent=None):
#         #....................................................
#         super(Menubar,s).__init__(parent)
#
#         cfg = Configuration.cfg
#         if cfg.debug: print("<Menubar.__init__>")
#
#         s.parent = parent
#
#         #....................................................
#         # Menus
#         s.fileMenu     = QMenu(s)
#         s.editMenu     = QMenu(s)
#         s.connectMenu  = QMenu(s)
#         s.fileMenu.setTitle(QString("File"))
#         s.editMenu.setTitle(QString("Edit"))
#
#         #s.connectMenu.setTitle(QString("Connect"))
#         #s.fileMenu.setTearOffEnabled (True)
#         s.fileMenu.addAction("Save Configuration", s.saveConfig)
#         s.editMenu.addAction("Edit Configuration File", s.editConfig)
#         s.editMenu.addAction("Set  RealTime Host", s.setHost)
#         #s.connectMenu.addAction("Ping RealTime Host", s.pingHost)
#
#         # Broken on ao188 pyqt versions
#         #s.fileMenu.addAction("ColorPicker", s.colorPicker)
#         #s.fileMenu.addAction   ("Set Color",s.raise_hsvWindow)
#         #s.colordlg = QtGui.QColorDialog(s.parent)
#         # Create Configuration editor toplevel window ahead of need
#
#         #fg     = " QWidget {color:%s}"% Kst.LBLFGCOLOR
#         #fg     = " QMenu {color:%s}"% Kst.LBLFGCOLOR
#         #bg     = " QWidget {background-color:%s}" % Kst.SETALARMPOPUPBKG
#         #border = " QWidget {border-color:%s}" % '#000000'
#         #s.connectMenu.setStyleSheet( fg+bg+border )
#
#         s.addMenu(s.fileMenu)
#         s.addMenu(s.editMenu)
#
#         # preload edit popup window
#         s.editConfigWindow  = editConfig.editConfigWindowMwin()
#         s.editConfigWindow.setWindowModality(Qt.NonModal)
#         s.editConfigWindow.setGeometry(20,80, 500,900)
#
#         #s.Led = KLed()
#         #s.setCornerWidget(s.Led)
#         #s.connectBtn = QPushButton(s)
#         #s.connectBtn.connect( s.connectBtn, SIGNAL('clicked()'), connect)
#
#
#    #....................................................
#    def colorSelected(s,color):
#        print("ColorSelected", color)
#        print("Hue:", color.hsvHue())
#        print("Sat:", color.saturation())
#        print("Val:", color.value())
#
#    #...........................................................................
##    def colorChoice(s,color):
##        print("ColorChoice")
##        print("Hue:", color.hsvHue())
##        print("Sat:", color.saturation())
##        print("Val:", color.value())
#
#    #...........................................................................
#    #  Good for later versions of pyqt
#    #...........................................................................
#    def raise_hsvWindow(s):
#        print("* hsv ")
#
#        #s.connect (s.colordlg, QtCore.SIGNAL('currentColorChanged(QColor)'),
#        #           s.colorChoice)
#
#        #s.connect (s.colordlg, QtCore.SIGNAL('colorSelected(QColor)'),
#        #           s.colorSelected)
#
#        #s.colordlg.show()
#
#        QColorDialog(s).show()  # early pyqt
#
#    #...........................................................................
#    #  raise color picker window.
#    #  >>> No good for ao188.  Needs pyqt update
#    #...........................................................................
#    def later_raise_hsvWindow(s):
#        print("* hsv ")
#
#        #s.connect (s.colordlg, QtCore.SIGNAL('currentColorChanged(QColor)'),
#        #           s.colorChoice)
#
#        #s.connect (s.colordlg, QtCore.SIGNAL('colorSelected(QColor)'),
#        #           s.colorSelected)
#
#        #s.colordlg.show()
#
#    #...........................................................................
#    def editConfig(s):
#
#        #s.editConfigWindow  = editConfig.editConfigWindowMwin()
#        #s.editConfigWindow.setWindowModality(Qt.NonModal)
#        #s.editConfigWindow.setGeometry(20,80, 500,900)
#
#        qp = QWidget.mapToGlobal (s, QPoint(0,0)) # where to pop up
#        s.editConfigWindow.move(qp.x(),qp.y())
#        s.editConfigWindow.setValues()
#        s.editConfigWindow.show()
#
#    #...........................................................................
#    def saveConfig(s):
#        s.editConfigWindow.saveDict()     # Perfrom a shelve sync
#
#    #...........................................................................
#    def colorPicker(s):
#        QColorDialog(s).show()  # early pyqt
#
#       #menubar.fileMenu.addAction("Set HSV",mrrcolorBar.colorDialog.show())
#       #menubar.connect (QColorDialog(menubar),
#       #    QtCore.SIGNAL('colorSelected(QColor)'), Dmf1.mrr.colorChoice)
#
#    def connectHost(s):
#        print("Connect to host")
#
#    def setHost(s):
#        print("Set host")
#
#    def pingHost(s):
#        print("Ping host")
#
#
#
#
#
#
