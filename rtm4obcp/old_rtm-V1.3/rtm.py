#!/usr/bin/python
#===============================================================================
# File : start.py
#      : Start AO mirrors gui display and server
#
# Notes:
#  o connect to server via via: telnet 127.0.0.1 12345
#  o Test connection and data with datasource.py
#===============================================================================
from __future__ import absolute_import, print_function, division

import sys
#sys.path.append("../lib")
import Configurer
import Configuration
from PyQt4 import (QtCore, QtGui)
from PyQt4.QtCore import (Qt, SIGNAL, SLOT, QString, QSize, QRect, QPoint)
from PyQt4.QtGui import  (QMainWindow, QApplication,  QWidget,           \
                          QGridLayout, QHBoxLayout,   QVBoxLayout,       \
                          QLineEdit,   QFrame,QLabel, QPushButton,QDial, \
                          QSlider,QLabel,QMenuBar,QMenu,QColorDialog,    \
                          QSplitter,QSizePolicy,QFont, QPalette,QColor, \
                          QSpacerItem,QToolBar,QStatusBar)

import CmdlineOptions as Clo
import Constants as Kst
import numpy as np
import PyQt4.Qwt5 as Qwt
from EventLoopSocket import (EventLoopSocket_Listen, EventLoopSocket_Connected)
import RtData
import frm_MirrorFrame
import frm_SHFrame
import frm_TTPlotFrame
import frm_ChartsFrame
import Labels
import editConfig
import Constants as Kst
import Logger
import os
import util
import toolbar  # our toolbar.py


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def prn_data():
    print("-------------------------------------------------------------")
    #for i in range (0,188):
    #    print("%.2f" % mrr1_fdta[i])


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def getCommandLineOptions():
    # If debug, print commandline options to stdout
    if debug: CmdlineOptions.prn_options()
    CmdlineOptions.prn_options()


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class mainWindow(QMainWindow):

    def __init__(s, parent=None):

        super(mainWindow, s).__init__(parent)

        if Clo.version:
            print("Realtime Monitor Version %s" % Kst.VERSION)
            sys.exit()

        print("||||||||||||||||||||||||||||||||||||||||||||")
        print("||||||||||||  RTM V%s START ||||||||||||||||" % Kst.VERSION)
        print("||||||||||||||||||||||||||||||||||||||||||||")

        s.debug = Clo.debug  # commandline debug value
        if Clo.debug: Clo.prn_options()  # If debug, list commandline options

        #.......................................................................
        # Configure logging independently from Configurer so Configurer
        # can log configuration problems.
        #.......................................................................

        # logpath from command line or Constants.py
        if Clo.logpath is not None:  # given on commandline?
            logpath = Clo.logpath
        else:  # try the logpath from Constants.py
            logpath = "%s/%s" % (Kst.LOGDIR, Kst.LOGFILE
                                 )  # use constants default

        # 's.logger' is our wrapper instance, s.lg = s.logger.lg will be the
        # python logging module instance
        s.logger = Logger.Logger(logpath, nfiles=5, level='INFO', debug=s.debug)
        logpath = s.logger.logpath  # logpath from logger
        s.lg = s.logger.lg  # 's.lg' will be python logging system
        s.logger.setLevel('INFO')  # set console & file logging level

        # Now that we have logging, write startup banner to logfile
        s.logger.set_console_level('ERROR')  # don't write this to stdout again
        s.lg.info("\n\n")
        s.lg.info(
                "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
        )
        s.lg.info(
                "||||||||||||||||||||||||||||||   RTM V%s START   ||||||||||||||||||||||||||||||"
                % Kst.VERSION)
        s.lg.info(
                "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
        )
        s.logger.set_console_level(
                s.logger.level)  #restore console logging level

        # Configure all other startup-values from a config file (Kst.CONFIGFILE)
        Configurer.Configurer(Kst.CONFIGFILE, logpath, s.lg)
        cfg = Configuration.cfg
        cfg.logpath = s.logger.logpath
        s.lg.info("o Invoked as               : %s" % cfg.execname)
        s.lg.info("o Executable is            : %s" % cfg.execpath)
        s.lg.info("o Executing from Directory : %s" % cfg.execdir)
        s.lg.info("o Working Directory is     : %s" % cfg.cwd)
        s.lg.info("o Logging to file          : %s" % cfg.logpath)

        #s.lg.info("o QWT VERSION:", Qwt.
        #s.lg.info("o Executable directory    : %s" % cfg.execDir)
        #s.lg.info("o Configuration Path      : %s" % cfg.configpath)

        # mainwin status bar
        cfg.statusBar = QStatusBar()
        cfg.statusBar = s.statusBar
        #cfg.statusBar().showMessage('Status messages will be displayed here')

        # debug level is set from the command-line  --debug option
        if cfg.debug:
            s.lg.info(" o Debug level:%d" % cfg.debug)

        # if debug-level > 1,  print configuration
        if cfg.debug > 1 or cfg.verbose:
            cfg.prn_cfg()

        # Set background-color & font. Use a monospace font for readable values
        s.setStyleSheet("QMainWindow{ background-color: %s }" %
                        Kst.MWINBKGCOLOR)
        s.setFont(QFont("Monospace"))
        s.font = s.font()
        # s.font.setPointSize(8)

        # set main window Title
        s.setWindowTitle(QString("RealTime Data Monitor"))

        # Main Windowframe
        frm = QFrame()  #frm    = QFrame(s)
        frm.setFrameStyle(QFrame.Box)
        frm.setFrameShadow(QFrame.Sunken)

        #frm.setMidLineWidth(1)
        frm.setLineWidth(1)
        s.setCentralWidget(frm)  # set frame as mainwin central widget

        #s.setMenuBar(Menubar(s))   # set a menubar in main window
        s.toolbar = toolbar.toolbar(s)
        s.addToolBar(s.toolbar)

        #.......................................................................
        # Create subframes & their widgets
        s.Dmf1 = frm_MirrorFrame.MirrorFrame('DM')  # Dm Eye
        s.Crvf2 = frm_MirrorFrame.MirrorFrame('Curvature')  # Curvature Eye
        s.Apdf3 = frm_MirrorFrame.MirrorFrame('HOWFS/APD')  # Apd Eye
        s.Shf4 = frm_SHFrame.SHFrame('LOWFS/SH')  # S.Hartmann Eye
        s.Ttf5 = frm_TTPlotFrame.TTPlotFrame('TipTilt Mount')  # TipTilt plots
        s.Chf6 = frm_ChartsFrame.ChartsFrame('ChartsFrame')  # stripcharts
        s.Lbf7 = Labels.gainsLabelFrame()

        #Labels.fixLabelStyle(Lbf7)

        #.......................................................................
        # Layouts
        #.......................................................................
        mainLayout = QVBoxLayout()  # main layout contains top & bottom layouts
        topLayout = QHBoxLayout()  # top layout: mirror & shack hartmann eyes
        botLayout = QHBoxLayout()  # bottom layout:stripcharts,ttplots,labels
        botLeftLayout = QVBoxLayout()  # stacked stripcharts
        botRightLayout = QVBoxLayout()  # stacked ttplots,labelsframe

        #.......................................................................
        # Add Dm,Crv,Apd,Sh Eyes horizontally to top-layout
        topLayout.addWidget(s.Dmf1)
        topLayout.addWidget(s.Crvf2)
        topLayout.addWidget(s.Apdf3)
        topLayout.addWidget(s.Shf4)

        #.......................................................................
        botLeftLayout.addWidget(s.Chf6)

        botRightLayout.addWidget(s.Ttf5)
        botRightLayout.addWidget(s.Lbf7)
        botRightLayout.addStretch()

        botLayout.addLayout(botLeftLayout)
        botLayout.addLayout(botRightLayout)

        mainLayout.addLayout(topLayout)  # add top layout
        mainLayout.addLayout(botLayout)  # add bottom layout
        frm.setLayout(mainLayout)  # set layout in frame

        # Main Window x,y position on screen width/height
        #s.setGeometry(cfg.ScreenX,cfg.ScreenY,1200,750)

        #........................................................................
        # Create receiver for Mirror Data
        s.rtData = RtData.RtData(s)

        # Connect Eyball data-handlers
        s.rtData.connect(s.rtData, SIGNAL('EyeDataReady'),
                         s.Dmf1.mrr.data_ready)

        s.rtData.connect(s.rtData, SIGNAL('EyeDataReady'),
                         s.Crvf2.mrr.data_ready)

        s.rtData.connect(s.rtData, SIGNAL('EyeDataReady'),
                         s.Apdf3.mrr.data_ready)

        s.rtData.connect(s.rtData, SIGNAL('SHEyeDataReady'),
                         s.Shf4.shw.data_ready)

        #........................................................................
        # Connect labelled-data handlers
        #........................................................................
        # Dm labels
        s.rtData.connect(s.rtData, SIGNAL('LabelDataReady'),
                         s.Dmf1.labelsFrame.data_ready)

        # Crv labels
        s.rtData.connect(s.rtData, SIGNAL('LabelDataReady'),
                         s.Crvf2.labelsFrame.data_ready)

        # Apd labels
        s.rtData.connect(s.rtData, SIGNAL('LabelDataReady'),
                         s.Apdf3.labelsFrame.data_ready)

        # Sh labels
        s.rtData.connect(s.rtData, SIGNAL('LabelDataReady'),
                         s.Shf4.labelsFrame.data_ready)

        # Remaining labels
        s.rtData.connect(s.rtData, SIGNAL('LabelDataReady'), s.Lbf7.data_ready)

        # Shack-Hartmann defocus indicator
        s.rtData.connect(s.rtData, QtCore.SIGNAL('SHArrowDataReady'),
                         s.Shf4.defocus_data_ready)

        # Mirror frame defocus indicators
        s.rtData.connect(s.rtData, QtCore.SIGNAL('DefocusDataReady'),
                         s.Dmf1.defocus_data_ready)

        # Curvature frame defocus indicator
        s.rtData.connect(s.rtData, QtCore.SIGNAL('DefocusDataReady'),
                         s.Crvf2.defocus_data_ready)

        # tt plot Mount plots
        s.rtData.connect(s.rtData, QtCore.SIGNAL('MountPlotDataReady'),
                         s.Ttf5.data_ready)

        # Stripcharts
        s.rtData.connect(s.rtData, QtCore.SIGNAL('ChartDataReady'),
                         s.Chf6.data_ready)

        if cfg.debug:
            s.lg.info(" o Debug          : %d" % (cfg.debug))
        if cfg.test:
            s.lg.info(" o Test           : %d" % (cfg.test))

        # Server Socket: create socket, listen for connect in qt eventloop
        # call data_handler when data source connects
        try:
            s.Lskt = EventLoopSocket_Listen(s.rtData.data_handler, cfg.port)
        except Exception, e:
            s.lg.error("Could not create data socket:%s Goodbye..." % e)
            sys.exit(-1)

        s.Lskt.name = "Rtm Monitor Data Socket"

        #start listening (in eventLoop) for clients,create socketpair on connect
        s.Lskt.activate()

        # pass toolbar-Slot to Lskt's connected-socket signal
        # must be called after socket is 'activated'
        s.Lskt.setConnectObject(s.toolbar.set_conBtnState)

        s.lg.info("o Listening on port        : %d" % (cfg.port))

        s.toolbar.setPlotFrame(s.Chf6)

        cfg.Lskt = s.Lskt  ###!

    # called on window close
    def closeEvent(s, ev):

        #if s.Lskt.connected_skt is not None:

        s.lg.info(
                "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
        )
        s.lg.info(
                "||||||||||||||||||||||||||||||   RTM V%s END     ||||||||||||||||||||||||||||||"
                % Kst.VERSION)
        s.lg.info(
                "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        )


#-------------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":

    #.......................................................................
    qap = QApplication(sys.argv)  # must have an 'application'
    mwin = mainWindow()  # create our main window
    mwin.show()  # show it

    # temporary Kludge to get correct border around labelled values on ao188
    Labels.fixLabelStyle(mwin.Dmf1.labelsFrame)
    Labels.fixLabelStyle(mwin.Crvf2.labelsFrame)
    Labels.fixLabelStyle(mwin.Apdf3.labelsFrame)
    Labels.fixLabelStyle(mwin.Shf4.labelsFrame)
    Labels.fixLabelStyle(mwin.Lbf7)

    qap.exec_()  # enter application event loop
