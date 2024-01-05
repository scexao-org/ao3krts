#===============================================================================
# File : rtData.py
#      : Data handler for AO 188 mirror gui
#
# Notes:
# telnet 10.0.0.6 25010
#Trying 10.0.0.6...
#Connected to 10.0.0.6.
#Escape character is '^]'.
#cntmongui connect
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
from PyQt5.QtCore import QObject
import sys
import numpy as np
import configuration
import constants as Kst

DATA_HEADER_CHARS = 32
DATA_GEN_NITEMS = 32
DATA_DM_NITEMS = 210
DATA_CRV_NITEMS = 210
DATA_HOWFS_APD_NITEMS = 210
DATA_LOWFS_SH_NITEMS = 60
DATA_TT_NITEMS = 20
DATA_MAX_CHARS_PER_ITEM = 7
DATA_TOTAL_ITEMS        = DATA_GEN_NITEMS+DATA_DM_NITEMS+DATA_CRV_NITEMS + \
    DATA_HOWFS_APD_NITEMS + DATA_LOWFS_SH_NITEMS + \
    DATA_TT_NITEMS + DATA_HEADER_CHARS


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class rtData(QObject):

    def __init__(self, parent=None):
        self.cfg = configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<rtData.__init__>")

        super(rtData, self).__init__(parent)
        self.hist = False
        self.chunksize = Kst.RTDATACHUNKSIZE  # ~ 5000
        self.frameN = 0  # frame number sent by RTdata
        self.frameCount = 0  # our count

    #---------------------------------------------------------------------------
    def data_handler(self, bytes_buffer):
        #.......................................................................
        # Read string data from socket
        #.......................................................................
        if (self.cfg.debug >= 5): print("rtData.data_handler")

        #.......................................................................
        if bytes_buffer == b"":  # if nothing, return
            self.cfg.lg.info("Bytes buffer empty...\n")
            return None

        #.......................................................................
        # Convert remainder of datastring to a numpy float array
        #  type:'numpy.ndarray'
        #.......................................................................
        self.fdata = np.frombuffer(bytes_buffer, '<f4', count=660)

        # Get Frame Number.
        self.frameN = int(self.fdata[Kst.GENDATASTART +
                                     Kst.FRAME_NUMBER])  # frame number
        if self.frameN == 0:
            self.lg.info("Rx'd frame zero. Reset Frame Count")
            self.frameCount = 0

        self.frameCount += 1

        if self.cfg.test == 1:
            print("Frame No:%d" % (self.frameN), '\r', end=' ')
            sys.stdout.flush()

        # dump data to stdout if debug value high enough
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            DmData = self.fdata[Kst.DM_CELLDATASTART:Kst.DM_CELLDATAEND]
            CrvData = self.fdata[Kst.CRV_CELLDATASTART:Kst.CRV_CELLDATAEND]
            ApdData = self.fdata[Kst.APD_CELLDATASTART:Kst.APD_CELLDATAEND]
            ShData = self.fdata[Kst.SH_CELLDATASTART:Kst.SH_CELLDATAEND]
            GenData = self.fdata[Kst.GENDATASTART:Kst.GENDATAEND]

            print("...................................................")
            print("                  Frame:", self.frameN)
            print("...................................................")
            print("Data Header:", HeaderData)
            print("ID:", IdString, "Frame:", self.frameN)
            print("...................................................")
            print("Dm Data:")
            print(DmData)
            print("...................................................")
            print("Crv Data:")
            print(CrvData)
            print("...................................................")
            print("Apd Data:")
            print(ApdData)
            print("...................................................")
            print("SH  Data:")
            print(ShData)
            print("...................................................")
            print("Gen Data:")
            print(GenData)
            print("...................................................")

        if self.frameN % self.cfg.framesPerEye == 0:
            self.emit(SIGNAL('EyeDataReady'), self.fdata)

        if self.frameN % self.cfg.framesPerLabel == 0:
            self.emit(SIGNAL('LabelDataReady'), self.fdata)

        if self.frameN % self.cfg.framesPerChart == 0:
            self.emit(SIGNAL('ChartDataReady'), self.fdata)

        if self.frameN % self.cfg.framesPerMountPlot == 0:
            self.emit(SIGNAL('MountPlotDataReady'), self.fdata)

        if self.frameN % self.cfg.framesPerSH == 0:
            self.emit(SIGNAL('SHEyeDataReady'), self.fdata)

        if self.frameN % self.cfg.framesPerSHArrow == 0:
            self.emit(SIGNAL('SHArrowDataReady'), self.fdata)
            # Also SH defocus indicator

        if self.frameN % self.cfg.framesPerDefocusUpdate == 0:
            self.emit(SIGNAL('DefocusDataReady'), self.fdata)

        return True

    #---------------------------------------------------------------------------
    # connect data ready signal to data sinks as instructed
    # s.connect (s, SIGNAL(sig), handler) # Good #1
    #def connect_handler(s, sig, handler):
    #     if s.cfg.debug:
    #         print("rtData.connect_handler")
    #     s.connect (s, QtCore.SIGNAL(sig), handler)
