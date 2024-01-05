#!/usr/bin/python
""" Quick and dirty data simulator for AO realtime-monitor
"""

#^==============================================================================
# FILE: simdata.py
#     : Quick and dirty data simulator for AO realtime-monitor
#       Sends data to given host at given port @ approx 10 Hz
#     : Constants from Constants.py
#
# Options:
#  -h, --help         show this help message and exit
#  --logpath=LOGPATH  Set logfile path
#  --libpath=LIBPATH  Set library path
#  --debug=DEBUG      Set debug level 1-10
#  --verbose=VERBOSE  Set verbosity level 1-10
#  --test=TEST        set test number
#  -V                 Print version number and quit
#  --host=HOST        set host.          Exp: '--host 'localhost'
#  --port=PORT        set RTS data port. Exp: '--port NUMBER'
#===============================================================================
from __future__ import absolute_import, print_function, division
import sys, random, time
import socket

import CmdlineOptions as opts
import numpy as np
import Constants as Kst

# Test numbers
TEST_NOCONNECT = 0  # Generate & dump data but no connection, no send.
TEST_SAFETY_ALARMS = 2  # test safety alarms
TEST_LGSMODE = 7  #


#------------------------------------------------------------------------------
# class DataSource(object)
#
# server host = 'localhost'
# server port = PORT
# user ports should be > 1024
# connect via: telnet 127.0.0.1 12345
#------------------------------------------------------------------------------
class DataSource(object):

    def __init__(self):
        self.debug = opts.debug
        if self.debug: print("<DataSource.__init__>")
        #............................................................
        super(DataSource, self).__init__()

        self.skt = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM)  # create a TCP socket
        self.serverHost = None  # servername is localhost
        self.serverPort = None  # use arbitrary port > 1024
        self.rxData = []
        self.frameN = 0
        self.DataStr = ' '

        self.safety1count = 0
        self.safety2count = 0
        self.defocusCount = 0
        self.tfnCount = 0  # random true/false/negative

    #-----------------------------------------------------------------------
    def connect(self, host, port):
        """connect to given server on given port"""
        print("** Connecting on port:", port)
        if port <= Kst.RESERVEDPORTSTOP:
            print("** Error: Port must be greater than 1024 **")
            print("Goodbye...")
            sys.exit(0)

        try:
            self.skt.connect((host, int(port)))
        except Exception as e:
            print("** Connect exception for host:%s port:%d %s" %
                  (host, port, e))
            print("Goodbye...")
            sys.exit(0)

        self.serverHost = host  # servername is localhost
        self.serverPort = port
        print("Connected to host:%s on port:%s" % (host, port))

    #-----------------------------------------------------------------------
    def readServer(self, ntoread=1024):
        print("Read Socket")
        try:
            self.rxData = self.skt.recv(ntoread)
        except Exception as e:
            print("** Socket Read Exception:", e)
            return None

        print("rxData:", self.rxData)
        return (self.rxData)

    #-----------------------------------------------------------------------
    def sendData(self):
        try:
            self.skt.sendall(self.DataStr)
        except Exception as e:
            print("** Socket Write Exception:", e)
            print("** Goodbye **")
            sys.exit(0)
            return

    #-----------------------------------------------------------------------
    def meterData(self):
        self.sendData()

    #-----------------------------------------------------------------------
    #    Min      = ShData.min()
    #    Max      = ShData.max()
    #    Var      = ShData.var()
    #    AvgCount = ShData.mean() # ??? count
    #    AvgMag   = ShData.mean() # ??? magnitude

    def fakeData(self, verbose=False):

        self.DataStr = GenDataStr = DmDataStr = CrvDataStr = ApdDataStr = ShDataStr = ""
        #.......................................................................
        # ID / COMMAND SECTION: 32 characters. 'AORTS' must be first 5 chars
        #.......................................................................
        HeaderStr = 'AORTS                          '

        # dm,crv,apd,sh data
        dm_cellData = np.random.uniform(51, -62, size=188)
        #crv_cellData = np.random.uniform(Kst.CRVMIN,Kst.CRVMAX,size=188)
        crv_cellData = np.random.uniform(-0.035, 0.024, size=188)
        apd_cellData = np.random.uniform(60, 114, size=188)
        sh_cellData = np.random.uniform(0, 0.12, size=16)
        GenData = np.zeros(Kst.GENDATASZ)
        if self.debug:
            print("Gendata len:", len(GenData))

        #
        GenData[Kst.FRAME_NUMBER] = self.frameN
        GenData[Kst.VMDRIVE] = 1
        #GenData[Kst.VMDRIVE             ] = s.randomTrueFalseNeg() # 0,1,-1
        GenData[Kst.VMFREQ] = Kst.VMFREQ
        GenData[Kst.VMVOLT] = Kst.VMVOLT
        GenData[Kst.VMPHASE] = Kst.VMPHASE
        #GenData[Kst.LOOPSTATUS          ] = s.randomTrueFalseNeg() # 0,1,-1
        GenData[Kst.LOOPSTATUS] = 1
        GenData[Kst.DMGAIN] = Kst.DMGAIN
        GenData[Kst.DMGAINHOLD] = Kst.DMGAINHOLD
        GenData[Kst.TTGAIN] = Kst.TTGAIN
        GenData[Kst.TTGAINHOLD] = Kst.TTGAINHOLD
        GenData[Kst.PSUBGAIN] = Kst.PSUBGAIN
        GenData[Kst.PSUBGAINHOLD] = Kst.PSUBGAINHOLD
        GenData[Kst.STTGAIN] = Kst.STTGAIN
        GenData[Kst.STTGAINHOLD] = Kst.STTGAINHOLD
        GenData[Kst.HTTGAIN] = Kst.HTTGAIN
        GenData[Kst.HDFGAIN] = Kst.HDFGAIN
        GenData[Kst.LTTGAIN] = Kst.LTTGAIN
        GenData[Kst.LDFGAIN] = Kst.LDFGAIN
        GenData[Kst.WTTGAIN] = Kst.WTTGAIN
        GenData[Kst.ADFGAIN] = Kst.ADFGAIN
        GenData[Kst.CTRLMTRXSIDE] = 1 if opts.test == TEST_LGSMODE else 0
        GenData[Kst.APDSAFETY] = self.randomSafety1(50)
        GenData[Kst.DMSAFETY] = self.randomSafety2(50)
        GenData[Kst.DM_CELLDATAMIN] = dm_cellData.min()
        GenData[Kst.DM_CELLDATAMAX] = dm_cellData.max()
        GenData[Kst.DM_CELLDATAVAR] = dm_cellData.var()
        GenData[Kst.DM_CELLDATAAVG] = dm_cellData.mean()
        GenData[Kst.DM_TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.DM_TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.DM_TTMODEVAR] = Kst.DM_TTMODEVAR
        GenData[Kst.DM_DEFOCUS] = self.randomDefocus()
        GenData[Kst.DM_DEFOCUSVAR] = Kst.DM_DEFOCUSVAR
        GenData[Kst.DM_FLATVAR] = random.uniform(-1, 1)
        GenData[Kst.DM_TIMEVAR] = Kst.DM_TIMEVAR
        GenData[Kst.DM_TTMOUNTX] = random.uniform(-9, 9)
        GenData[Kst.DM_TTMOUNTY] = random.uniform(-9, 9)
        GenData[Kst.DM_TTMOUNTVAR] = Kst.DM_TTMOUNTVAR
        GenData[Kst.DM_TTMOUNTFLATVAR] = Kst.DM_TTMOUNTFLATVAR
        GenData[Kst.DM_TTMOUNTTIMEVAR] = Kst.DM_TTMOUNTTIMEVAR
        GenData[Kst.CRV_CELLDATAMIN] = crv_cellData.min()
        GenData[Kst.CRV_CELLDATAMAX] = crv_cellData.max()
        GenData[Kst.CRV_CELLDATAVAR] = crv_cellData.var()
        GenData[Kst.CRV_CELLDATAAVG] = crv_cellData.mean()
        GenData[Kst.CRV_TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.CRV_TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.CRV_TTMODEVAR] = Kst.CRV_TTMODEVAR
        GenData[Kst.CRV_DEFOCUS] = self.randomDefocus()
        GenData[Kst.CRV_DEFOCUSVAR] = Kst.CRV_DEFOCUSVAR
        GenData[Kst.CRV_FLATVAR] = Kst.CRV_FLATVAR
        GenData[Kst.CRV_TIMEVAR] = Kst.CRV_TIMEVAR
        GenData[Kst.CRV_WAVEFRONTERROR] = random.uniform(-1, 1)
        GenData[Kst.APD_CELLDATAMIN] = apd_cellData.min()
        GenData[Kst.APD_CELLDATAMAX] = apd_cellData.max()
        GenData[Kst.APD_CELLDATAVAR] = apd_cellData.var()
        GenData[Kst.APD_CELLDATAAVG] = apd_cellData.mean()
        GenData[Kst.APD_RMAGAVG] = Kst.APD_RMAGAVG
        GenData[Kst.LWF_DATAMIN] = sh_cellData.min()
        GenData[Kst.LWF_DATAMAX] = sh_cellData.max()
        GenData[Kst.LWF_DATAVAR] = sh_cellData.var()
        GenData[Kst.LWF_COUNTAVG] = sh_cellData.mean()
        GenData[Kst.LWF_RMAGAVG] = Kst.LWF_RMAGAVG
        GenData[Kst.LWF_TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.LWF_TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.LWF_TTMODEVAR] = Kst.LWF_TTMODEVAR
        GenData[Kst.LWF_DEFOCUS] = self.randomDefocus()
        GenData[Kst.LWF_DEFOCUSVAR] = Kst.LWF_DEFOCUSVAR

        GenData[Kst.SH_Q1TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.SH_Q1TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.SH_Q2TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.SH_Q2TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.SH_Q3TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.SH_Q3TTMODEY] = random.uniform(-1, 1)
        GenData[Kst.SH_Q4TTMODEX] = random.uniform(-1, 1)
        GenData[Kst.SH_Q4TTMODEY] = random.uniform(-1, 1)

        GenData[Kst.WFS_TTCH1] = random.uniform(0, 10)
        GenData[Kst.WFS_TTCH2] = random.uniform(0, 10)
        GenData[Kst.WFS_VAR] = Kst.WFS_VAR
        GenData[Kst.IRM2TTX] = Kst.IRM2TTX
        GenData[Kst.IRM2TTY] = Kst.IRM2TTY
        GenData[Kst.IRM2TTVAR] = Kst.IRM2TTVAR

        for v in dm_cellData:
            DmDataStr += " %.2f" % v
        for v in crv_cellData:
            CrvDataStr += " %.2f" % v
        for v in apd_cellData:
            ApdDataStr += " %.2f" % v
        for v in sh_cellData:
            ShDataStr += " %.2f" % v

        GenDataStr += " %d" % GenData[
                Kst.FRAME_NUMBER]  # Frame No. is an integer
        for v in GenData[1:]:
            GenDataStr += " %.2f" % v

        if self.debug:
            print("GendataStr len:", len(GenDataStr))

        if verbose:
            print("----------------------------------------------------")
            print("             Frame:", self.frameN)
            print("----------------------------------------------------")
            print('Header :[', HeaderStr, ']')
            print("....................................................")
            print('DM     :[', DmDataStr, ']')
            print("....................................................")
            print('CRV    :[', CrvDataStr, ']')
            print("....................................................")
            print('APD    :[', ApdDataStr, ']')
            print("....................................................")
            print('SH     :[', ShDataStr, ']')
            print("....................................................")
            print('General:[', GenDataStr, ']')
            print("....................................................")
            #print('Data   :[',s.Data,']')
            print("....................................................")

        self.DataStr = HeaderStr  + DmDataStr + CrvDataStr + \
                    ApdDataStr + ShDataStr + GenDataStr

        if self.debug:
            print("DataStr len:", len(self.DataStr))

        ConstantDataStrLength = 5000
        rump = ConstantDataStrLength - len(self.DataStr)

        for i in range(rump):
            self.DataStr += ' '

        if self.debug:
            print("DataStr len:", len(self.DataStr))

        self.frameN += 1

    #-----------------------------------------------------------------------
    def set_timer(self, interval):
        print("< set_timer >")
        self.timer.setInterval(interval)
        self.timer.start()

    #-----------------------------------------------------------------------
    def timer_handler(self):

        self.colormap[self.ndx] = self.color
        self.ndx = self.ndx + 1
        if self.ndx >= 188:
            self.ndx = 0
            #if s.color == s.color00:
            #    s.color = s.color01
            #elif s.color == s.color01:
            #    s.color = s.color00
        #s.repaint()

    #-----------------------------------------------------------------------
    #  0,1,-1
    #-----------------------------------------------------------------------
    def randomTrueFalseNeg(self):

        #s.tfnCount += 1
        #if s.tfnCount > 50:
        #    s.tfnCount = 0

        r = random.uniform(0, 100)

        if r > 30:
            return 1
        elif r <= 30 and r > 10:
            return 0
        else:
            return -1

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def randomDefocus(self):

        if self.defocusCount < 20:
            x = random.uniform(-0.1, 0.1)
        else:
            x = random.uniform(-1000, 1000)
            if self.defocusCount >= 40:
                self.defocusCount = 0

        self.defocusCount += 1
        return x

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def randomSafety1(self, n):
        if opts.test != TEST_SAFETY_ALARMS:
            return 0
        # keep safety on for N counts
        if self.safety1count:
            self.safety1count += 1
            if self.safety1count >= n:
                self.safety1count = 0
                return 0  # safety off
            else:
                return 1  # safety on

        self.safety1count = randomXY(0, 1,
                                     99)  # return 0 99 percent of the time
        return self.safety1count

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def randomSafety2(self, n):
        if opts.test != TEST_SAFETY_ALARMS:
            return 0
        # keep safety on for N counts
        if self.safety2count:
            self.safety2count += 1
            if self.safety2count >= n:
                self.safety2count = 0
                return 0  # safety off
            else:
                return 1  # safet on

        self.safety2count = randomXY(0, 1, 99)  # return 0 99percent of the time
        return self.safety2count


# return x a weighted number of times, else return y
def randomXY(x, y, weight):
    n = np.random.uniform(0, 100)
    if n <= weight:
        return x
    return y


#^------------------------------------------------------------------------------
# Commandline options
#  --test = 0, --verbose = 1  : don't send data, just display it
#
#-------------------------------------------------------------------------------
if __name__ == "__main__":

    print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    print("||||||||||||||||||  simdata  |||||||||||||||||||||||||||||||")
    print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
    print("")

    if opts.version:
        print("realtime-monitor data simulator Version: 1.0")
        print("")
        sys.exit()

    if opts.tests:
        print("--------------- Tests -----------------------")
        print("Generate & dump data but no connection, no send:",
              TEST_NOCONNECT)
        print("Test safey alarms                              :",
              TEST_SAFETY_ALARMS)
        print("set laser-guidestar mode                      :", TEST_LGSMODE)
        sys.exit()

    # args
    if opts.host is None:
        host = 'localhost'
    else:
        host = opts.host

    if opts.port is None:
        port = int(Kst.DFLT_DATAPORT)
    else:
        port = opts.port

    # create fake data
    dtasrc = DataSource()

    # Establish socket connection to host
    if opts.test != TEST_NOCONNECT:
        print("Connecting to host: %s  port:%d" % (host, port))
        dtasrc.connect(host, port)
        dtasrc.readServer()

    # Loop, sending data at 1/interval Hz
    #interval = 0.10
    interval = 0.1
    i = 0
    while True:
        i = i + 1
        time.sleep(interval)
        print("Send:", i, '\r', end=' ')
        sys.stdout.flush()
        dtasrc.fakeData(verbose=opts.verbose)
        if opts.test != TEST_NOCONNECT:
            dtasrc.sendData()

        #if i > 40:
        #    time.sleep(2)
        #    i = 0
