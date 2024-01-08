#!/usr/bin/python
"""
Stripchart:
"""
from __future__ import absolute_import, print_function, division
import sys, time
import numpy as np
from PyQt4 import QtCore
from PyQt4.QtGui import (QWidget, QSizePolicy, QFrame, QBrush, QPen, QColor)
from PyQt4.QtCore import (Qt, QTimer, QObject, SIGNAL, QObject, QSize)
import random
import Configuration
import Constants as Kst
import PyQt4.Qwt5 as Qwt
#from PyQt4.Qwt5.anynumpy import *
from numpy import zeros


#------------------------------------------------------------------------------
#
# Notes:
# Change the color of the qwt plot axis, numbers and ticks
#   myplot->axisWidget (QwtPlot::xBottom)->setPalette (palette).
#------------------------------------------------------------------------------
class ttplotWidget(Qwt.QwtPlot):

    #...........................................................................
    #
    #...........................................................................
    def __init__(s, *args, **kwargs):
        Qwt.QwtPlot.__init__(s, *args)

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.MountXDct = None  # tiltx alarm dictionary must be set by caller
        s.MountYDct = None  # tilty alarm dictionary must be set by caller
        s.alarmState = False

        if s.cfg.debug: print("<ttplotWidget.__init__>", kwargs['name'])

        # kwargs
        s.wd = kwargs['wd']
        s.ht = kwargs['ht']
        s.name = kwargs['name']
        s.axisTitle = kwargs['axisTitle']
        s.leftright = kwargs['xtickrange']
        s.bottop = kwargs['ytickrange']

        s.margin = 0
        s.minSize = s.wd - s.margin
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  #hrz,vrt

        s.plotLayout().setMargin(s.margin)
        s.plotLayout().setCanvasMargin(s.margin)

        s.hAlarm = None
        s.lAlarm = None

        #s.setTitle(kwargs['axisTitle'])
        #s.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)

        # scales
        s.setAxisAutoScale(False)  #position of this statement matters
        s.setAxisScale(s.xBottom, s.leftright[0], s.leftright[1])
        s.setAxisScale(s.yLeft, s.bottop[0], s.bottop[1])

        s.setAxisAutoScale(False)  #position of this statement matters
        s.setAxisScale(s.xBottom, s.leftright[0], s.leftright[1])
        s.setAxisScale(s.yLeft, s.bottop[0], s.bottop[1])

        #s.setAxisScale(s.xBottom, -10, 14400)

        #s.setAxisTitle(s.xBottom, 'X volts')
        #s.setAxisTitle(s.yLeft,   'Y volts')
        #s.plotLayout().setAlignCanvasToScales(True)

        s.cnv = s.canvas()
        s.cnv.setFrameStyle(QFrame.Box | QFrame.Plain)
        pal = s.cnv.palette()

        # stylesheet items 'color', gridline-color,background-color,
        # set plot backgound
        s.setCanvasBackground(QColor(Kst.TTPLOTBACKGROUND))
        #s.setCanvasBackground(QColor('#FFFFFF'))
        #s.setCanvasBackground(QColor(Kst.TTPLOTGRID))

        # set foreground color
        s.setStyleSheet("color:%s" % '#00FF00')

        # create & attach grid
        s.grid = Qwt.QwtPlotGrid()

        pen = QPen(QColor(Kst.STRIPCHARTGRID))  # create pen & set color
        pen.setDashPattern([1, 6])  # set pen linestyle

        #s.grid.setMajPen(QPen(Qt.green,  0, Qt.DotLine))
        s.grid.setMajPen(pen)
        #s.grid.setMinPen(QPen(Qt.green,  0, Qt.DotLine))
        s.grid.enableXMin(True)
        s.grid.enableYMin(True)
        s.grid.attach(s)

        # plot
        s.plot = Qwt.QwtPlotCurve()
        s.plot.attach(s)

        # no x/y scale line, ticks, labels
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleDraw = s.axisScaleDraw(i)
            scaleDraw.enableComponent(Qwt.QwtAbstractScaleDraw.Backbone, False)

            scaleDraw.enableComponent(Qwt.QwtAbstractScaleDraw.Ticks, False)

            scaleDraw.enableComponent(Qwt.QwtAbstractScaleDraw.Labels, False)

        #s.plot.setPen(QPen(Qt.green))
        s.plot.setSymbol(
                Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse, QBrush(Qt.green),
                              QPen(Qt.white), QSize(12, 12)))

        # Cartesian axes
        xaxis = CartesianAxis(s.xBottom, s.yLeft)
        yaxis = CartesianAxis(s.yLeft, s.xBottom)

        xaxis.attach(s)
        yaxis.attach(s)

        s.phase = 0.0
        s.dataready_count = 0
        s.frameN = None
        s.frameCount = 0
        s.rawData = None
        s.fdata = None
        s.displayRate = 1  # plot after this many frames

        s.nDots = 1
        s.xv = zeros(s.nDots, dtype=float)
        s.yv = zeros(s.nDots, dtype=float)

        s.timerId = None
        s.fakeData = False
        #s.sizePolicy().setHeightForWidth(True)

    #...........................................................................
    #
    #...........................................................................
    def timerEvent(s, e):
        s.xv[0] = random.uniform(-1, 1)
        s.yv[0] = random.uniform(-1, 1)
        s.plot.setData(s.xv[:1], s.yv[:1])
        s.replot()

    #...........................................................................
    # data_ready x,y :
    # s.xv[0] = data[Kst.DM_TTMOUNTX]
    # s.yv[0] = data[Kst.DM_TTMOUNTY]
    #...........................................................................
    def data_ready(s, x, y):

        if s.fakeData: return
        s.xv[0] = x
        s.yv[0] = y

        if s.cfg.debug >= Kst.DBGLEVEL_RATE1:
            print(s.name, "Tt Mount:", s.xv[0], s.yv[0])

        s.checkAlarms(x, y)
        s.plot.setData(s.xv[:1], s.yv[:1])
        s.replot()

    # Check X/Y hi & low alarms
    # If alarm-state is unchanged, do nothing.
    # If alarm-state is True and is a new state, set new state
    # and color background alarm color.
    # If alarm-state is False and is a new state, set alarm
    # and color background no-alarm color
    def checkAlarms(s, x, y):
        alarmState = Kst.NOALARM

        #print ("%s: %f,%f"% (s.name,x,y))

        # High X Alarm?
        if s.MountXDct['alarmHi' ]['enable'] \
        and x >= s.MountXDct['alarmHi' ]['value']:
            alarmState = Kst.HIGHALARM

        # Low X Alarm?
        elif s.MountXDct['alarmLow']['enable'] \
        and x <= s.MountXDct['alarmLow']['value']:
            alarmState = Kst.LOWALARM

        # High Y Alarm?
        if s.MountYDct['alarmHi' ]['enable'] \
        and y >= s.MountYDct['alarmHi' ]:
            alarmState = Kst.HIGHALARM

        # Low Y Alarm?
        elif s.MountYDct['alarmLow']['enable'] \
        and y <= s.MountYDct['alarmLow']:
            alarmState = Kst.LOWALARM

        # Set alarm colors only if alarm state transitions.
        # If alarm-state is unchanged, do nothing
        if alarmState == s.alarmState:
            pass  # do nothing if same state

        # New state: if alarm-state HIGH set high alarm color
        elif alarmState == Kst.HIGHALARM:
            s.lg.warn("%s : High Alarm x:%f y%f" % (s.name, x, y))
            s.setStyleSheet(" QWidget {background-color:%s}" % Kst.ALARMRED)
            #s.setStyleSheet("color:%s"%Kst.ALARMRED )
            #s.setStyleSheet("color:%s"%'#00FF00')

        # New state: if alarm-state low set low alarm color
        elif alarmState == Kst.LOWALARM:
            s.lg.warn("%s : Low Alarm x:%f y%f" % (s.name, x, y))
            s.setStyleSheet(" QWidget {background-color:%s}" % Kst.ALARMYELLOW)

        # New state: if no-alarm, set no-alarm color
        else:
            s.lg.warn("%s : Alarm Off x:%f y%f" % (s.name, x, y))
            s.setStyleSheet("color:%s" % '#00FF00')

        s.alarmState = alarmState

    #...........................................................................
    #
    #...........................................................................
    #def alignScales(s):
    #    s.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
    #    s.canvas().setLineWidth(1)
    #    for i in range(Qwt.QwtPlot.axisCnt):
    #        scaleWidget = s.axisWidget(i)
    #        if scaleWidget:
    #            scaleWidget.setMargin(0)
    #        scaleDraw = s.axisScaleDraw(i)
    #        if scaleDraw:
    #            scaleDraw.enableComponent(
    #                Qwt.QwtAbstractScaleDraw.Backbone, False)
    #
    def heightForWidth(s, w):
        return (w)

    def heightForWidth(s, w):
        return (w)

    def sizeHint(s):
        return QSize(s.minSize, s.minSize)

    def minimumSizeHint(s):
        return QSize(s.minSize, s.minSize)

    #...........................................................................
    #
    #...........................................................................
    def setFakeData(s):
        if s.fakeData:
            s.fakeData = False
            s.killTimer(s.timerId)  # see QObject

        else:
            s.fakeData = True
            s.timerId = s.startTimer(1000)  # see QObject


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class CartesianAxis(Qwt.QwtPlotItem):
    """Supports a Cartesian coordinate system
    """

    #...........................................................................
    def __init__(self, masterAxis, slaveAxis):
        """Valid input values for masterAxis and slaveAxis are QwtPlot.yLeft,
        QwtPlot.yRight, QwtPlot.xBottom, and QwtPlot.xTop. When masterAxis is
        an x-axis, slaveAxis must be an y-axis; and vice versa.
        """
        Qwt.QwtPlotItem.__init__(self)
        self.__axis = masterAxis
        if masterAxis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
            self.setAxis(slaveAxis, masterAxis)
        else:
            self.setAxis(masterAxis, slaveAxis)
        self.scaleDraw = Qwt.QwtScaleDraw()
        self.scaleDraw.setAlignment(
                (Qwt.QwtScaleDraw.LeftScale, Qwt.QwtScaleDraw.RightScale,
                 Qwt.QwtScaleDraw.BottomScale,
                 Qwt.QwtScaleDraw.TopScale)[masterAxis])

    #...........................................................................
#    def draw(self, painter, xMap, yMap, rect):
#        """Draw an axis on the plot canvas
#        """
#        if self.__axis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
#            self.scaleDraw.move(round(xMap.xTransform(0.0)), yMap.p2())
#            self.scaleDraw.setLength(yMap.p1()-yMap.p2())
#        elif self.__axis in (Qwt.QwtPlot.xBottom, Qwt.QwtPlot.xTop):
#            self.scaleDraw.move(xMap.p1(), round(yMap.xTransform(0.0)))
#            self.scaleDraw.setLength(xMap.p2()-xMap.p1())
#        self.scaleDraw.setScaleDiv(self.plot().axisScaleDiv(self.__axis))
#        self.scaleDraw.draw(painter, self.plot().palette())

#...........................................................................

    def draw(self, painter, xMap, yMap, rect):
        """Draw an axis on the plot canvas
        """
        if self.__axis in (Qwt.QwtPlot.yLeft, Qwt.QwtPlot.yRight):
            self.scaleDraw.move(round(xMap.xTransform(0.0)), yMap.p2())
            self.scaleDraw.setLength(yMap.p1() - yMap.p2())
        elif self.__axis in (Qwt.QwtPlot.xBottom, Qwt.QwtPlot.xTop):
            self.scaleDraw.move(xMap.p1(), round(yMap.xTransform(0.0)))
            self.scaleDraw.setLength(xMap.p2() - xMap.p1())

        self.scaleDraw.setScaleDiv(self.plot().axisScaleDiv(self.__axis))
        self.scaleDraw.draw(painter, self.plot().palette())


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
if __name__ == "__main__":

    from PyQt4.QtGui import (QApplication)
    #from PyQt4 import Qt

    app = QApplication(sys.argv)
    #--------------------------------------
    wdg = ttplotWidget(wd=300, ht=300, name='TipTilt', xtickrange=[-1, 1],
                       ytickrange=[-1, 1], axisTitle='Error')

    wdg.setGeometry(0, 0, 200, 200)  # where to appear on root window
    wdg.resize(400, 300)
    wdg.show()
    app.exec_()  # Gui loop
    sys.exit()

    #s.grid  = Qwt.QwtPlotGrid()
    #s.xdiv  = Qwt.QwtScaleDiv()
    #s.xdiv.setInterval(10,100)
    #s.grid.setXDiv(s.xdiv)
    #s.grid.attach(s)
    #s.grid.setYDiv()
    #s.plot.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
    #                                QBrush(),
    #                                QPen(Qt.green),
    #                                QSize(7, 7)))
