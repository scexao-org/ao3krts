#!/usr/bin/env python
#===============================================================================
# File : start.py
#      : Start AO mirrors gui display and server
#
# Notes:
#  o connect to server via via: telnet 127.0.0.1 12345
#  o Test connection and data with datasource.py
#===============================================================================
from __future__ import absolute_import, print_function, division
# PyQt5 fails to link the proper libstdc++ in a conda environment, and goes
# for the system one (usually older), which creates conflict with subsequent imports.
# We import ZMQ BEFORE any Qt import to force linkage to libstdc++ in the proper environment
# (zmq caused the conflict, but anything that loads some cython / compiled stuff would work)
import zmq

import sys
#sys.path.append("../lib")
import Configurer
import Configuration

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QMainWindow, QApplication, QHBoxLayout,
                             QVBoxLayout, QFrame, QStatusBar)

import CmdlineOptions as Clo
import Constants as Kst
from EventLoopSocket import EventLoopDataRecvMgr
import RtData
import frm_MirrorFrame
import frm_SHFrame
import frm_TTPlotFrame
import frm_ChartsFrame
import Labels
import Constants as Kst
import Logger
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
    Clo.prn_options()


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class mainWindow(QMainWindow):

    def __init__(self, parent=None):

        super(mainWindow, self).__init__(parent)

        if Clo.version:
            print("Realtime Monitor Version %s" % Kst.VERSION)
            sys.exit()

        print("||||||||||||||||||||||||||||||||||||||||||||")
        print("||||||||||||  RTM V%s START |||||||||||||||" % Kst.VERSION)
        print("||||||||||||||||||||||||||||||||||||||||||||")

        self.debug = int(
                bool(Clo.debug)
        )  # commandline debug value # bool(None) legal but not int(None)
        if Clo.debug:
            Clo.prn_options()  # If debug, list commandline options

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
        self.logger = Logger.Logger(logpath, nfiles=5, level='INFO',
                                    debug=self.debug)
        logpath = self.logger.logpath  # logpath from logger
        self.log = self.logger.lg  # 's.lg' will be python logging system
        assert self.log is not None  # type guard

        self.logger.setLevel('INFO')  # set console & file logging level

        # Now that we have logging, write startup banner to logfile
        self.logger.set_console_level(
                'ERROR')  # don't write this to stdout again
        self.log.info("\n\n")
        self.log.info("||||||||||||||||||||||||||||||||||||||||||||||||")
        self.log.info("||||||||||||||   RTM V%s START   ||||||||||||||" %
                      Kst.VERSION)
        self.log.info("||||||||||||||||||||||||||||||||||||||||||||||||\n")
        self.logger.set_console_level(
                self.logger.level)  #restore console logging level

        # Configure all other startup-values from a config file (Kst.CONFIGFILE)
        Configurer.Configurer(Kst.CONFIGFILE, logpath, self.log)
        cfg = Configuration.cfg
        cfg.logpath = self.logger.logpath
        self.log.info("o Invoked as               : %s" % cfg.execname)
        self.log.info("o Executable is            : %s" % cfg.execpath)
        self.log.info("o Executing from Directory : %s" % cfg.execdir)
        self.log.info("o Working Directory is     : %s" % cfg.cwd)
        self.log.info("o Logging to file          : %s" % cfg.logpath)

        #s.lg.info("o QWT VERSION:", Qwt.
        #s.lg.info("o Executable directory    : %s" % cfg.execDir)
        #s.lg.info("o Configuration Path      : %s" % cfg.configpath)

        # mainwin status bar
        cfg.statusBar = QStatusBar()
        cfg.statusBar = self.statusBar
        #cfg.statusBar().showMessage('Status messages will be displayed here')

        # debug level is set from the command-line  --debug option
        if cfg.debug:
            self.log.info(" o Debug level:%d" % cfg.debug)

        # if debug-level > 1,  print configuration
        if cfg.debug > 1 or cfg.verbose:
            cfg.prn_cfg()

        # Set background-color & font. Use a monospace font for readable values
        self.setStyleSheet("QMainWindow{ background-color: %s }" %
                           Kst.MWINBKGCOLOR)
        self.setFont(QFont("Monospace"))
        self.font = self.font()
        # s.font.setPointSize(8)

        # set main window Title
        self.setWindowTitle("RealTime Data Monitor")

        # Main Windowframe
        frm = QFrame()  #frm    = QFrame(s)
        frm.setFrameStyle(QFrame.Box)
        frm.setFrameShadow(QFrame.Sunken)

        #frm.setMidLineWidth(1)
        frm.setLineWidth(1)
        self.setCentralWidget(frm)  # set frame as mainwin central widget

        #s.setMenuBar(Menubar(s))   # set a menubar in main window
        self.toolbar = toolbar.Toolbar(self)
        self.addToolBar(self.toolbar)

        #.......................................................................
        # Create subframes & their widgets
        self.Dmf1 = frm_MirrorFrame.MirrorFrame('DM')  # Dm Eye
        self.Crvf2 = frm_MirrorFrame.MirrorFrame('Curvature')  # Curvature Eye
        self.Apdf3 = frm_MirrorFrame.MirrorFrame('HOWFS/APD')  # Apd Eye
        self.Shf4 = frm_SHFrame.SHFrame('LOWFS/SH')  # S.Hartmann Eye
        self.Ttf5 = frm_TTPlotFrame.TTPlotFrame(
                'TipTilt Mount')  # TipTilt plots
        self.Chf6 = frm_ChartsFrame.ChartsFrame('ChartsFrame')  # stripcharts
        self.Lbf7 = Labels.GainsLabelFrame()

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
        topLayout.addWidget(self.Dmf1)
        topLayout.addWidget(self.Crvf2)
        topLayout.addWidget(self.Apdf3)
        topLayout.addWidget(self.Shf4)

        #.......................................................................
        botLeftLayout.addWidget(self.Chf6)

        botRightLayout.addWidget(self.Ttf5)
        botRightLayout.addWidget(self.Lbf7)
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
        self.rtData = RtData.RtData(self)

        # Connect Eyeball data-handlers
        self.rtData.EyeDataReady.connect(self.Dmf1.mrr.data_ready)
        self.rtData.connect(self.rtData, SIGNAL('EyeDataReady'),
                            self.Dmf1.mrr.data_ready)

        self.rtData.connect(self.rtData, SIGNAL('EyeDataReady'),
                            self.Crvf2.mrr.data_ready)

        self.rtData.connect(self.rtData, SIGNAL('EyeDataReady'),
                            self.Apdf3.mrr.data_ready)

        self.rtData.connect(self.rtData, SIGNAL('SHEyeDataReady'),
                            self.Shf4.shw.data_ready)

        #........................................................................
        # Connect labelled-data handlers
        #........................................................................
        # Dm labels
        self.rtData.connect(self.rtData, SIGNAL('LabelDataReady'),
                            self.Dmf1.labelsFrame.data_ready)

        # Crv labels
        self.rtData.connect(self.rtData, SIGNAL('LabelDataReady'),
                            self.Crvf2.labelsFrame.data_ready)

        # Apd labels
        self.rtData.connect(self.rtData, SIGNAL('LabelDataReady'),
                            self.Apdf3.labelsFrame.data_ready)

        # Sh labels
        self.rtData.connect(self.rtData, SIGNAL('LabelDataReady'),
                            self.Shf4.labelsFrame.data_ready)

        # Remaining labels
        self.rtData.connect(self.rtData, SIGNAL('LabelDataReady'),
                            self.Lbf7.data_ready)

        # Shack-Hartmann defocus indicator
        self.rtData.connect(self.rtData, QtCore.SIGNAL('SHArrowDataReady'),
                            self.Shf4.defocus_data_ready)

        # Mirror frame defocus indicators
        self.rtData.connect(self.rtData, QtCore.SIGNAL('DefocusDataReady'),
                            self.Dmf1.defocus_data_ready)

        # Curvature frame defocus indicator
        self.rtData.connect(self.rtData, QtCore.SIGNAL('DefocusDataReady'),
                            self.Crvf2.defocus_data_ready)

        # tt plot Mount plots
        self.rtData.connect(self.rtData, QtCore.SIGNAL('MountPlotDataReady'),
                            self.Ttf5.data_ready)

        # Stripcharts
        self.rtData.connect(self.rtData, QtCore.SIGNAL('ChartDataReady'),
                            self.Chf6.data_ready)

        if cfg.debug:
            self.log.info(" o Debug          : %d" % (cfg.debug))
        if cfg.test:
            self.log.info(" o Test           : %d" % (cfg.test))

        # Server Socket: create socket, listen for connect in qt eventloop
        # call data_handler when data source connects
        try:
            self.zmq_subber = EventLoopDataRecvMgr(self.rtData.data_handler,
                                                   cfg.rtDataHost,
                                                   cfg.rtDataPort)
        except Exception as e:
            self.log.error("Could not create data socket:%s Goodbye..." % e)
            sys.exit(-1)

        self.zmq_subber.name = "Rtm Monitor Data Socket"

        # pass toolbar-Slot to Lskt's connected-socket signal
        # must be called after socket is 'activated'
        self.zmq_subber.setConnectObject(self.toolbar.set_conBtnState)

        self.log.info(
                "o Listening for zmq PUB traffic from AORTS port        : %d" %
                (cfg.rtDataPort))

        self.toolbar.setPlotFrame(self.Chf6)

        cfg.zmq_subber = self.zmq_subber  ###!

    # called on window close
    def closeEvent(s, ev):

        #if s.Lskt.connected_skt is not None:

        s.log.info("||||||||||||||||||||||||||||||||||||||||||||||||")
        s.log.info("||||||||||||||   RTM V%s END     ||||||||||||||" %
                   Kst.VERSION)
        s.log.info("||||||||||||||||||||||||||||||||||||||||||||||||\n")


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
