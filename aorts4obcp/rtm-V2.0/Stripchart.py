#!/usr/bin/python
"""
Stripchart Widget
"""

#===============================================================================
# File: Stripchart.py
#
# Notes:
# http://docs.huihoo.com/qwt/class_qwt_plot-members.html
# http://docs.huihoo.com/qwt/class_qwt_pickerhtml
#===============================================================================
from __future__ import absolute_import, print_function, division
import sys
import numpy as np

import Configuration

from PyQt5.QtCore import (Qt, QObject, QObject, QDateTime, QEvent, QPoint)
from PyQt5.QtGui import (QPen, QFont, QColor)
from PyQt5.QtWidgets import (QFrame, QSizePolicy, QLabel)

import qwt
import hacked_qwtScaleDiv
import Constants as Kst
import stripchartDialog
import timeUtil as tUtil


#------------------------------------------------------------------------------
# Class Stripchart
#------------------------------------------------------------------------------
class Stripchart(qwt.QwtPlot):

    # args is a tuple of positional args
    # kwargs is a dictionary of keyword args
    def __init__(self, *args, **kwargs):
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        self.lg.debug("<Stripchart.__init__>", kwargs['name'])
        qwt.QwtPlot.__init__(self)

        # kwargs
        self.name = kwargs['name']  # chart name
        self.dt0 = kwargs['qtt']  # TimeZero: QDateTime instance from caller
        self.chartNumber = kwargs['chartNumber']  # chartnumber 1-N

        # stripchart configuration dictionary
        self.pDct = self.cfg.cfgD['stripchart']['chart' + str(self.chartNumber)]

        self.timeSpec = self.dt0.timeSpec()  # UTC/LOCAL
        #tUtil.prnTime(s.dt0)

        # set TZero to current time, zeroing minutes & seconds
        tUtil.setTimeI(self.dt0, self.dt0.time().hour(), 0, 0)
        #tUtil.prnTime(s.dt0)

        # Set total seconds from dt0
        # Will be updated by caller's timer
        self.tSeconds = self.dt0.secsTo(QDateTime().currentDateTime())
        #print("s.TSeconds", s.tSeconds)

        # Accumulator accumY accumulates data for s.maxhours * 3600
        self.maxHours = self.cfg.cfgD['gen']['stripchartHours']['value']
        #s.maxHours  = 1
        self.acmWd = self.maxHours * 3600  # N accum-1-second-elements
        self.acmMin = 0  # min accum index
        self.acmMax = self.acmWd  # max accum index
        self.accumY = np.zeros(self.acmMax,
                               dtype=float)  # create&zero accumulator
        self.acmMinVal = 1000.0  # init min accumulator value for compare
        self.acmMaxVal = -1000.0  # init max accumulator value for compare
        self.acmShift = 3600  # size of accum left-shift on overflow (seconds)
        self.acmShiftOffset = 0

        # Plot-vectors: xv & yv.
        # Set by s.setPlot
        self.yv = None  # plot data vector s.accumY[s.acmP1:s.acmP2]
        self.xv = np.arange(0, self.acmWd, 1)  # [t1, t1+1, t1+2 ... t2-1]
        self.xvMax = None  # X plot data vector max  index set by setPlot
        self.yvMax = None  # Y plot data vector max index set by setPlot
        self.yvWd = None  # width of y-vector

        # seconds of yv left-shift on yv overflow mode for
        # seconds,minutes,hours scales
        self.yvShiftSeconds = self.cfg.cfgD['gen']['secondsScaleShift']['value']
        self.yvShiftMinutes = self.cfg.cfgD['gen']['minutesScaleShift']['value']
        self.yvShiftHours = self.cfg.cfgD['gen']['hoursScaleShift']['value']
        self.acmP1 = None  # Y vector leftmost  accumulator point set by setPlot
        self.acmP2 = None  # Y vector rightmost accumulator point set by setPlot
        self.plotUnits = None  # set by setPlot

        #-----------------------------------------------------------------------
        self.cnv = self.canvas()
        self.cnv.setFrameStyle(QFrame.Box | QFrame.Sunken)
        self.cnv.setLineWidth(2)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # hz,vt
        pen = QPen(QColor(Kst.STRIPCHARTGRID))  # create pen & set color
        pen.setDashPattern([1, 10])  # set pen linestyle
        self.grid = qwt.QwtPlotGrid()  # create grid
        self.grid.setPen(pen)  # Set grid color     # set pen in grid
        self.grid.attach(self)  # attach grid to plot

        self.plotLayout().setSpacing(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
        #s.setCanvasBackground(Qt.black)          # set plot background
        self.setCanvasBackground(Qt.white)  # set plot background

        #s.plotLayout.addWidget(s.lblXcoord)
        self.plot1 = qwt.QwtPlotCurve()
        self.plot1.attach(self)
        self.plot1.setPen(QPen(Qt.green))
        self.yaxisId = self.plot1.yAxis()
        self.xaxisId = self.plot1.xAxis()

        #s.xAxisId             = s.xBottom
        #s.yAxisId             = s.yLeft
        #print("AXIS ID's",  qwt.QwtPlot.xBottom, s.xaxisId, qwt.QwtPlot.yLeft, s.yaxisId)

        # Font
        qf = QFont()
        qf.setPointSize(8)

        # Plot title
        titleText = qwt.QwtText(kwargs['name'])
        titleText.setFont(qf)
        self.setTitle(titleText)

        # workaround for y-axis legend clipping bug. Setting a Y-axis title
        # fixes the bug
        self.setAxisTitle(qwt.QwtPlot.yLeft, ' ')

        # popup dialog
        self.dlg = stripchartDialog.StripchartDialog(self.name + ' Stripchart',
                                                     self.pDct, self)

        #s.connect(s.dlg.okButton,  SIGNAL("ChartPopupOK"), s.foo)
        # Mouse wheel
        self.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        self.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        self.wheelIncr = 120  # probable delta from wheel event=ev.delta
        self.__initMouseTracking()  # track coords with mouse movement
        #s.__initZooming()     # set up click&drag rubberband zoom

        # Two Labels for mouse plot coordinates
        self.lblX = QLabel('123.456')
        self.lblY = QLabel('789.123')
        self.lblX.setMinimumHeight(18)
        self.lblY.setMinimumHeight(18)

        self.__initPicker()  # init mouse-click&drag picker

        self.plot1.setStyle(self.plot1.Steps)  # steps
        self.setPlot(Kst.HOURS, 0, 2 * 3600)  # create plot from T0 to nminutes
        self.scaleDirty = True  # redraw scale
        self.autoMinMax = True  # automatic minmax scaling
        self.autoMinMaxButton = None  # autoMinMax button widget. Caller must set

        #s.YScaleTop     = s.pDct['fixedScaleMax']['value']
        #s.YScaleBtm     = s.pDct['fixedScaleMin']['value']

        # Fixed values
        self.fixedScaleTop = self.pDct['fixedScaleMax']['value']
        self.fixedScaleBtm = self.pDct['fixedScaleMin']['value']

        #print("s.ID           :", s.pDct['Id'])
        #print("s.fixedScaleTop", s.fixedScaleTop)
        #print("s.fixedScaleBtm", s.fixedScaleBtm)

        # set Y-axis scale = zero True/False
        self.zeroScaleBase = self.pDct['zeroScaleBase']['value']
        #print("s.zeroScaleBase", s.zeroScaleBase)

    #...........................................................................
    # Set scale mode. Called by instantiator and by H M S radio buttons
    #...........................................................................
    def setHmsScale(self, mode):
        # Hours
        if mode == Kst.HOURS:
            nHours = 4  # display 4 hours on chart
            t1 = self.tSeconds - (3 * 3600)
            if t1 < 0:
                t1 = 0
            t2 = t1 + nHours * 3600
            self.setPlot(Kst.HOURS, t1, t2)

        # Minutes
        elif mode == Kst.MINUTES:
            nMinutes = 5  # display 5 minutes on chart
            t1 = self.tSeconds - (nMinutes * 60)
            if t1 < 0:
                t1 = 0
            t2 = t1 + (nMinutes * 60) + 60
            self.setPlot(Kst.MINUTES, t1, t2)

        # Seconds
        elif mode == Kst.SECONDS:
            nSeconds = 60  # display 60 seconds on chart
            t1 = self.tSeconds - nSeconds
            if t1 < 0:
                t1 = 0
            t2 = t1 + nSeconds + 10
            self.setPlot(Kst.SECONDS, t1, t2)

    #...........................................................................
    # t1,t2 are seconds since timeZero
    # They become pointers, acmP1,acmP2 to the accumulated data
    #...........................................................................
    def setPlot(self, unit, t1, t2):
        #print("<setPlot> ", t1,t2)
        self.plotUnits = unit
        self.acmP1 = t1
        self.acmP2 = t2
        self.yvWd = self.yvMax = self.xvMax = t2 - t1

        # create & zero Y-plot vector mapped to section of accumulator
        self.yv = self.accumY[self.acmP1:self.acmP2]

        self.draw = TimeScaleDraw(self.plotUnits, when=self.dt0.addSecs(t1),
                                  timespec=self.timeSpec)
        self.setAxisScaleDraw(self.xaxisId, self.draw)
        if unit == Kst.HOURS:
            self.setScaleDiv(0.0, self.xvMax)
            self.setAxisScale(self.xaxisId, 0.0, self.xvMax, 60 * 30)
        elif unit == Kst.MINUTES:
            self.setAxisScale(self.xaxisId, 0.0, self.xvMax, 60)
        elif unit == Kst.SECONDS:
            self.setSecScaleDiv(0.0, self.xvMax)
            self.setAxisScale(self.xaxisId, 0.0, self.xvMax, 10)

        self.updateAxes()
        self.plotv(self.xv, self.yv)

    #...........................................................................
    # Note that in pyqwt: QwtScaleDiv(double, double, QwtTickList*)
    # is implemented as: scaleDiv = QwtScaleDiv(
    #    lower, upper, majorTicks, mediumTicks, minorTicks)
    #...........................................................................
    def setScaleDiv(self, t1, t2):
        #print("<Stripchart.setScaleDIV>", t1,t2)
        # division ticks
        minTicks = []
        minTicks = list(np.arange(t1, t2, 60, dtype=int))
        medTicks = list(np.arange(t1, t2, 600, dtype=int))
        majTicks = list(np.arange(t1, t2, 3600, dtype=int))

        self.div = hacked_qwtScaleDiv.QwtScaleDiv(t1, t2, majTicks, medTicks,
                                                  minTicks)
        #s.div.setInterval(t1,t2)
        self.setAxisScaleDiv(self.xaxisId, self.div)

    #...........................................................................
    # Note that in pyqwt: QwtScaleDiv(double, double, QwtTickList*)
    # is implemented as: scaleDiv = QwtScaleDiv(
    #    lower, upper, majorTicks, mediumTicks, minorTicks)
    #...........................................................................
    def setSecScaleDiv(self, t1, t2):

        minTicks = []
        medTicks = list(np.arange(t1, t2, 5, dtype=int))
        majTicks = list(np.arange(t1, t2, 10, dtype=int))
        self.div = hacked_qwtScaleDiv.QwtScaleDiv(t1, t2, majTicks, medTicks,
                                                  minTicks)
        #s.div.setInterval(t1,t2)
        self.setAxisScaleDiv(self.xaxisId, self.div)

    #...........................................................................
    #
    #...........................................................................
    def plotv(self, xv, yv):
        min_len = min(len(xv), len(yv))
        self.plot1.setData(xv[:min_len], yv[:min_len])  # set plot vectors
        self.replot()  # schedule plot

    #...........................................................................
    ##
    #...........................................................................
    def timerEvent(self, e):
        print("Null timer event")
        #x = random.uniform(-s.xvLen,s.xvLen,10)
        ## shift array left by 10 & set 10 new values at end
        #s.fakeyv =  concatenate((s.fakeyv[10:], s.fakeyv[:10]), 1)
        #s.fakeyv[s.xvLen-10:s.xvLen] =  x
        #s.plot1.setData(s.fakexv, s.fakeyv)
        #s.replot()

    #...........................................................................
    # Mousewheel event handler  (not thumbwheel widget handler)
    # we.delta() : forward:128 backward:-128
    # delta # forward 1 backward -1
    #...........................................................................
    def wheelEvent(self, we):
        delta = we.delta() / self.wheelIncr
        self.wheelVal = delta
        self.wheelAccumVal += delta

        p1 = self.acmP1 + delta * 60
        p2 = self.acmP2 + delta * 60

        if p1 < self.acmMin or p2 > self.acmMax:
            return

        self.setPlot(self.plotUnits, p1, p2)

    #...........................................................................
    def showCoordinates(self, position):
        # print("showCoordinates", position)
        self.xCoord = self.invTransform(qwt.QwtPlot.xBottom, position.x())
        self.yCoord = self.invTransform(qwt.QwtPlot.yLeft, position.y())
        self.lblX.setText(self.draw.str(self.xCoord))
        self.lblY.setText('%7.3f' % self.yCoord)

    #
    # QwtPlotPicker (
    #  xAxis, yAxis,
    #  selectionFlags,
    #   RubberBand rubberBand,
    #   DisplayMode trackerMode,
    #  QwtPlotCanvas *)
    def __initPicker(self):

        self.picker = None
        return

        self.picker = qwt.QwtPlotPicker(qwt.QwtPlot.xBottom, qwt.QwtPlot.yLeft,
                                        qwt.QwtPicker.RectSelection,
                                        qwt.QwtPlotPicker.RectRubberBand,
                                        qwt.QwtPicker.AlwaysOn, self.canvas())

        self.picker.setRubberBandPen(QPen(Qt.black))

        self.picker.connect(self.picker,
                            SIGNAL('selected(const QwtDoubleRect&)'),
                            self.pickerHandler)

    #...........................................................................
    # Rectangle-picker handler called on left-mouse click & drag
    # p is QRectFF = 4 points at mouse click and drag
    #print('PickerHandler', qR)
    #print("Points",p1,p2,p3,p4)
    # p2:bottom, p4:top,
    #print("Top:",p4)
    #print("Btm:",p2)
    def pickerHandler(self, qR):
        #print("<pikcerHanlder>", qR)
        p1, p2, p3, p4 = qR.getCoords()
        #print("Ps", p1,p2,p3,p4)
        #s.fixedScaleTop = s.pDct['fixedScaleMax']['value'] = p4
        #s.fixedScaleBtm = s.pDct['fixedScaleMin']['value'] = p2
        #s.setAutoMinMax(False)
        #s.setYScale(s, btm, top )

        # catch a left click with no length or height
        if p1 == p3:
            return
        if p2 == p4:
            return

        self.dlg.setSpinners(p4, p2)

        # pretend we are the popup fixed range spinners
        self.setFixedScale('SP1', p4)  #set top scale same as spinner 1
        self.setFixedScale('SP2', p2)  #set top scale same as spinner 2

        #pX1 = int( qR.left()  + 0.5) # round leftmost  Xaxis point to integer
        #pX2 = int( qR.right() + 0.5) # round rightmost Xaxis point to integer
        #s.setPick(qR)
        #s.xCoord = s.invTransform(qwt.QwtPlot.xBottom, position.x())
        #s.yCoord = s.invTransform(qwt.QwtPlot.yLeft  , position.y())
        #s.xCoord = s.invTransform(qwt.QwtPlot.xBottom, qR.left())

    # display plot from x1 to x2
    def setPick(self, x1, x2):
        print("setPick", x1, x2)
        nSeconds = x2 - x1  # width of scale in plot-units=seconds

    # s.setXXScale( 0, nSeconds )

    #...........................................................................

    def __initMouseTracking(self):
        """Initialize mouse tracking
        """
        self.connect(Spy(self.canvas()), SIGNAL("MouseMove"),
                     self.showCoordinates)

        #s.cfg.statusBar().showMessage(
        #    'Mouse movements in the plot canvas are shown in the status bar')

    #...........................................................................
    # perform click-Action on mouse release
    # Event.button values are Left-button:1 Middle button: 4, right button:2
    #
    def mouseReleaseEvent(self, event):

        button = event.button()

        if button == Kst.LB:  # left button
            return
        elif button == Kst.MB:  # middle button
            return
        elif button == Kst.RB:  # right button
            # Uncomment for individual popups
            event.accept()
            self.dlg.popup(self.mapToGlobal(QPoint(0 + self.width() + 20, 0)))

    #def testPrint(s):
    #    s.painter.drawText(painter,QRect, QString("this is text"))

    #...........................................................................
    def __initZooming(self):
        """Initialize zooming
        """
        self.zoomer = qwt.QwtPlotZoomer(
                qwt.QwtPlot.xBottom,
                qwt.QwtPlot.yLeft,
                qwt.QwtPicker.DragSelection,
                qwt.QwtPickerAlwaysOff,
                #s.plot.canvas()
                self.canvas())

        #s.zoomer.setRubberBandPen(QPen(Qt.black))
        self.zoomer.setRubberBandPen(QPen(Qt.black))

    #...........................................................................
    def setZoomerMousePattern(self, index):
        """Set the mouse zoomer pattern.
        """
        if index == 0:
            pattern = [
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.LeftButton,
                                                     Qt.Qt.NoModifier),
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.MidButton,
                                                     Qt.Qt.NoModifier),
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.RightButton,
                                                     Qt.Qt.NoModifier),
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.LeftButton,
                                                     Qt.Qt.ShiftModifier),
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.MidButton,
                                                     Qt.Qt.ShiftModifier),
                    qwt.QwtEventPattern.MousePattern(Qt.Qt.RightButton,
                                                     Qt.Qt.ShiftModifier),
            ]
            self.zoomer.setMousePattern(pattern)
        elif index in (1, 2, 3):
            self.zoomer.initMousePattern(index)
        else:
            raise ValueError('index must be in (0, 1, 2, 3)')

    def shiftAccumulatorLeft(self, shiftN):
        print("******************************")
        print("s.accumY:", self.accumY)
        print("******************************")
        print("shiftAccumulatorLeft:", shiftN)
        print("s.acmShiftOffset", self.acmShiftOffset)
        self.acmShiftOffset += shiftN
        print("s.acmShiftOffset", self.acmShiftOffset)

        # [t1, t1+1, t1+2 ... t2-1]
        print("xv[0]", self.xv[0])
        print("xv[1]", self.xv[1])
        self.xv = np.arange(shiftN, self.acmWd + shiftN, 1)
        print("xv[0]", self.xv[0])
        print("xv[1]", self.xv[1])
        print("xv[-2]", self.xv[-2])
        print("xv[-1]", self.xv[-1])

        # shift all elements of array left by n
        # placing elements shifted off left on the right
        # eg: [1,2,3,4] shift 2 = [3,4,1,2]
        #np.concatenate((s.accumY[n:],s.accumY[:n]), n) # rotate left by n
        #s.accumY[s.accum.size-n:] = 0  # zero rightmost n-elements

        # rotate left by shifN
        np.concatenate((self.accumY[shiftN:], self.accumY[:shiftN]), shiftN)
        self.accumY[self.accum.size - shiftN:] = 0  # zero rightmost n-elements

        print("******************************")
        print("s.accumY:", self.accumY)
        print("******************************")

        #    #s.setPlotUnits(s.plotUnits) # rel
        #    #s.acmT0  += n  # adjust time of zero-eth datum

        #s.accumY[s.acNdx] = ydatum
        self.setPlot(self.plotUnits, self.acmP1 + self.acmShiftOffst,
                     self.acmP2)

    #...........................................................................
    # Plot data as handler for instantiators timer-tick.
    # seconds : seconds from application start.
    # (datum value is repeated if realtime data not being sent)
    #...........................................................................
    def plotDatum(self, seconds, ydatum):
        #print("<plotDatum>",ydatum)
        # OK: s.tSeconds = s.dt0.secsTo(QDateTime().currentDateTime())
        self.tSeconds += 1
        try:
            self.accumY[self.tSeconds - self.acmShiftOffset] = ydatum
        except IndexError as e:
            print("********** Index Error at %d ***********:%s" %
                  (self.tSeconds, e))
            print("Index       :", self.tSeconds)
            #print("Index-Offset:", s.tSeconds-s.acmShiftOffset)
            #shiftAccumlatorLeft(1800)
            #print("Index-Offset:", s.tSeconds-s.acmShiftOffset)
            #s.accumY[s.tSeconds-s.acmShiftOffset] = ydatum
            sys.exit()

        # If AutoMinMax keep min,max values (excludeing datum = 0.0)
        if self.autoMinMax:
            if ydatum != 0 and self.acmMinVal > ydatum:
                self.acmMinVal = ydatum
                self.scaleDirty = True  # force scale redraw

            # set max data value
            if self.acmMaxVal < ydatum:
                self.acmMaxVal = ydatum
                self.scaleDirty = True  # force scale redraw

        if self.scaleDirty:
            self.scaleDirty = False
            if self.autoMinMax:
                self.YScaleTop = self.acmMaxVal + self.acmMaxVal * 0.01
                self.YScaleBtm = self.acmMinVal - self.acmMinVal * 0.01
            else:
                self.YScaleTop = self.fixedScaleTop
                self.YScaleBtm = self.fixedScaleBtm

            self.setYScale(self.YScaleBtm, self.YScaleTop)

        # shift left on plot beyond right edge of stripchart
        if self.tSeconds > self.acmP2:
            if self.plotUnits == Kst.HOURS:
                p1 = self.acmP1 + self.yvShiftHours
                p2 = self.acmP2 + self.yvShiftHours

            elif self.plotUnits == Kst.MINUTES:
                p1 = self.acmP1 + self.yvShiftMinutes
                p2 = self.acmP2 + self.yvShiftMinutes

            else:  # s.plotUnits == Kst.SECONDS
                p1 = self.acmP1 + self.yvShiftSeconds
                p2 = self.acmP2 + self.yvShiftSeconds

            self.setPlot(self.plotUnits, p1, p2)

        # plot
        self.plotv(self.xv, self.yv)

    #...........................................................................
    # Set auto-scaling for y-axis by wrapping
    # QwtPlot's 'setAxisAutoScale' and doing housekeeping
    #
    def setAutoMinMax(self, state):
        #print("setAutoMinMAX:",state)
        self.autoMinMax = state
        self.setAutoMinMaxButton(state)

    #...........................................................................
    # Set instantiator's autoscale-button indicators on/off
    def setAutoMinMaxButton(self, state):
        #print("setAutoMinMaxButton:",state)
        self.autoMinMaxButton.setChecked(state)
        if state:
            self.autoMinMaxButton.setText('A')
        else:
            self.autoMinMaxButton.setText('F')

    #...........................................................................
    # setYScale: set Y-axis fixed-scale high/low values
    #    if step is zero qwtplot calculates stepsize automatically
    #   Calling qwtplot.setAxisScale disables built-in auto-scaling
    #...........................................................................
    def setYScale(self, btm, top, step=0):
        #print("<setYScale>", btm, top)

        #If flag set, force bottom scale = 0
        if self.zeroScaleBase:
            #print("ZeroScaleBase")
            self.YScaleBtm = 0

        # Else set bottom scale to value if btm not none
        elif btm is not None:
            self.YScaleBtm = btm

        # set top scale if not none
        if top is not None:
            self.YScaleTop = top

        # disable autoscaling and set fixed values
        self.setAxisScale(self.yaxisId, self.YScaleBtm, self.YScaleTop, step)
        self.updateAxes()

    #..........................................................................
    # fixedScaleHandler: handle action on popup fixed y-axis range spinners
    #..........................................................................
    def fixedScaleHandler(self, value):
        #print("<fixedScaleHandler> %s %f"% (s.name,value))
        sender = self.sender()
        Xid = self.sender().Xid
        #print("XID>",Xid)
        self.setFixedScale(Xid, value)

    #..........................................................................
    # fixedScaleHandler:
    #..........................................................................
    def setFixedScale(self, Xid, value):

        # handle chart popup upper spinwheel & mouse rubber-band
        # (s.dlg.topSpinner.setValue(value))
        if Xid == 'SP1':
            self.fixedScaleTop = self.pDct['fixedScaleMax']['value'] = value
            self.setAutoMinMax(False)
            self.setYScale(None, self.fixedScaleTop)

        # handle chart popup lower spinwheel & mouse rubber-band
        elif Xid == 'SP2':
            self.fixedScaleBtm = self.pDct['fixedScaleMin']['value'] = value
            self.setAutoMinMax(False)
            self.setYScale(self.fixedScaleBtm, None)

        # A/F button
        # handle Auto/Fixed range button toggle
        elif Xid == 'RB1':
            # value = true:false
            # Set instantiator's autoscale-button indicators on/off
            # value is button state
            self.scaleDirty = True  # force Y-axis scale redraw
            self.setAutoMinMax(value)  # turn auto-scaling on/off
            self.setYScale(self.fixedScaleBtm, self.fixedScaleTop)

        # Z-button
        # handle zeroScaleBase button
        elif Xid == 'RB2':
            self.zeroScaleBase = value  # True/False
            self.scaleDirty = True  # force Y-axis scale redraw
        else:
            self.lg.error("<fixedScaleHandler> %s unknown caller" % self.name)


#------------------------------------------------------------------------------
# Class TimeScaleDraw
#------------------------------------------------------------------------------
class TimeScaleDraw(qwt.QwtScaleDraw):

    def __init__(self, unit, when='now', timespec=Qt.LocalTime):

        qwt.QwtScaleDraw.__init__(self)
        self.unit = unit
        self.setLabelAlignment(Qt.AlignLeft | Qt.AlignBottom)
        #s.setLabelRotation(-25.0)
        self.dt0 = tUtil.setTime(when, timeSpec=timespec)

        #print("................ TimescaleDraw ............")
        #tUtil.prnTime(s.dt0)
        #tUtil.setTimeI(s.dt0, s.dt0.time().hour(),0,0) # zero minutes & seconds
        #tUtil.prnTime(s.dt0)
        #print("............................")

        # set tick lengths
        self.setTickLength(qwt.QwtScaleDiv.MinorTick, 4)
        self.setTickLength(qwt.QwtScaleDiv.MediumTick, 8)
        self.setTickLength(qwt.QwtScaleDiv.MajorTick, 12)

    # plot will call this to label ticks
    def label(self, secs):
        dt = self.dt0.addSecs(secs)

        if self.unit == Kst.SECONDS:
            #print("TimeScaleDraw:", dt.toString('hh:mm:ss'))
            return qwt.QwtText(dt.toString('hh:mm:ss'))
        else:
            return qwt.QwtText(dt.toString('hh:mm'))

    def str(self, secs):
        dt = self.dt0.addSecs(secs)
        #return(dt.toString('yyyy MM dd hh:mm:ss'))
        return (dt.toString('hh:mm:ss'))


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class Spy(QObject):

    def __init__(self, parent):
        QObject.__init__(self, parent)
        parent.setMouseTracking(True)
        parent.installEventFilter(self)

    def eventFilter(self, _, event):
        if event.type() == QEvent.MouseMove:
            self.emit(SIGNAL("MouseMove"), event.pos())
        return False


#-----------------------------------------------------------------------
# Stripchart test, probably
#-----------------------------------------------------------------------
if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    wdg = Stripchart(name='TipTilt', xtickrange=[-1, 1], ytickrange=[-1, 1],
                     axisTitle='Error')

    wdg = Stripchart(name='TipTilt', xtickrange=[-1, 1], ytickrange=[-1, 1],
                     axisTitle='Error')

    wdg.resize(300, 100)
    wdg.show()
    app.exec_()  # Gui loop
    sys.exit()
