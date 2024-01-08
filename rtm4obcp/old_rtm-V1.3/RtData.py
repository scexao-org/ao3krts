#===============================================================================
# File : RtData.py
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
from PyQt4.QtCore import (Qt, SIGNAL, SLOT, QString, QObject, QTimer)
import sys
import numpy as np
import Configuration
import Constants as Kst

DATA_HEADER_CHARS = 32
DATA_GEN_NITEMS = 32
DATA_DM_NITEMS = 210
DATA_CRV_NITEMS = 210
DATA_HOWFS_APD_NITEMS = 210
DATA_LOWFS_SH_NITEMS = 60
DATA_TT_NITEMS = 20
DATA_MAX_CHARS_PER_ITEM = 7
DATA_TOTAL_ITEMS        = DATA_GEN_NITEMS+DATA_DM_NITEMS+DATA_CRV_NITEMS + \
    DATA_HOWFS_APD_NITEMS+DATA_LOWFS_SH_NITEMS     + \
    DATA_TT_NITEMS + DATA_HEADER_CHARS


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class RtData(QObject):

    def __init__(s, parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<RtData.__init__>")

        super(RtData, s).__init__(parent)
        s.hist = False
        s.chunksize = Kst.RTDATACHUNKSIZE  # ~ 5000
        s.frameN = 0  # frame number sent by RTdata
        s.frameCount = 0  # our count

    #---------------------------------------------------------------------------
    def data_handler(s, skt):
        #.......................................................................
        # Read string data from socket
        #.......................................................................
        if (s.cfg.debug >= 5): print("RtData.data_handler")

        # Read RTData from socket
        try:
            DataString = skt.recv(s.chunksize)
        except Exception, (value, message):
            s.cfg.lg.error("<RtData> Socket read error: %d %s" %
                           (value, message))
            return False

        #.......................................................................
        if DataString == "":  # if nothing, return
            s.cfg.lg.info("Client closed socket?...\n")
            return None

        #.......................................................................
        # Data Header:32 bytes of characters or spaces
        #            First five bytes must = 'AORTS'
        #.......................................................................
        HeaderData = DataString[Kst.HEADER_START:Kst.HEADER_END]
        IdString = HeaderData[0:5]  # Unused

        #.......................................................................
        # Convert remainder of datastring to a numpy float array
        #  type:'numpy.ndarray'
        #.......................................................................
        s.fdata = np.fromstring(DataString[32:(s.chunksize - 32)], dtype=float,
                                sep=' ')

        # Get Frame Number.
        s.frameN = int(s.fdata[Kst.GENDATASTART +
                               Kst.FRAME_NUMBER])  # frame number
        if s.frameN == 0:
            s.lg.info("Rx'd frame zero. Reset Frame Count")
            s.frameCount = 0

        s.frameCount += 1

        if s.cfg.test == 1:
            print("Frame No:%d" % (s.frameN), '\r', end=' ')
            sys.stdout.flush()

        # dump data to stdout if debug value high enough
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            DmData = s.fdata[Kst.DM_CELLDATASTART:Kst.DM_CELLDATAEND]
            CrvData = s.fdata[Kst.CRV_CELLDATASTART:Kst.CRV_CELLDATAEND]
            ApdData = s.fdata[Kst.APD_CELLDATASTART:Kst.APD_CELLDATAEND]
            ShData = s.fdata[Kst.SH_CELLDATASTART:Kst.SH_CELLDATAEND]
            GenData = s.fdata[Kst.GENDATASTART:Kst.GENDATAEND]

            print("...................................................")
            print("                  Frame:", s.frameN)
            print("...................................................")
            print("Data Header:", HeaderData)
            print("ID:", IdString, "Frame:", s.frameN)
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

        if not s.frameN % s.cfg.framesPerEye:
            s.emit(SIGNAL('EyeDataReady'), s.fdata)

        if not s.frameN % s.cfg.framesPerLabel:
            s.emit(SIGNAL('LabelDataReady'), s.fdata)

        if not s.frameN % s.cfg.framesPerChart:
            s.emit(SIGNAL('ChartDataReady'), s.fdata)

        if not s.frameN % s.cfg.framesPerMountPlot:
            s.emit(SIGNAL('MountPlotDataReady'), s.fdata)

        if not s.frameN % s.cfg.framesPerSH:
            s.emit(SIGNAL('SHEyeDataReady'), s.fdata)

        if not s.frameN % s.cfg.framesPerSHArrow:
            s.emit(SIGNAL('SHArrowDataReady'), s.fdata)
            # Also SH defocus indicator

        if not s.frameN % s.cfg.framesPerDefocusUpdate:
            s.emit(SIGNAL('DefocusDataReady'), s.fdata)

        return True

    #---------------------------------------------------------------------------
    # connect data ready signal to data sinks as instructed
    # s.connect (s, SIGNAL(sig), handler) # Good #1
    #def connect_handler(s, sig, handler):
    #     if s.cfg.debug:
    #         print("RtData.connect_handler")
    #     s.connect (s, QtCore.SIGNAL(sig), handler)
