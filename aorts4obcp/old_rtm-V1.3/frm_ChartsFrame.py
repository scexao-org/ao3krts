#===============================================================================
# File : Plotframe.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

import Constants as Kst
import Configuration
from PyQt4.QtCore import (Qt, QRect, SIGNAL, QString, QDateTime, QTime,
                          QDateTime)
from PyQt4.QtGui import (QColor,QWidget,QFrame,QLabel,QStyleOption, \
       QGridLayout, QHBoxLayout,QVBoxLayout,QSizePolicy,QSplitter,  \
       QMenuBar,QMenu,QAction, \
       QButtonGroup,QRadioButton,QLCDNumber,QPalette,QColor,QDial,QPushButton)
import Stripchart

from PyQt4.QtCore import Qt
import PyQt4.Qwt5 as Qwt
#from PyQt4.Qwt5.anynumpy import *
from numpy import zeros
import numpy as np
import timeUtil as tUtil


#------------------------------------------------------------------------------
# SHFrame
#------------------------------------------------------------------------------
class ChartsFrame(QFrame):

    def __init__(s, name="noname", parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.lg.debug("<SHFrame.__init__>:%s" % name)
        #............................................................
        super(ChartsFrame, s).__init__(parent)

        s.name = name
        s.setMaximumSize(900, 600)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # hrz,vrt
        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)

        s.layout = QGridLayout()
        s.displayPerNframes = 10
        s.MaxLedHeight = 30
        s.MaxLabelHeight = 12

        # get/set Timezone for stripchart labels
        s.timeSpec = tUtil.zoneToSpec(
                s.cfg.cfgD['gen']['stripchartTzone']['value'])
        # hack the time now
        if s.timeSpec == Qt.UTC:
            s.lg.info("o Charts timeZone is       : UTC")
            s.qdt0 = QDateTime().currentDateTimeUtc()
        else:
            s.lg.info("o Charts timeZone is       : LOCAL TIME")
            s.qdt0 = QDateTime().currentDateTime()

        #............................................................
        # Plots
        #............................................................

        # current y-value of the four stripcharts
        s.y1 = s.y2 = s.y3 = s.y4 = s.apdRmag = s.ShRmag = 0

        s.pwdg1 = Stripchart.Stripchart(name='APD Count high-order WFS',
                                        qtt=s.qdt0, chartNumber=1)

        s.pwdg2 = Stripchart.Stripchart(name='APD Count low-order WFS',
                                        qtt=s.qdt0, chartNumber=2)

        s.pwdg3 = Stripchart.Stripchart(name='Wavefront Error', qtt=s.qdt0,
                                        chartNumber=3)

        s.pwdg4 = Stripchart.Stripchart(name='Dm Variance', qtt=s.qdt0,
                                        chartNumber=4)

        # X/Y Mouse plot-coordinate labels
        s.lblX = QLabel(QString('123.456'))
        s.lblY = QLabel(QString('789.123'))
        s.lblX.setMinimumHeight(18)
        s.lblY.setMinimumHeight(18)
        s.lblXYLayout = QHBoxLayout()
        s.lblXYLayout.addWidget(s.lblX)
        s.lblXYLayout.addWidget(s.lblY)

        # 6 lcds display current plot value & two rmag-values
        s.lcd1 = s.lcd()
        s.lcd1b = s.lcd()  # kludged-on APD Rmag: 'apdRmag'

        s.lcd2 = s.lcd()
        s.lcd2b = s.lcd()  # kludged-on Shack-Hartmann Rmag: 'shRmag'

        s.lcd3 = s.lcd()
        s.lcd4 = s.lcd()

        s.lcd1.setToolTip(QString("Current APD Count HOWFS Plot Value "))
        s.lcd1b.setToolTip(QString("Current HOWFS Rmag "))

        s.lcd2.setToolTip(QString("Current APD Count LOWFS Plot Value"))
        s.lcd2b.setToolTip(QString("Current LOWFS Rmag"))

        s.lcd3.setToolTip(QString("Current Wavefront Error Plot Value "))
        s.lcd4.setToolTip(QString("Current DM Variance Plot Value "))

        # labels for the leds
        s.lbl1 = s.makeLabel('Howfs Count')
        s.lbl1b = s.makeLabel('Howfs Rmag')
        s.lbl2 = s.makeLabel('Lowfs Count')
        s.lbl2b = s.makeLabel('Lowfs Rmag')
        s.lbl3 = s.makeLabel('Wavefront Error')
        s.lbl4 = s.makeLabel('Dm Variance')

        hrzPolicy = QSizePolicy.Expanding
        vrtPolicy = QSizePolicy.Expanding
        s.pwdg1.setSizePolicy(hrzPolicy, vrtPolicy)
        s.pwdg2.setSizePolicy(hrzPolicy, vrtPolicy)
        s.pwdg3.setSizePolicy(hrzPolicy, vrtPolicy)
        s.pwdg4.setSizePolicy(hrzPolicy, vrtPolicy)

        #............................................................
        # Create 3 HMS buttons for chart scale
        s.btnGroup = QButtonGroup()
        s.btnGroup.setExclusive(True)

        s.rBtn1 = QRadioButton("h")
        s.rBtn2 = QRadioButton("m")
        s.rBtn3 = QRadioButton("s")

        s.btnGroup.addButton(s.rBtn1)
        s.btnGroup.addButton(s.rBtn2)
        s.btnGroup.addButton(s.rBtn3)
        s.connect(s.btnGroup, SIGNAL('buttonClicked(int)'),
                  s.btnHandler_plotTime)
        s.btnLayout = QHBoxLayout()
        s.btnLayout.addWidget(s.rBtn1)
        s.btnLayout.addWidget(s.rBtn2)
        s.btnLayout.addWidget(s.rBtn3)

        s.rBtn1.setToolTip(QString("Set HOURS scale"))
        s.rBtn2.setToolTip(QString("Set MINUTES scale"))
        s.rBtn3.setToolTip(QString("Set SECONDS scale"))

        #                             row,column, rowSpan, columnSpan,
        lblRspan = 2
        lcdRspan = 6

        plotRspan = 20
        plotCspan = 100
        s.layout.addLayout(s.btnLayout, 1, 0)

        # Fixed Y-scale range-setting:  2 thumbwheels & button for each plot
        s.rangeBtns1Layout = s.make_rangeBtns(
                s.pwdg1, s.cfg.cfgD['stripchart']['chart1'])
        s.rangeBtns2Layout = s.make_rangeBtns(
                s.pwdg2, s.cfg.cfgD['stripchart']['chart2'])
        s.rangeBtns3Layout = s.make_rangeBtns(
                s.pwdg3, s.cfg.cfgD['stripchart']['chart3'])
        s.rangeBtns4Layout = s.make_rangeBtns(
                s.pwdg4, s.cfg.cfgD['stripchart']['chart4'])

        #--- plot 1
        pr = 0 * plotRspan  # row of first column-plot
        r = pr + 2  # row of first column-1 widget
        s.layout.addWidget(s.lbl1, r, 0, lblRspan, 1)

        r += lblRspan
        s.layout.addWidget(s.lcd1, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lcd1b, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lbl1b, r, 0, lblRspan, 1)

        s.layout.addLayout(s.rangeBtns1Layout, pr + 4, 9, 10, 1)  #range buttons

        r += lblRspan
        s.layout.addWidget(s.pwdg1, pr, 10, plotRspan, plotCspan)

        #--- plot 2
        pr = 1 * plotRspan  # row of next column-2 plot
        r = pr + 2  # row of next column-1 widget
        s.layout.addWidget(s.lbl2, r, 0, lblRspan, 1)

        r += lblRspan
        s.layout.addWidget(s.lcd2, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lcd2b, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lbl2b, r, 0, lblRspan, 1)

        s.layout.addLayout(s.rangeBtns2Layout, pr + 4, 9, 10, 1)  #range buttons

        s.layout.addWidget(s.pwdg2, pr, 10, plotRspan, plotCspan)

        #--- plot 3
        pr = 2 * plotRspan  # row of next column2 plot

        r = pr + 6
        s.layout.addWidget(s.lcd3, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lbl3, r, 0, lblRspan, 1)

        s.layout.addLayout(s.rangeBtns3Layout, pr + 4, 9, 10,
                           1)  #range thumbwheels
        s.layout.addWidget(s.pwdg3, pr, 10, plotRspan, plotCspan)

        #--- plot 4
        pr = 3 * plotRspan  # row of next column2 plot

        r = pr + 6
        s.layout.addWidget(s.lcd4, r, 0, lcdRspan, 1)

        r += lcdRspan
        s.layout.addWidget(s.lbl4, r, 0, lblRspan, 1)
        s.layout.addLayout(s.rangeBtns4Layout, pr + 4, 9, 10,
                           1)  #range thumbwheels
        s.layout.addWidget(s.pwdg4, pr, 10, plotRspan, plotCspan)

        # buttons
        #r = pr + 3*plotRspan  # row of next column2 plot
        r = 4 * plotRspan

        # add X & Y mouse coordinates lables
        s.layout.addLayout(s.lblXYLayout, r, 0)

        #s.lbl5   = s.makeLabel("12.34")
        #s.lbl5.setMinimumHeight(18)

        # this fits nicely into ulc of stripchart margin
        #s.layout.addWidget(s.pwdg1.lblX,  0,  14, 1, 1)
        #s.layout.addWidget(s.pwdg1.lblY,  0,  15, 1, 1)

        s.seconds = 0
        s.setLayout(s.layout)

        # Set MINUTES plot scales
        s.pwdg1.setHmsScale(Kst.MINUTES)
        s.pwdg2.setHmsScale(Kst.MINUTES)
        s.pwdg3.setHmsScale(Kst.MINUTES)
        s.pwdg4.setHmsScale(Kst.MINUTES)
        s.rBtn2.setChecked(True)  # check the minutes button

        s.pwdg1.lblX = s.lblX
        s.pwdg1.lblY = s.lblY
        s.pwdg2.lblX = s.lblX
        s.pwdg2.lblY = s.lblY
        s.pwdg3.lblX = s.lblX
        s.pwdg3.lblY = s.lblY
        s.pwdg4.lblX = s.lblX
        s.pwdg4.lblY = s.lblY

        # set timer.  timer-tick drives stripcharts
        s.timerTick = 1  # call timerEvent at one Hertz
        s.y1 = 0
        #**************
        #s.timerTick  = 0.001             #
        #**************

        s.startTimer(s.timerTick * 1000)  # seconds to msecs

    #...........................................................................
    # lcd: create an lcd number display
    # Notes:
    # palette = lcd.palette();
    # palette.setColor( palette.Background, Qt.black )
    # palette.setColor( palette.Foreground, Qt.green )
    # lcd.setPalette( palette );
    # lcd.setSegmentStyle(QLCDNumber.Filled)
    #fg     = " QLCDNumber {color:%s}"%fgclr
    #bg     = " QLCDNumber {background-color:%s}"%bgclr
    #lcd.setStyleSheet(fg+bg)
    def lcd(s):
        lcd = QLCDNumber(5)  # 4 digits or 3 digits 1 decimal-point
        #lcd.setSegmentStyle(QLCDNumber.Flat)
        lcd.setSegmentStyle(QLCDNumber.Filled)
        lcd.setMaximumHeight(s.MaxLedHeight)  # max width,height
        lcd.setStyleSheet("color: rgb(0, 255, 0);\n"
                          "background-color: rgb(0, 0,0);")
        return lcd

    #...........................................................................
    def btnHandler_plotTime(s, x):
        if s.cfg.debug: print("btnHandler_plotTime", x)

        id = s.btnGroup.checkedId()  # which radio button?
        #print("Id:", id)
        # Hours button
        if id == -2:
            s.pwdg1.setHmsScale(Kst.HOURS)
            s.pwdg2.setHmsScale(Kst.HOURS)
            s.pwdg3.setHmsScale(Kst.HOURS)
            s.pwdg4.setHmsScale(Kst.HOURS)

        # Minutes button
        if id == -3:
            s.pwdg1.setHmsScale(Kst.MINUTES)
            s.pwdg2.setHmsScale(Kst.MINUTES)
            s.pwdg3.setHmsScale(Kst.MINUTES)
            s.pwdg4.setHmsScale(Kst.MINUTES)

        # Seconds button
        if id == -4:  # Minutes
            s.pwdg1.setHmsScale(Kst.SECONDS)
            s.pwdg2.setHmsScale(Kst.SECONDS)
            s.pwdg3.setHmsScale(Kst.SECONDS)
            s.pwdg4.setHmsScale(Kst.SECONDS)

    #...........................................................................
    def makeLabel(s, text):
        lbl = QLabel(QString(text))
        fg = " QLabel {color:black}"
        bg = " QLabel {background-color:%s}" % Kst.MWINBKGCOLOR
        border = " QLabel {border-color:%s}" % Kst.MWINBKGCOLOR
        lbl.setStyleSheet(fg + bg + border)
        lbl.setMaximumHeight(s.MaxLabelHeight)
        return (lbl)

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def data_ready(s, data):
        gendata = data[Kst.GENDATASTART:]

        s.y1 = gendata[Kst.APD_CELLDATAAVG]
        s.y2 = gendata[Kst.LWF_COUNTAVG]
        s.y3 = gendata[Kst.CRV_WAVEFRONTERROR]
        s.y4 = gendata[Kst.DM_FLATVAR]

        s.apdRmag = gendata[Kst.APD_RMAGAVG]  # Howfs Rmag
        s.ShRmag = gendata[Kst.LWF_RMAGAVG]  # Lowfs Rmag

    #-----------------------------------------------------------------------
    # timerEvent:  accumulate & display current data at each tick
    #-----------------------------------------------------------------------
    def timerEvent(s, e):

        s.seconds += 1  # seconds from startup

        #*print("Seconds:", s.seconds)
        #*s.y1 += 0.01

        ### shift yv left by 1
        s.pwdg1.plotDatum(s.seconds, s.y1)  # plot apd count howfs
        s.pwdg2.plotDatum(s.seconds, s.y2)  # plot apd count lowfs
        s.pwdg3.plotDatum(s.seconds, s.y3)  # plot wavefront error
        s.pwdg4.plotDatum(s.seconds, s.y4)  # plot Dm Variance

        s.lcd1.display(float(s.y1))  # LCD = apd-howfs count
        s.lcd1b.display(float(s.apdRmag))  # LCD = howfs Rmag (apd Rmag)
        s.lcd2.display(float(s.y2))  # LCD = apd count lowfs
        s.lcd2b.display(float(s.ShRmag))  # LCD = lowfs Rmag (Sh Rmag)
        s.lcd3.display(float(s.y3))  # LCD = wavefront error
        s.lcd4.display(float(s.y4))  # LCD = Dm Variance

    def setPlotRange(s, mode):
        s.pwdg1.setRange(mode)
        s.pwdg2.setRange(mode)
        s.pwdg3.setRange(mode)
        s.pwdg4.setRange(mode)

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def clearPlotHistory(s):
        s.seconds = 0
        s.pwdg1.resetPlot()
        s.pwdg2.resetPlot()
        s.pwdg3.resetPlot()
        s.pwdg4.resetPlot()

    def topWheelHandler(s, value, x):
        print("<topWheelHandler> Value:", value, x)

    def btmWheelHandler(s, value):
        print("<btmWheelHandler> Value:", value)

    # make range Thumb-wheels and connect to plot widgets
    # w1.setStep(step)
    # w1.setTotalAngle(rots * 360.0)
    def make_rangeBtns(s, pwdg, pDct):
        btn1 = QPushButton('A')
        btn1.Xid = 'RB1'  # our tag: range-button-0
        pwdg.autoMinMaxButton = btn1
        btn1.setFixedSize(13, 20)
        btn1.setCheckable(True)
        btn1.setChecked(True)
        btn1.setFlat(True)
        btn1.setStyleSheet("background-color: rgb(0, 255, 0);")
        btn1.setToolTip(QString("Toggle Auto/Fixed Y-axis scale"))

        btn2 = QPushButton('Z')
        btn2.Xid = 'RB2'  # our tag: range-button-0
        btn2.setFixedSize(13, 20)
        btn2.setCheckable(True)
        btn2.setChecked(pDct['zeroScaleBase']['value'])
        btn2.setFlat(True)
        btn2.setStyleSheet("background-color: rgb(0, 255, 0);")
        btn2.setToolTip(QString("Set zero-based Y-Axis scale"))
        layout = QVBoxLayout()

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        s.connect(btn1, SIGNAL('toggled(bool)'), pwdg.fixedScaleHandler)
        s.connect(btn2, SIGNAL('toggled(bool)'), pwdg.fixedScaleHandler)
        return layout


#    def make_rangeWheels(s, pwdg, pDct ):
#        rots = 10
#        step = 1.0
#
#
#        btn1 = QPushButton('A')
#        btn1.Xid = 'RB1' # our tag: range-button-0
#        pwdg.autoscaleButton  = btn1
#        btn1.setFixedSize(14,20)
#        btn1.setCheckable(True)
#        btn1.setChecked(True)
#        btn1.setFlat(True)
#        btn1.setStyleSheet("background-color: rgb(0, 255, 0);")
#        btn1.setToolTip(QString("Toggle Auto/Fixed Y-axis scale"))
#
#        btn2 = QPushButton('Z')
#        btn2.Xid = 'RB2' # our tag: range-button-0
#
#        btn2.setFixedSize(14,20)
#        btn2.setCheckable(True)
#        btn2.setChecked(True)
#        btn2.setFlat(True)
#        btn2.setStyleSheet("background-color: rgb(0, 255, 0);")
#        btn2.setToolTip(QString("Set zero-based Y-Axis scale"))
#
#
#        w1 = Qwt.QwtWheel()
#        pwdg.tw1 = w1
#        w1.Xid = 'TW1'  # our tag : scale-wheel-1
#        w1.setOrientation(Qt.Vertical)
#        w1.setRange(pDct['scaleWheelMin' ]['value'],
#                    pDct['scaleWheelMax' ]['value'],
#                    step)
#
#
#        w1.setValue(pDct['fixedScaleMax']['value'])
#        w1.setFixedSize(10,30) # w,h
#        #s.connect(w1,SIGNAL('valueChanged(double)'),pwdg.topScaleWheelHandler)
#
#        #fg     = " btn {color:black}"
#        #bg     = " btn {background-color:%s}" % '#00FF00'
#        #border = " btn {border-color:%s}" % '#FF0000'
#        #btn.setStyleSheet(fg+bg)
#
#        w2 = Qwt.QwtWheel()
#        pwdg.tw2 = w2
#        w2.Xid = 'TW2'  # our tag : scale-wheel-2
#        w2.setOrientation(Qt.Vertical)
#        w2.setRange(pDct['scaleWheelMin' ]['value'],
#                    pDct['scaleWheelMax' ]['value'],
#                    step)
#
#        #w2.setStep(step)
#        w1.setValue(pDct['fixedScaleMin']['value'])
#        w2.setFixedSize(10,30) # w,h
#        #w2.setTotalAngle(rots * 360.0)
#        #s.connect(w2,SIGNAL('valueChanged(double)'), pwdg.btmScaleWheelHandler)
#
#        wheelsLayout = QVBoxLayout()
#        wheelsLayout.addWidget(w1)
#        wheelsLayout.addWidget(btn1)
#        wheelsLayout.addWidget(btn2)
#        wheelsLayout.addWidget(w2)
#        pwdg.setAutoScale(True)
#
#        s.connect(w1,   SIGNAL('valueChanged(double)'), pwdg.fixedScaleHandler)
#        s.connect(btn1, SIGNAL('toggled(bool)'), pwdg.fixedScaleHandler)
#        s.connect(btn2, SIGNAL('toggled(bool)'), pwdg.fixedScaleHandler)
#        s.connect(w2,   SIGNAL('valueChanged(double)'), pwdg.fixedScaleHandler)
#
#        return wheelsLayout
#

#-----------------------------
#    def data_ready(s, data ):
#        if s.cfg.debug >= Kst.DBGLEVEL_RATE1:
#            print("ChartsFrame.data_ready")
#        s.chunkSize = s.cfg.framesPerChart
#        gendata = data[Kst.GENDATASTART:]
#        frameN  = gendata[Kst.FRAME_NUMBER]
#
#        # Trigger count, triggers plot every chunksize frames
#        # values are : 0,1,2...chunksize-1, 0,1,2...chunksize-1, 0,1,2...
#        trgCount = frameN % s.chunkSize
#        y1 = gendata[Kst.APD_CELLDATAAVG   ]
#        y2 = gendata[Kst.LWF_COUNTAVG      ]
#        y3 = gendata[Kst.CRV_WAVEFRONTERROR]
#        y4 = gendata[Kst.DM_FLATVAR        ]
#
#
#
#        # plot on every chunkSize frames
#        # else accumulate values and return
#        if s.plotAveragedValues:
#            if not trgCount:
#                #print(".....................................................")
#                # coerce index for triggered datum to chunksize
#                # eg, 0 becomes 10 for chunskize = 10
#                s.accumY1[s.chunkSize]=y1
#                s.accumY2[s.chunkSize]=y2
#                s.accumY3[s.chunkSize]=y3
#                s.accumY3[s.chunkSize]=y4
#
#                # average accumulated vals
#                avgY1 = s.accumY1[1:s.chunkSize+1].mean()
#                avgY2 = s.accumY2[1:s.chunkSize+1].mean()
#                avgY3 = s.accumY3[1:s.chunkSize+1].mean()
#                avgY4 = s.accumY4[1:s.chunkSize+1].mean()
#
#                # Plot
#                s.pwdg1.data_ready(avgY1)
#                s.pwdg2.data_ready(avgY2)
#                s.pwdg3.data_ready(avgY3)
#                s.pwdg4.data_ready(avgY4)
#
#            else:
#                # Accumulate values and return
#                # coerce chunksize index=0 to chunksize
#                # eg. if chunksize=10,  then if index=0, index=10
#                s.accumY1[trgCount]=y1
#                s.accumY2[trgCount]=y2
#                s.accumY3[trgCount]=y3
#                s.accumY4[trgCount]=y4
#                return
#
#        else:
#                #s.pwdg1.data_ready(y1)
#                #s.pwdg2.data_ready(y2)
#                #s.pwdg3.data_ready(y3)
#                #s.pwdg4.data_ready(y4)
#
#                #s.lcd1.display(float(y1))
#                #s.lcd2.display(float(y2))
#                #s.lcd3.display(float(y3))
#                #s.lcd4.display(float(y4))
#

# knobs & labels
#s.dial1  = QDial()
#s.dial1.setMinimumSize(20,20)
#s.dial2  = QDial()
#s.dial3  = QDial()
#s.dial4  = QDial()
#s.layout.addWidget(s.dial1,  0,  c, 1, 1)

#tUtil.prnTime(s.qdt0)
#s.baseDT  = qtTimes.QtTimes(zone=s.tZone)
#s.baseH   = s.baseDT.hour()
#print("s.baseDT:", s.baseDT)
#print("s.baseH:", s.baseH)

#............................................................
# Menus
#s.menubar = QMenuBar()
#s.menu    = QMenu('Menu')
#s.menu.addAction("act2")
#s.menubar.addMenu(s.menu)
#............................................................

#.......................................................................
#s.chunkSize = s.cfg.framesPerChart # plot every chunkSize frames
#s.plotAveragedValues = False

#s.accumSize = 60 * 60 * 12        # 12 hours
#s.accumY1 = np.zeros(s.accumSize)
#s.accumY2 = np.zeros(s.accumSize)
#s.accumY3 = np.zeros(s.accumSize)
#s.accumY4 = np.zeros(s.accumSize)
#
