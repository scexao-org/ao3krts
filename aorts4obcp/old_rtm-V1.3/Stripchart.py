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
import sys, time
import numpy as np
import random
import Configuration
import PyQt4.Qt as Qt
from PyQt4 import QtCore
from PyQt4.QtGui import (QWidget, QFrame, QBrush, QPen, QFont, QPalette, QColor,
                         QSizePolicy, QLabel)
from PyQt4.QtCore import (Qt,QTimer,QObject, SIGNAL,QObject,QSize,QString,\
                          QDateTime,QTime,QEvent,QString,QPoint)

from PyQt4 import Qwt5 as Qwt
import Constants as Kst
import stripchartDialog
import timeUtil as tUtil


#------------------------------------------------------------------------------
# Class Stripchart
#------------------------------------------------------------------------------
class Stripchart(Qwt.QwtPlot):

    # args is a tuple of positional args
    # kwargs is a dictionary of keyword args
    def __init__(s, *args, **kwargs):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.lg.debug("<Stripchart.__init__>", kwargs['name'])
        Qwt.QwtPlot.__init__(s)

        # kwargs
        s.name = kwargs['name']  # chart name
        s.dt0 = kwargs['qtt']  # TimeZero: QDateTime instance from caller
        s.chartNumber = kwargs['chartNumber']  # chartnumber 1-N

        # stripchart configuration dictionary
        s.pDct = s.cfg.cfgD['stripchart']['chart' + str(s.chartNumber)]

        s.timeSpec = s.dt0.timeSpec()  # UTC/LOCAL
        #tUtil.prnTime(s.dt0)

        # set TZero to current time, zeroing minutes & seconds
        tUtil.setTimeI(s.dt0, s.dt0.time().hour(), 0, 0)
        #tUtil.prnTime(s.dt0)

        # Set total seconds from dt0
        # Will be updated by caller's timer
        s.tSeconds = s.dt0.secsTo(QDateTime().currentDateTime())
        #print("s.TSeconds", s.tSeconds)

        # Accumulator accumY accumulates data for s.maxhours * 3600
        s.maxHours = s.cfg.cfgD['gen']['stripchartHours']['value']
        #s.maxHours  = 1
        s.acmWd = s.maxHours * 3600  # N accum-1-second-elements
        s.acmMin = 0  # min accum index
        s.acmMax = s.acmWd  # max accum index
        s.accumY = np.zeros(s.acmMax, dtype=float)  # create&zero accumulator
        s.acmMinVal = 1000.0  # init min accumulator value for compare
        s.acmMaxVal = -1000.0  # init max accumulator value for compare
        s.acmShift = 3600  # size of accum left-shift on overflow (seconds)
        s.acmShiftOffset = 0

        # Plot-vectors: xv & yv.
        # Set by s.setPlot
        s.yv = None  # plot data vector s.accumY[s.acmP1:s.acmP2]
        s.xv = np.arange(0, s.acmWd, 1)  # [t1, t1+1, t1+2 ... t2-1]
        s.xvMax = None  # X plot data vector max  index set by setPlot
        s.yvMax = None  # Y plot data vector max index set by setPlot
        s.yvWd = None  # width of y-vector

        # seconds of yv left-shift on yv overflow mode for
        # seconds,minutes,hours scales
        s.yvShiftSeconds = s.cfg.cfgD['gen']['secondsScaleShift']['value']
        s.yvShiftMinutes = s.cfg.cfgD['gen']['minutesScaleShift']['value']
        s.yvShiftHours = s.cfg.cfgD['gen']['hoursScaleShift']['value']
        s.acmP1 = None  # Y vector leftmost  accumulator point set by setPlot
        s.acmP2 = None  # Y vector rightmost accumulator point set by setPlot
        s.plotUnits = None  # set by setPlot

        #-----------------------------------------------------------------------
        s.cnv = s.canvas()
        s.cnv.setFrameStyle(QFrame.Box | QFrame.Sunken)
        s.cnv.setLineWidth(2)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # hz,vt
        pen = QPen(QColor(Kst.STRIPCHARTGRID))  # create pen & set color
        pen.setDashPattern([1, 10])  # set pen linestyle
        s.grid = Qwt.QwtPlotGrid()  # create grid
        s.grid.setPen(pen)  # Set grid color     # set pen in grid
        s.grid.attach(s)  # attach grid to plot

        s.plotLayout().setMargin(0)
        s.plotLayout().setCanvasMargin(0)
        s.plotLayout().setAlignCanvasToScales(1)
        #s.setCanvasBackground(Qt.black)          # set plot background
        s.setCanvasBackground(Qt.white)  # set plot background

        #s.plotLayout.addWidget(s.lblXcoord)
        s.plot1 = Qwt.QwtPlotCurve()
        s.plot1.attach(s)
        s.plot1.setPen(QPen(Qt.green))
        s.yaxisId = s.plot1.yAxis()
        s.xaxisId = s.plot1.xAxis()

        #s.xAxisId             = s.xBottom
        #s.yAxisId             = s.yLeft
        #print("AXIS ID's",  Qwt.QwtPlot.xBottom, s.xaxisId, Qwt.QwtPlot.yLeft, s.yaxisId)

        # Font
        qf = QFont()
        qf.setPointSize(8)

        # Plot title
        titleText = Qwt.QwtText(QString(kwargs['name']))
        titleText.setFont(qf)
        s.setTitle(titleText)

        # workaround for y-axis legend clipping bug. Setting a Y-axis title
        # fixes the bug
        s.setAxisTitle(Qwt.QwtPlot.yLeft, ' ')

        # popup dialog
        s.dlg = stripchartDialog.stripchartDialog(s.name + ' Stripchart',
                                                  s.pDct, s)

        #s.connect(s.dlg.okButton,  SIGNAL("ChartPopupOK"), s.foo)
        # Mouse wheel
        s.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        s.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        s.wheelIncr = 120  # probable delta from wheel event=ev.delta
        s.__initMouseTracking()  # track coords with mouse movement
        #s.__initZooming()     # set up click&drag rubberband zoom

        # Two Labels for mouse plot coordinates
        s.lblX = QLabel(QString('123.456'))
        s.lblY = QLabel(QString('789.123'))
        s.lblX.setMinimumHeight(18)
        s.lblY.setMinimumHeight(18)

        s.__initPicker()  # init mouse-click&drag picker
        s.plot1.setStyle(s.plot1.Steps)  # steps
        s.setPlot(Kst.HOURS, 0, 2 * 3600)  # create plot from T0 to nminutes
        s.scaleDirty = True  # redraw scale
        s.autoMinMax = True  # automatic minmax scaling
        s.autoMinMaxButton = None  # autoMinMax button widget. Caller must set

        #s.YScaleTop     = s.pDct['fixedScaleMax']['value']
        #s.YScaleBtm     = s.pDct['fixedScaleMin']['value']

        # Fixed values
        s.fixedScaleTop = s.pDct['fixedScaleMax']['value']
        s.fixedScaleBtm = s.pDct['fixedScaleMin']['value']

        #print("s.ID           :", s.pDct['Id'])
        #print("s.fixedScaleTop", s.fixedScaleTop)
        #print("s.fixedScaleBtm", s.fixedScaleBtm)

        # set Y-axis scale = zero True/False
        s.zeroScaleBase = s.pDct['zeroScaleBase']['value']
        #print("s.zeroScaleBase", s.zeroScaleBase)

    #...........................................................................
    # Set scale mode. Called by instantiator and by H M S radio buttons
    #...........................................................................
    def setHmsScale(s, mode):
        # Hours
        if mode == Kst.HOURS:
            nHours = 4  # display 4 hours on chart
            t1 = s.tSeconds - (3 * 3600)
            if t1 < 0:
                t1 = 0
            t2 = t1 + nHours * 3600
            s.setPlot(Kst.HOURS, t1, t2)

        # Minutes
        elif mode == Kst.MINUTES:
            nMinutes = 5  # display 5 minutes on chart
            t1 = s.tSeconds - (nMinutes * 60)
            if t1 < 0:
                t1 = 0
            t2 = t1 + (nMinutes * 60) + 60
            s.setPlot(Kst.MINUTES, t1, t2)

        # Seconds
        elif mode == Kst.SECONDS:
            nSeconds = 60  # display 60 seconds on chart
            t1 = s.tSeconds - nSeconds
            if t1 < 0:
                t1 = 0
            t2 = t1 + nSeconds + 10
            s.setPlot(Kst.SECONDS, t1, t2)

    #...........................................................................
    # t1,t2 are seconds since timeZero
    # They become pointers, acmP1,acmP2 to the accumulated data
    #...........................................................................
    def setPlot(s, unit, t1, t2):
        #print("<setPlot> ", t1,t2)
        s.plotUnits = unit
        s.acmP1 = t1
        s.acmP2 = t2
        s.yvWd = s.yvMax = s.xvMax = t2 - t1

        # create & zero Y-plot vector mapped to section of accumulator
        s.yv = s.accumY[s.acmP1:s.acmP2]

        s.draw = TimeScaleDraw(s.plotUnits, when=s.dt0.addSecs(t1),
                               timespec=s.timeSpec)
        s.setAxisScaleDraw(s.xaxisId, s.draw)
        if unit == Kst.HOURS:
            s.setScaleDiv(0.0, s.xvMax)
            s.setAxisScale(s.xaxisId, 0.0, s.xvMax, 60 * 30)
        elif unit == Kst.MINUTES:
            s.setAxisScale(s.xaxisId, 0.0, s.xvMax, 60)
        elif unit == Kst.SECONDS:
            s.setSecScaleDiv(0.0, s.xvMax)
            s.setAxisScale(s.xaxisId, 0.0, s.xvMax, 10)

        s.updateAxes()
        s.plotv(s.xv, s.yv)

    #...........................................................................
    # Note that in pyqwt: QwtScaleDiv(double, double, QwtTickList*)
    # is implemented as: scaleDiv = QwtScaleDiv(
    #    lower, upper, majorTicks, mediumTicks, minorTicks)
    #...........................................................................
    def setScaleDiv(s, t1, t2):
        #print("<Stripchart.setScaleDIV>", t1,t2)
        # division ticks
        minTicks = []
        minTicks = map(None, np.arange(t1, t2, 60, dtype=int))
        medTicks = map(None, np.arange(t1, t2, 600, dtype=int))
        majTicks = map(None, np.arange(t1, t2, 3600, dtype=int))
        s.div = Qwt.QwtScaleDiv(t1, t2, majTicks, medTicks, minTicks)
        #s.div.setInterval(t1,t2)
        s.setAxisScaleDiv(s.xaxisId, s.div)

    #...........................................................................
    # Note that in pyqwt: QwtScaleDiv(double, double, QwtTickList*)
    # is implemented as: scaleDiv = QwtScaleDiv(
    #    lower, upper, majorTicks, mediumTicks, minorTicks)
    #...........................................................................
    def setSecScaleDiv(s, t1, t2):
        #print("<Stripchart.setSecScaleDiv>", t1,t2)
        # division ticks
        #minTicks = map(None, np.arange(t1, t2,   5, dtype=int))
        minTicks = []
        medTicks = map(None, np.arange(t1, t2, 5, dtype=int))
        majTicks = map(None, np.arange(t1, t2, 10, dtype=int))
        s.div = Qwt.QwtScaleDiv(t1, t2, majTicks, medTicks, minTicks)
        #s.div.setInterval(t1,t2)
        s.setAxisScaleDiv(s.xaxisId, s.div)

    #...........................................................................
    #
    #...........................................................................
    def plotv(s, xv, yv):
        s.plot1.setData(xv, yv)  # set plot vectors
        s.replot()  # schedule plot

    #...........................................................................
    ##
    #...........................................................................
    def timerEvent(s, e):
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
    def wheelEvent(s, we):
        delta = we.delta() / s.wheelIncr
        s.wheelVal = delta
        s.wheelAccumVal += delta

        p1 = s.acmP1 + delta * 60
        p2 = s.acmP2 + delta * 60

        if p1 < s.acmMin or p2 > s.acmMax:
            return

        s.setPlot(s.plotUnits, p1, p2)

    #...........................................................................
    def showCoordinates(s, position):
        # print("showCoordinates", position)
        s.xCoord = s.invTransform(Qwt.QwtPlot.xBottom, position.x())
        s.yCoord = s.invTransform(Qwt.QwtPlot.yLeft, position.y())
        s.lblX.setText(s.draw.str(s.xCoord))
        s.lblY.setText('%7.3f' % s.yCoord)

        #print("Position:", position.x(), position.y())
        #s.cfg.statusBar().showMessage(
        #    'x = %+.6g, y = %.6g'
        #    % (s.invTransform(Qwt.QwtPlot.xBottom, position.x()),
        #       s.invTransform(Qwt.QwtPlot.yLeft, position.y())))

        #print(    'x = %+.6g, y = %.6g'
        #    % (s.invTransform(Qwt.QwtPlot.xBottom, position.x()),
        #       s.invTransform(Qwt.QwtPlot.yLeft, position.y())))

        #print(s.trackerText(QPoint(position.x(), position.y())))

        #print("X:", s.xCoord, "Y", s.yCoord)
        #print('Time', s.draw.str(s.xCoord) )

    #
    # QwtPlotPicker (
    #  xAxis, yAxis,
    #  selectionFlags,
    #   RubberBand rubberBand,
    #   DisplayMode trackerMode,
    #  QwtPlotCanvas *)
    def __initPicker(s):

        #s.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yLeft,
        #                       Qwt.QwtPicker.PointSelection,
        #                       Qwt.QwtPlotPicker.CrossRubberBand,
        #                       Qwt.QwtPicker.AlwaysOn,
        #                       s.canvas())
        #s.picker.connect(
        #   s.picker, SIGNAL('selected(const QwtDoublePoint&)'), s.pickerHandler)

        s.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yLeft,
                                     Qwt.QwtPicker.RectSelection,
                                     Qwt.QwtPlotPicker.RectRubberBand,
                                     Qwt.QwtPicker.AlwaysOn, s.canvas())

        s.picker.setRubberBandPen(QPen(Qt.black))

        s.picker.connect(s.picker, SIGNAL('selected(const QwtDoubleRect&)'),
                         s.pickerHandler)

    #...........................................................................
    # Rectangle-picker handler called on left-mouse click & drag
    # p is QRectFF = 4 points at mouse click and drag
    #print('PickerHandler', qR)
    #print("Points",p1,p2,p3,p4)
    # p2:bottom, p4:top,
    #print("Top:",p4)
    #print("Btm:",p2)
    def pickerHandler(s, qR):
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

        s.dlg.setSpinners(p4, p2)

        # pretend we are the popup fixed range spinners
        s.setFixedScale('SP1', p4)  #set top scale same as spinner 1
        s.setFixedScale('SP2', p2)  #set top scale same as spinner 2

        #pX1 = int( qR.left()  + 0.5) # round leftmost  Xaxis point to integer
        #pX2 = int( qR.right() + 0.5) # round rightmost Xaxis point to integer
        #s.setPick(qR)
        #s.xCoord = s.invTransform(Qwt.QwtPlot.xBottom, position.x())
        #s.yCoord = s.invTransform(Qwt.QwtPlot.yLeft  , position.y())
        #s.xCoord = s.invTransform(Qwt.QwtPlot.xBottom, qR.left())

    # display plot from x1 to x2
    def setPick(s, x1, x2):
        print("setPick", x1, x2)
        nSeconds = x2 - x1  # width of scale in plot-units=seconds

    # s.setXXScale( 0, nSeconds )

    #...........................................................................

    def __initMouseTracking(s):
        """Initialize mouse tracking
        """
        s.connect(Spy(s.canvas()), SIGNAL("MouseMove"), s.showCoordinates)

        #s.cfg.statusBar().showMessage(
        #    'Mouse movements in the plot canvas are shown in the status bar')

    #...........................................................................
    # perform click-Action on mouse release
    # Event.button values are Left-button:1 Middle button: 4, right button:2
    #
    def mouseReleaseEvent(s, event):

        button = event.button()

        if button == Kst.LB:  # left button
            return
        elif button == Kst.MB:  # middle button
            return
        elif button == Kst.RB:  # right button
            # Uncomment for individual popups
            event.accept()
            s.dlg.popup(s.mapToGlobal(QPoint(0 + s.width() + 20, 0)))

    #def testPrint(s):
    #    s.painter.drawText(painter,QRect, QString("this is text"))

    #...........................................................................
    def __initZooming(s):
        """Initialize zooming
        """
        s.zoomer = Qwt.QwtPlotZoomer(
                Qwt.QwtPlot.xBottom,
                Qwt.QwtPlot.yLeft,
                Qwt.QwtPicker.DragSelection,
                Qwt.QwtPickerAlwaysOff,
                #s.plot.canvas()
                s.canvas())

        #s.zoomer.setRubberBandPen(QPen(Qt.black))
        s.zoomer.setRubberBandPen(QPen(Qt.black))

    #...........................................................................
    def setZoomerMousePattern(self, index):
        """Set the mouse zoomer pattern.
        """
        if index == 0:
            pattern = [
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.LeftButton,
                                                     Qt.Qt.NoModifier),
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.MidButton,
                                                     Qt.Qt.NoModifier),
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.RightButton,
                                                     Qt.Qt.NoModifier),
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.LeftButton,
                                                     Qt.Qt.ShiftModifier),
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.MidButton,
                                                     Qt.Qt.ShiftModifier),
                    Qwt.QwtEventPattern.MousePattern(Qt.Qt.RightButton,
                                                     Qt.Qt.ShiftModifier),
            ]
            self.zoomer.setMousePattern(pattern)
        elif index in (1, 2, 3):
            self.zoomer.initMousePattern(index)
        else:
            raise ValueError, 'index must be in (0, 1, 2, 3)'

    #def shiftAccumulatorLeft(s, n):
    #    #print("shiftAccumulatorLeft:",n)
    #
    #    s.qttT0.adjust(n)  # increase accumulatort zeroeth element time
    #    #s.qttT0.prnTimes()
    #    s.setSCaleDraw()   # correct tick label times. (uses qttT0)
    #
    #    # shift all elements of array left by n
    #    # placing elements shifted off left on the right
    #    # eg: [1,2,3,4] shift 2 = [3,4,1,2]
    #    np.concatenate((s.accumY[n:],s.accumY[:n]), n)
    #    s.accumY[s.accum.size-n:] = 0  # zero rightmost n-elements
    #    #s.setPlotUnits(s.plotUnits) # rel
    #    #s.acmT0  += n  # adjust time of zero-eth datum

    #
    def shiftAccumulatorLeft(s, shiftN):
        print("******************************")
        print("s.accumY:", s.accumY)
        print("******************************")
        print("shiftAccumulatorLeft:", n)
        print("s.acmShiftOffset", s.acmShiftOffset)
        s.acmShiftOffset += shiftN
        print("s.acmShiftOffset", s.acmShiftOffset)

        # [t1, t1+1, t1+2 ... t2-1]
        print("xv[0]", s.xv[0])
        print("xv[1]", s.xv[1])
        s.xv = np.arange(shiftN, s.acmWd + shiftN, 1)
        print("xv[0]", s.xv[0])
        print("xv[1]", s.xv[1])
        print("xv[-2]", s.xv[-2])
        print("xv[-1]", s.xv[-1])

        # shift all elements of array left by n
        # placing elements shifted off left on the right
        # eg: [1,2,3,4] shift 2 = [3,4,1,2]
        #np.concatenate((s.accumY[n:],s.accumY[:n]), n) # rotate left by n
        #s.accumY[s.accum.size-n:] = 0  # zero rightmost n-elements

        # rotate left by shifN
        np.concatenate((s.accumY[shiftN:], s.accumY[:shiftN]), shiftN)
        s.accumY[s.accum.size - shiftN:] = 0  # zero rightmost n-elements

        print("******************************")
        print("s.accumY:", s.accumY)
        print("******************************")

        #    #s.setPlotUnits(s.plotUnits) # rel
        #    #s.acmT0  += n  # adjust time of zero-eth datum

        #s.accumY[s.acNdx] = ydatum
        setPlot(s.plotUnits, s.acmP1 + s.acmShiftOffst, s.acmP2)

    #...........................................................................
    # Plot data as handler for instantiators timer-tick.
    # seconds : seconds from application start.
    # (datum value is repeated if realtime data not being sent)
    #...........................................................................
    def plotDatum(s, seconds, ydatum):
        #print("<plotDatum>",ydatum)
        # OK: s.tSeconds = s.dt0.secsTo(QDateTime().currentDateTime())
        s.tSeconds += 1
        try:
            s.accumY[s.tSeconds - s.acmShiftOffset] = ydatum
        except IndexError as e:
            print("********** Index Error at %d ***********:%s" %
                  (s.tSeconds, e))
            print("Index       :", s.tSeconds)
            #print("Index-Offset:", s.tSeconds-s.acmShiftOffset)
            #shiftAccumlatorLeft(1800)
            #print("Index-Offset:", s.tSeconds-s.acmShiftOffset)
            #s.accumY[s.tSeconds-s.acmShiftOffset] = ydatum
            sys.exit()

        # If AutoMinMax keep min,max values (excludeing datum = 0.0)
        if s.autoMinMax:
            if ydatum != 0 and s.acmMinVal > ydatum:
                s.acmMinVal = ydatum
                s.scaleDirty = True  # force scale redraw

            # set max data value
            if s.acmMaxVal < ydatum:
                s.acmMaxVal = ydatum
                s.scaleDirty = True  # force scale redraw

        if s.scaleDirty:
            s.scaleDirty = False
            if s.autoMinMax:
                s.YScaleTop = s.acmMaxVal + s.acmMaxVal * 0.01
                s.YScaleBtm = s.acmMinVal - s.acmMinVal * 0.01
            else:
                s.YScaleTop = s.fixedScaleTop
                s.YScaleBtm = s.fixedScaleBtm

            s.setYScale(s.YScaleBtm, s.YScaleTop)

        # shift left on plot beyond right edge of stripchart
        if s.tSeconds > s.acmP2:
            if s.plotUnits == Kst.HOURS:
                p1 = s.acmP1 + s.yvShiftHours
                p2 = s.acmP2 + s.yvShiftHours

            elif s.plotUnits == Kst.MINUTES:
                p1 = s.acmP1 + s.yvShiftMinutes
                p2 = s.acmP2 + s.yvShiftMinutes

            else:  # s.plotUnits == Kst.SECONDS
                p1 = s.acmP1 + s.yvShiftSeconds
                p2 = s.acmP2 + s.yvShiftSeconds

            s.setPlot(s.plotUnits, p1, p2)

        # plot
        s.plotv(s.xv, s.yv)

    #...........................................................................
    # Set auto-scaling for y-axis by wrapping
    # QwtPlot's 'setAxisAutoScale' and doing housekeeping
    #
    def setAutoMinMax(s, state):
        #print("setAutoMinMAX:",state)
        s.autoMinMax = state
        s.setAutoMinMaxButton(state)

    #...........................................................................
    # Set instantiator's autoscale-button indicators on/off
    def setAutoMinMaxButton(s, state):
        #print("setAutoMinMaxButton:",state)
        s.autoMinMaxButton.setChecked(state)
        if state:
            s.autoMinMaxButton.setText('A')
        else:
            s.autoMinMaxButton.setText('F')

    #...........................................................................
    # setYScale: set Y-axis fixed-scale high/low values
    #    if step is zero qwtplot calculates stepsize automatically
    #   Calling qwtplot.setAxisScale disables built-in auto-scaling
    #...........................................................................
    def setYScale(s, btm, top, step=0):
        #print("<setYScale>", btm, top)

        #If flag set, force bottom scale = 0
        if s.zeroScaleBase:
            #print("ZeroScaleBase")
            s.YScaleBtm = 0

        # Else set bottom scale to value if btm not none
        elif btm is not None:
            s.YScaleBtm = btm

        # set top scale if not none
        if top is not None:
            s.YScaleTop = top

        # disable autoscaling and set fixed values
        s.setAxisScale(s.yaxisId, s.YScaleBtm, s.YScaleTop, step)
        s.updateAxes()

    #..........................................................................
    # fixedScaleHandler: handle action on popup fixed y-axis range spinners
    #..........................................................................
    def fixedScaleHandler(s, value):
        #print("<fixedScaleHandler> %s %f"% (s.name,value))
        sender = s.sender()
        Xid = s.sender().Xid
        #print("XID>",Xid)
        s.setFixedScale(Xid, value)

    #..........................................................................
    # fixedScaleHandler:
    #..........................................................................
    def setFixedScale(s, Xid, value):

        # handle chart popup upper spinwheel & mouse rubber-band
        # (s.dlg.topSpinner.setValue(value))
        if Xid == 'SP1':
            s.fixedScaleTop = s.pDct['fixedScaleMax']['value'] = value
            s.setAutoMinMax(False)
            s.setYScale(None, s.fixedScaleTop)

        # handle chart popup lower spinwheel & mouse rubber-band
        elif Xid == 'SP2':
            s.fixedScaleBtm = s.pDct['fixedScaleMin']['value'] = value
            s.setAutoMinMax(False)
            s.setYScale(s.fixedScaleBtm, None)

        # A/F button
        # handle Auto/Fixed range button toggle
        elif Xid == 'RB1':
            # value = true:false
            # Set instantiator's autoscale-button indicators on/off
            # value is button state
            s.scaleDirty = True  # force Y-axis scale redraw
            s.setAutoMinMax(value)  # turn auto-scaling on/off
            s.setYScale(s.fixedScaleBtm, s.fixedScaleTop)

        # Z-button
        # handle zeroScaleBase button
        elif Xid == 'RB2':
            s.zeroScaleBase = value  # True/False
            s.scaleDirty = True  # force Y-axis scale redraw
        else:
            lg.error("<fixedScaleHandler> %s unknown caller" % s.name)


#------------------------------------------------------------------------------
# Class TimeScaleDraw
#------------------------------------------------------------------------------
class TimeScaleDraw(Qwt.QwtScaleDraw):

    def __init__(s, unit, when='now', timespec=Qt.LocalTime):

        Qwt.QwtScaleDraw.__init__(s)
        s.unit = unit
        s.setLabelAlignment(Qt.AlignLeft | Qt.AlignBottom)
        #s.setLabelRotation(-25.0)
        s.dt0 = tUtil.setTime(when, timeSpec=timespec)

        #print("................ TimescaleDraw ............")
        #tUtil.prnTime(s.dt0)
        #tUtil.setTimeI(s.dt0, s.dt0.time().hour(),0,0) # zero minutes & seconds
        #tUtil.prnTime(s.dt0)
        #print("............................")

        # set tick lengths
        s.setTickLength(Qwt.QwtScaleDiv.MinorTick, 4)
        s.setTickLength(Qwt.QwtScaleDiv.MediumTick, 8)
        s.setTickLength(Qwt.QwtScaleDiv.MajorTick, 12)

    # plot will call this to label ticks
    def label(s, secs):
        dt = s.dt0.addSecs(secs)

        if s.unit == Kst.SECONDS:
            #print("TimeScaleDraw:", dt.toString('hh:mm:ss'))
            return Qwt.QwtText(dt.toString('hh:mm:ss'))
        else:
            return Qwt.QwtText(dt.toString('hh:mm'))

    def str(s, secs):
        dt = s.dt0.addSecs(secs)
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
#
#-----------------------------------------------------------------------
if __name__ == "__main__":

    from PyQt4.QtGui import (QApplication)

    app = QApplication(sys.argv)

    wdg = Stripchart(name='TipTilt', xtickrange=[-1, 1], ytickrange=[-1, 1],
                     axisTitle='Error')

    wdg = Stripchart(name='TipTilt', xtickrange=[-1, 1], ytickrange=[-1, 1],
                     axisTitle='Error')

    wdg.resize(300, 100)
    wdg.show()
    app.exec_()  # Gui loop
    sys.exit()

    #-----------------------------------------------------------------------
    #
    # shift array left by 1
    # & assign new value to the end
    #s.fakeyv =  concatenate((s.fakeyv[1:], s.fakeyv[:1]), 1)
    #s.fakeyv[-1] = random.uniform(-100,100)
    #
    # shift array left by 10
    # & assign 10 new values to the end
    # s.fakeyv =  concatenate((s.fakeyv[10:], s.fakeyv[:10]), 1)
    # s.fakeyv[90:100] =  x
    #-----------------------------------------------------------------------
    #def timerEvent(s, e):
    #    x = random.uniform(-s.xvLen,s.xvLen,10)
    #    # shift array left by 10 & set 10 new values at end
    #    s.fakeyv =  concatenate((s.fakeyv[10:], s.fakeyv[:10]), 1)
    #    s.fakeyv[s.xvLen-10:s.xvLen] =  x
    #    s.plot1.setData(s.fakexv, s.fakeyv)
    #    s.replot()

    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------
    #def fakedata(s):
    #    s.fakexv = arange(0.0, 300.1, 1)
    #    s.xvLen =  len(s.fakexv)
    #    s.fakeyv = zeros(s.xvLen, Float)
    #    #s.fakeyv = arange(0.0, 100.1, 1)
    #    s.fake   = True
    #    s.startTimer(1000)

    #s.grid  = Qwt.QwtPlotGrid()
    #s.xdiv  = Qwt.QwtScaleDiv()
    #s.xdiv.setInterval(10,100)
    #s.grid.setXDiv(s.xdiv)
    #s.grid.attach(s)
    #s.grid.setYDiv()

    #s.setTitle(kwargs['name'])
    #s.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);
    #s.insertLegend(Qwt.QwtLegend(),Qwt.QwtPlot.BottomLegend);

    #QwtScaleWidget *qwtsw = myqwtplot.axisWidget(QwtPlot::xBottom);
    #QPalette palette = qwtsw->palette();
    #palette.setColor( QPalette::WindowText, Qt::gray); // for ticks
    #palette.setColor( QPalette::Text, Qt::gray); // for ticks' labels
    #qwtsw->setPalette( palette );
    #cnv = s.plot1.canvas()
    #wdg = s.plot1.axisWidget(Qwt.QwtPlot.BottomLegend)

    #s.plot1.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
    #                                QBrush(),
    #                                QPen(Qt.green),
    #                                QSize(2, 2)))
    #mY = Qwt.QwtPlotMarker()
    #mY.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)
    #mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
    #mY.setYValue(0.0)
    #mY.attach(s)
    #s.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (seconds)")
    #s.setAxisTitle(Qwt.QwtPlot.yLeft, kwargs['axisTitle'])

    #s.startTimer(1000)

    ####
    #s.setAxisAutoScale(False) #position of this statement matters
    #nHours       = 4
    #s.leftright  = [ -10, 10]
    #interval =
    #ticks    =  60
    #s.setAxisScaleDiv(..., QwtScaleDiv(interval,ticks)
    #s.setAxisScaleDiv(..., QwtScaleDiv(interval,ticks)
    #s.setAxisScale(s.xBottom, s.leftright[0], s.leftright[1] )

#QwtScaleDiv scaleDiv = scaleEngine.divideScale(...);
#QwtValueList majorTicks = scaleDiv.ticks[QwtScaleDiv::MajorTick];
#majorTicks += interval.minValue () + interval.maxValue()) / 2);
#scaleDiv.setTicks(QwtScaleDiv::MajorTick, majorTicks);
#s.setAxisScale(s.xBottom,   0,    3600    )
#majorTicks   = s.xdiv.ticks[Qwt.QwtScaleDiv.MajorTick]
#s.xdiv.setInterval(intervalMin,intervalMax)
#s.xdiv.setTicks(Qwt.QwtScaleDiv.MajorTick, 30);
#enum      TickType {
#  NoTick = -1,
#  MinorTick,
#  MediumTick,
#  MajorTick,
#  NTickTypes
#}

# QwtPlotAbstractSeriesItem::setOrientation(Qt::Orientation orientation    )
#
#enum      CurveStyle {
#  NoCurve = -1,
#  Lines,
#  Sticks,
#  Steps,
#  Dots,
#  UserCurve = 100
#}

#s.plotSpeed = float(rate)
#s.frameRate = s.cfg.framesPerChart
#s.cfg.framesPerChart = s.plotSpeed * s.frameRate

#s.plot1.setXAxis(s.xv)

#for i in range(s.axisCnt):
#    scaleWidget = s.axisWidget(i)
#    if scaleWidget:
#        scaleWidget.set_axis_direction(reverse=True)

#def draw(self, painter, xMap, yMap, rect):
#> >         # Look at the ImagePlotDemo how to use the map
#> >       # and how you might try to draw the scales:
#> >         # 1. figure out the scale position in pixels
#> >       # 2. figure out the scale length in pixels
#> >         # 3. draw the scale (see QwtAbstractScaleDraw.draw())

#    def NOTdraw(self, painter, xMap, yMap, rect):
#        #if self.__axis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
#        #    self.scaleDraw.move(round(xMap.xTransform(0.0)), yMap.p2())
#        #    self.scaleDraw.setLength(yMap.p1()-yMap.p2())
#        #elif self.__axis in (Qwt.QwtPlot.xBottom, Qwt.QwtPlot.xTop):
#        #    self.scaleDraw.move(xMap.p1(), round(yMap.xTransform(0.0)))
#        #    self.scaleDraw.setLength(xMap.p2()-xMap.p1())
#        self.draw.setScaleDiv(self.div)
#        self.draw(painter, self.plot().palette())

#...........................................................................
#    def setPlotTicks(s):
#        print("<Stripchart.setPlotTicks")
#        print("xvMax:", s.xvMax)
#
#        # make list of ticks from 0 to xvMax at intervals of 60 & 3600
#        sticks = []
#        mticks = map(None, np.arange(0,s.tMax,  60, dtype=int))
#        hticks = map(None, np.arange(0,s.tMax,3600,  dtype=int))
#        ticks = [sticks, mticks, hticks]
#        print("mticks", mticks)
#        print("hticks", hticks)
#
#
#        # order matters
#        #s.scdiv = Qwt.QwtScaleDiv()
#        #s.scdiv.setInterval(0,60)
#        #s.scdiv.setTicks(Qwt.QwtScaleDiv.MajorTick, mticks);
#        #s.setAxisScaleDiv (s.xBottom, s.scdiv)
#
#
#        # Scale Divisions
#        #s.scdiv = Qwt.QwtScaleDiv(
#        #    ticks[Qwt.QwtScaleDiv.MajorTick].first(), \
#        #    ticks[Qwt.QwtScaleDiv.MajorTick].last() , \
#        #    ticks)
#        #s.scdiv = Qwt.QwtScaleDiv( 0.0, double(s.maxSeconds), ticks)
#        #s.setAxisScaleDiv (s.xBottom, s.scdiv)
#
#        s.scdiv = Qwt.QwtScaleDiv()
#        s.scdiv.setTicks(Qwt.QwtScaleDiv.MajorTick, mticks);
#
#        s.setAxisScaleDiv (s.xBottom, s.scdiv)
#
#        #s.setAxisScale    (s.xBottom,   0,    s.xvMax  )

#s.axes_reverse[s.xaxisId]

#    def draw(self, painter, xMap, yMap, rect):
#        #if self.__axis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
#        #    self.scaleDraw.move(round(xMap.xTransform(0.0)), yMap.p2())
#        #    self.scaleDraw.setLength(yMap.p1()-yMap.p2())
#        #elif self.__axis in (Qwt.QwtPlot.xBottom, Qwt.QwtPlot.xTop):
#        #    self.scaleDraw.move(xMap.p1(), round(yMap.xTransform(0.0)))
#        #    self.scaleDraw.setLength(xMap.p2()-xMap.p1())
#        self.draw.setScaleDiv(self.div)
#        self.draw(painter, self.plot().palette())
#
#
#
#        #division = s.scaleDiv()
#        #interval = s.scaleDiv().interval()
#        #interval.setMinValue(0)
#        #interval.setMaxValue(60)
#        #print("interval min:", interval.minValue())
#        #print("interval max:", interval.maxValue())
#        #interval.setBorderFlags(Qwt.QwtInterval.IncludeBorders)
#
#
#
#        #############################################################3
#        # y moves from left to right:
#        # shift y array right and assign new value y[0]
#        self.y = concatenate((self.y[:1], self.y[:-1]), 1)
#        self.y[0] = sin(self.phase) * (-1.0 + 2.0*random.random())
#
#        # z moves from right to left:
#        # Shift z array left and assign new value to z[n-1].
#        self.z = concatenate((self.z[1:], self.z[:1]), 1)
#        self.z[-1] = 0.8 - (2.0 * self.phase/pi) + 0.4*random.random()
#
#        self.curveR.setData(self.x, self.y)
#        self.curveL.setData(self.x, self.z)
#        self.replot()
#        self.phase += pi*0.02
#
#
#

# create plot time vector mapped to time in seconds of y-vector data
#s.xv = np.arange(s.acmP1, s.acmP2,  1) # [t1, t1+1, t1+2 ... t2-1]
#s.xv = np.arange(0, 2*3600,  1) # [t1, t1+1, t1+2 ... t2-1]

#...........................................................................
#
#...........................................................................
#def alignScales(s):
#    print("************* alignScales ***********")
#    s.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
#    s.canvas().setLineWidth(1)
#    for i in range(s.axisCnt):
#        scaleWidget = s.axisWidget(i)
#        if scaleWidget:
#            scaleWidget.setMargin(0)
#        scaleDraw = s.axisScaleDraw(i)
#
#        if scaleDraw:
#            scaleDraw.enableComponent(
#                Qwt.QwtAbstractScaleDraw.Backbone, False)

#print("Inteval: " , s.axisInterval(s.xAxisId),s.axisInterval(s.yAxisId)
#s.setItemAttribute(QwtPlotItem::AutoScale, state);
#s.setItemAttribute(s.yAxisId.AutoScale, state);
#onOff = s.setAxisAutoScale(s.xaxisId)
#print("Xax", onOff)
#onOff = s.setAxisAutoScale(s.yaxisId)
#print("Yax", onOff)
#s.setAxisAutoScale(s.yaxisId, False)
#s.scaleDirty = True
#s.updateLayout()
#s.autoRefresh()

#...........................................................................
#    def GOODsetSecScaleDraw(s, t1, t2):
#        print("<Stripchart.setScaleDraw>", t1,t2)
#
#        # division ticks
#        minTicks = map(None, np.arange(t1, t2,   1, dtype=int))
#        medTicks = map(None, np.arange(t1, t2,  10, dtype=int))
#        majTicks = map(None, np.arange(t1, t2,  60, dtype=int))
#
#        ticks = [minTicks, medTicks, majTicks]
#        #s.div = Qwt.QwtScaleDiv(t1, t2, majTicks, medTicks, minTicks)
#        #s.div.setInterval(t1,t2)
#        #s.setAxisScaleDiv(s.xaxisId,s.div)
#
#        # draw : create a scale-draw instance
#        s.draw = TimeScaleDraw(s.plotUnits, when=s.dt0.addSecs(t1),timespec=s.timeSpec)
#        s.setAxisScaleDraw(s.xaxisId, s.draw)
#        #s.setAxisScale(s.xaxisId, t1,t2,1)

# UNDER DEVELOPMENT
#def setPlotStyle(s, style):
#    s.plot1.setStyle(Qwt.QwtPlotCurve.Steps)   # steps
#    s.plot1.setStyle(Qwt.QwtPlotCurve.Lines)   # lines
#    s.plot1.setStyle(Qwt.QwtPlotCurve.XCross)  # Cross
#    # circle-on-stick
#    s.plot1.setPen(Qt.QPen(Qt.Qt.red))
#    s.plot1.setStyle(Qwt.QwtPlotCurve.Sticks)
#    s.plot1.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
#                                  Qt.QBrush(Qt.Qt.yellow),
#                                  Qt.QPen(Qt.Qt.blue),
#                                  Qt.QSize(5, 5)))

#...........................................................................
#def resetPlot(s):
#    #s.xv    = arange(range, 0.1, -1)    # 0 --> ,  left to right [0 300]
#    #s.yv    = zeros (range, dtype=float) # zero data
#    s.accumY[0:]  = 0.0
#    s.yv[0:] = 0.0

#...........................................................................
# shift accumY left by N.  Zero rightmost N elements
# subtract acmShift from s.acNdx
#
# vv = np.arange(1,11,1) # nelements = 10
# n=3; x=v;x = np.concatenate((v[n:],v[:n]),n); x[v.size-n:]=0;v; x
#def shiftAccumulatorLeft(s, n):
#    #print("shiftAccumulatorLeft:",n)
#
#    s.qttT0.adjust(n)  # increase accumulatort zeroeth element time
#    #s.qttT0.prnTimes()
#    s.setSCaleDraw()   # correct tick label times. (uses qttT0)
#
#    # shift all elements of array left by n
#    # placing elements shifted off left on the right
#    # eg: [1,2,3,4] shift 2 = [3,4,1,2]
#    np.concatenate((s.accumY[n:],s.accumY[:n]), n)
#    s.accumY[s.accum.size-n:] = 0  # zero rightmost n-elements

#    #s.setPlotUnits(s.plotUnits) # rel
#    #s.acmT0  += n  # adjust time of zero-eth datum
