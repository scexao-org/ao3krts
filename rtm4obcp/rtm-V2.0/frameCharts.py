#===============================================================================
# File : Plotframe.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

import constants as Kst
import configuration
from PyQt5.QtCore import (Qt, QDateTime, QDateTime)
from PyQt5.QtWidgets import (QFrame, QLabel, QGridLayout, QHBoxLayout,
                             QVBoxLayout, QSizePolicy, QButtonGroup,
                             QRadioButton, QLCDNumber, QPushButton)
import stripchart

import timeUtil as tUtil


#------------------------------------------------------------------------------
# SHFrame
#------------------------------------------------------------------------------
class ChartsFrame(QFrame):

    def __init__(self, name="noname", parent=None):
        self.cfg = configuration.cfg
        self.lg = self.cfg.lg
        self.lg.debug("<SHFrame.__init__>:%s" % name)
        #............................................................
        super(ChartsFrame, self).__init__(parent)

        self.name = name
        self.setMaximumSize(900, 600)
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)  # hrz,vrt
        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)

        self.layout = QGridLayout()
        self.displayPerNframes = 10
        self.MaxLedHeight = 30
        self.MaxLabelHeight = 12

        # get/set Timezone for stripchart labels
        self.timeSpec = tUtil.zoneToSpec(
                self.cfg.cfgD['gen']['stripchartTzone']['value'])
        # hack the time now
        if self.timeSpec == Qt.UTC:
            self.lg.info("o Charts timeZone is       : UTC")
            self.qdt0 = QDateTime().currentDateTimeUtc()
        else:
            self.lg.info("o Charts timeZone is       : LOCAL TIME")
            self.qdt0 = QDateTime().currentDateTime()

        #............................................................
        # Plots
        #............................................................

        # current y-value of the four stripcharts
        self.y1 = self.y2 = self.y3 = self.y4 = self.apdRmag = self.ShRmag = 0

        self.pwdg1 = stripchart.Stripchart(name='APD Count high-order WFS',
                                           qtt=self.qdt0, chartNumber=1)

        self.pwdg2 = stripchart.Stripchart(name='APD Count low-order WFS',
                                           qtt=self.qdt0, chartNumber=2)

        self.pwdg3 = stripchart.Stripchart(name='Wavefront Error',
                                           qtt=self.qdt0, chartNumber=3)

        self.pwdg4 = stripchart.Stripchart(name='Dm Variance', qtt=self.qdt0,
                                           chartNumber=4)

        # X/Y Mouse plot-coordinate labels
        self.lblX = QLabel('123.456')
        self.lblY = QLabel('789.123')
        self.lblX.setMinimumHeight(18)
        self.lblY.setMinimumHeight(18)
        self.lblXYLayout = QHBoxLayout()
        self.lblXYLayout.addWidget(self.lblX)
        self.lblXYLayout.addWidget(self.lblY)

        # 6 lcds display current plot value & two rmag-values
        self.lcd1 = self.lcd()
        self.lcd1b = self.lcd()  # kludged-on APD Rmag: 'apdRmag'

        self.lcd2 = self.lcd()
        self.lcd2b = self.lcd()  # kludged-on Shack-Hartmann Rmag: 'shRmag'

        self.lcd3 = self.lcd()
        self.lcd4 = self.lcd()

        self.lcd1.setToolTip("Current APD Count HOWFS Plot Value ")
        self.lcd1b.setToolTip("Current HOWFS Rmag ")

        self.lcd2.setToolTip("Current APD Count LOWFS Plot Value")
        self.lcd2b.setToolTip("Current LOWFS Rmag")

        self.lcd3.setToolTip("Current Wavefront Error Plot Value ")
        self.lcd4.setToolTip("Current DM Variance Plot Value ")

        # labels for the leds
        self.lbl1 = self.makeLabel('Howfs Count')
        self.lbl1b = self.makeLabel('Howfs Rmag')
        self.lbl2 = self.makeLabel('Lowfs Count')
        self.lbl2b = self.makeLabel('Lowfs Rmag')
        self.lbl3 = self.makeLabel('Wavefront Error')
        self.lbl4 = self.makeLabel('Dm Variance')

        hrzPolicy = QSizePolicy.Expanding
        vrtPolicy = QSizePolicy.Expanding
        self.pwdg1.setSizePolicy(hrzPolicy, vrtPolicy)
        self.pwdg2.setSizePolicy(hrzPolicy, vrtPolicy)
        self.pwdg3.setSizePolicy(hrzPolicy, vrtPolicy)
        self.pwdg4.setSizePolicy(hrzPolicy, vrtPolicy)

        #............................................................
        # Create 3 HMS buttons for chart scale
        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(True)

        self.rBtn1 = QRadioButton("h")
        self.rBtn2 = QRadioButton("m")
        self.rBtn3 = QRadioButton("s")

        self.btnGroup.addButton(self.rBtn1)
        self.btnGroup.addButton(self.rBtn2)
        self.btnGroup.addButton(self.rBtn3)
        self.btnGroup.buttonClicked.connect(self.btnHandler_plotTime)

        self.btnLayout = QHBoxLayout()
        self.btnLayout.addWidget(self.rBtn1)
        self.btnLayout.addWidget(self.rBtn2)
        self.btnLayout.addWidget(self.rBtn3)

        self.rBtn1.setToolTip("Set HOURS scale")
        self.rBtn2.setToolTip("Set MINUTES scale")
        self.rBtn3.setToolTip("Set SECONDS scale")

        #                             row,column, rowSpan, columnSpan,
        lblRspan = 2
        lcdRspan = 6

        plotRspan = 20
        plotCspan = 100
        self.layout.addLayout(self.btnLayout, 1, 0)

        # Fixed Y-scale range-setting:  2 thumbwheels & button for each plot
        self.rangeBtns1Layout = self.make_rangeBtns(
                self.pwdg1, self.cfg.cfgD['stripchart']['chart1'])
        self.rangeBtns2Layout = self.make_rangeBtns(
                self.pwdg2, self.cfg.cfgD['stripchart']['chart2'])
        self.rangeBtns3Layout = self.make_rangeBtns(
                self.pwdg3, self.cfg.cfgD['stripchart']['chart3'])
        self.rangeBtns4Layout = self.make_rangeBtns(
                self.pwdg4, self.cfg.cfgD['stripchart']['chart4'])

        #--- plot 1
        pr = 0 * plotRspan  # row of first column-plot
        r = pr + 2  # row of first column-1 widget
        self.layout.addWidget(self.lbl1, r, 0, lblRspan, 1)

        r += lblRspan
        self.layout.addWidget(self.lcd1, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lcd1b, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lbl1b, r, 0, lblRspan, 1)

        self.layout.addLayout(self.rangeBtns1Layout, pr + 4, 9, 10,
                              1)  #range buttons

        r += lblRspan
        self.layout.addWidget(self.pwdg1, pr, 10, plotRspan, plotCspan)

        #--- plot 2
        pr = 1 * plotRspan  # row of next column-2 plot
        r = pr + 2  # row of next column-1 widget
        self.layout.addWidget(self.lbl2, r, 0, lblRspan, 1)

        r += lblRspan
        self.layout.addWidget(self.lcd2, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lcd2b, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lbl2b, r, 0, lblRspan, 1)

        self.layout.addLayout(self.rangeBtns2Layout, pr + 4, 9, 10,
                              1)  #range buttons

        self.layout.addWidget(self.pwdg2, pr, 10, plotRspan, plotCspan)

        #--- plot 3
        pr = 2 * plotRspan  # row of next column2 plot

        r = pr + 6
        self.layout.addWidget(self.lcd3, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lbl3, r, 0, lblRspan, 1)

        self.layout.addLayout(self.rangeBtns3Layout, pr + 4, 9, 10,
                              1)  #range thumbwheels
        self.layout.addWidget(self.pwdg3, pr, 10, plotRspan, plotCspan)

        #--- plot 4
        pr = 3 * plotRspan  # row of next column2 plot

        r = pr + 6
        self.layout.addWidget(self.lcd4, r, 0, lcdRspan, 1)

        r += lcdRspan
        self.layout.addWidget(self.lbl4, r, 0, lblRspan, 1)
        self.layout.addLayout(self.rangeBtns4Layout, pr + 4, 9, 10,
                              1)  #range thumbwheels
        self.layout.addWidget(self.pwdg4, pr, 10, plotRspan, plotCspan)

        # buttons
        #r = pr + 3*plotRspan  # row of next column2 plot
        r = 4 * plotRspan

        # add X & Y mouse coordinates lables
        self.layout.addLayout(self.lblXYLayout, r, 0)

        #s.lbl5   = s.makeLabel("12.34")
        #s.lbl5.setMinimumHeight(18)

        # this fits nicely into ulc of stripchart margin
        #s.layout.addWidget(s.pwdg1.lblX,  0,  14, 1, 1)
        #s.layout.addWidget(s.pwdg1.lblY,  0,  15, 1, 1)

        self.seconds = 0
        self.setLayout(self.layout)

        # Set MINUTES plot scales
        self.pwdg1.setHmsScale(Kst.MINUTES)
        self.pwdg2.setHmsScale(Kst.MINUTES)
        self.pwdg3.setHmsScale(Kst.MINUTES)
        self.pwdg4.setHmsScale(Kst.MINUTES)
        self.rBtn2.setChecked(True)  # check the minutes button

        self.pwdg1.lblX = self.lblX
        self.pwdg1.lblY = self.lblY
        self.pwdg2.lblX = self.lblX
        self.pwdg2.lblY = self.lblY
        self.pwdg3.lblX = self.lblX
        self.pwdg3.lblY = self.lblY
        self.pwdg4.lblX = self.lblX
        self.pwdg4.lblY = self.lblY

        # set timer.  timer-tick drives stripcharts
        self.timerTick = 1  # call timerEvent at one Hertz
        self.y1 = 0
        #**************
        #s.timerTick  = 0.001             #
        #**************

        self.startTimer(self.timerTick * 1000)  # seconds to msecs

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
    def lcd(self):
        lcd = QLCDNumber(5)  # 4 digits or 3 digits 1 decimal-point
        #lcd.setSegmentStyle(QLCDNumber.Flat)
        lcd.setSegmentStyle(QLCDNumber.Filled)
        lcd.setMaximumHeight(self.MaxLedHeight)  # max width,height
        lcd.setStyleSheet("color: rgb(0, 255, 0);\n"
                          "background-color: rgb(0, 0,0);")
        return lcd

    #...........................................................................
    def btnHandler_plotTime(self, x):
        if self.cfg.debug: print("btnHandler_plotTime", x)

        id = self.btnGroup.checkedId()  # which radio button?
        #print("Id:", id)
        # Hours button
        if id == -2:
            self.pwdg1.setHmsScale(Kst.HOURS)
            self.pwdg2.setHmsScale(Kst.HOURS)
            self.pwdg3.setHmsScale(Kst.HOURS)
            self.pwdg4.setHmsScale(Kst.HOURS)

        # Minutes button
        if id == -3:
            self.pwdg1.setHmsScale(Kst.MINUTES)
            self.pwdg2.setHmsScale(Kst.MINUTES)
            self.pwdg3.setHmsScale(Kst.MINUTES)
            self.pwdg4.setHmsScale(Kst.MINUTES)

        # Seconds button
        if id == -4:  # Minutes
            self.pwdg1.setHmsScale(Kst.SECONDS)
            self.pwdg2.setHmsScale(Kst.SECONDS)
            self.pwdg3.setHmsScale(Kst.SECONDS)
            self.pwdg4.setHmsScale(Kst.SECONDS)

    #...........................................................................
    def makeLabel(self, text):
        lbl = QLabel(text)
        fg = " QLabel {color:black}"
        bg = " QLabel {background-color:%s}" % Kst.MWINBKGCOLOR
        border = " QLabel {border-color:%s}" % Kst.MWINBKGCOLOR
        lbl.setStyleSheet(fg + bg + border)
        lbl.setMaximumHeight(self.MaxLabelHeight)
        return (lbl)

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def data_ready(self, data):
        gendata = data[Kst.GENDATASTART:]

        self.y1 = gendata[Kst.APD_CELLDATAAVG]
        self.y2 = gendata[Kst.LWF_COUNTAVG]
        self.y3 = gendata[Kst.CRV_WAVEFRONTERROR]
        self.y4 = gendata[Kst.DM_FLATVAR]

        self.apdRmag = gendata[Kst.APD_RMAGAVG]  # Howfs Rmag
        self.ShRmag = gendata[Kst.LWF_RMAGAVG]  # Lowfs Rmag

    #-----------------------------------------------------------------------
    # timerEvent:  accumulate & display current data at each tick
    #-----------------------------------------------------------------------
    def timerEvent(self, e):

        self.seconds += 1  # seconds from startup

        #*print("Seconds:", s.seconds)
        #*s.y1 += 0.01

        ### shift yv left by 1
        self.pwdg1.plotDatum(self.seconds, self.y1)  # plot apd count howfs
        self.pwdg2.plotDatum(self.seconds, self.y2)  # plot apd count lowfs
        self.pwdg3.plotDatum(self.seconds, self.y3)  # plot wavefront error
        self.pwdg4.plotDatum(self.seconds, self.y4)  # plot Dm Variance

        self.lcd1.display(float(self.y1))  # LCD = apd-howfs count
        self.lcd1b.display(float(self.apdRmag))  # LCD = howfs Rmag (apd Rmag)
        self.lcd2.display(float(self.y2))  # LCD = apd count lowfs
        self.lcd2b.display(float(self.ShRmag))  # LCD = lowfs Rmag (Sh Rmag)
        self.lcd3.display(float(self.y3))  # LCD = wavefront error
        self.lcd4.display(float(self.y4))  # LCD = Dm Variance

    def setPlotRange(self, mode):
        self.pwdg1.setRange(mode)
        self.pwdg2.setRange(mode)
        self.pwdg3.setRange(mode)
        self.pwdg4.setRange(mode)

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    def clearPlotHistory(self):
        self.seconds = 0
        self.pwdg1.resetPlot()
        self.pwdg2.resetPlot()
        self.pwdg3.resetPlot()
        self.pwdg4.resetPlot()

    def topWheelHandler(self, value, x):
        print("<topWheelHandler> Value:", value, x)

    def btmWheelHandler(self, value):
        print("<btmWheelHandler> Value:", value)

    # make range Thumb-wheels and connect to plot widgets
    # w1.setStep(step)
    # w1.setTotalAngle(rots * 360.0)
    def make_rangeBtns(self, pwdg, pDct):
        btn1 = QPushButton('A')
        btn1.Xid = 'RB1'  # our tag: range-button-0
        pwdg.autoMinMaxButton = btn1
        btn1.setFixedSize(13, 20)
        btn1.setCheckable(True)
        btn1.setChecked(True)
        btn1.setFlat(True)
        btn1.setStyleSheet("background-color: rgb(0, 255, 0);")
        btn1.setToolTip("Toggle Auto/Fixed Y-axis scale")

        btn2 = QPushButton('Z')
        btn2.Xid = 'RB2'  # our tag: range-button-0
        btn2.setFixedSize(13, 20)
        btn2.setCheckable(True)
        btn2.setChecked(pDct['zeroScaleBase']['value'])
        btn2.setFlat(True)
        btn2.setStyleSheet("background-color: rgb(0, 255, 0);")
        btn2.setToolTip("Set zero-based Y-Axis scale")
        layout = QVBoxLayout()

        layout.addWidget(btn1)
        layout.addWidget(btn2)

        btn1.toggled.connect(pwdg.fixedScaleHandler)
        btn2.toggled.connect(pwdg.fixedScaleHandler)
        return layout
