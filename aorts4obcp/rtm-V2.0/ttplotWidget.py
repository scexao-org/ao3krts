#!/usr/bin/python
"""
Stripchart:
"""
from __future__ import absolute_import, print_function, division

import sys

from PyQt5.QtCore import (Qt, QSize)
from PyQt5.QtGui import (QBrush, QPen, QColor)
from PyQt5.QtWidgets import (QSlider, QSizePolicy, QFrame)

import random
import Configuration
import Constants as Kst

from numpy import zeros

import qwt


#------------------------------------------------------------------------------
#
# Notes:
# Change the color of the qwt plot axis, numbers and ticks
#   myplot->axisWidget (QwtPlot::xBottom)->setPalette (palette).
#------------------------------------------------------------------------------
class TTplotWidget(qwt.QwtPlot):

    #...........................................................................
    #
    #...........................................................................
    def __init__(self, *args, **kwargs):
        qwt.QwtPlot.__init__(self, *args)

        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        self.MountXDct = None  # tiltx alarm dictionary must be set by caller
        self.MountYDct = None  # tilty alarm dictionary must be set by caller
        self.alarmState = False

        if self.cfg.debug: print("<ttplotWidget.__init__>", kwargs['name'])

        # kwargs
        self.wd = kwargs['wd']
        self.ht = kwargs['ht']
        self.name = kwargs['name']
        self.axisTitle = kwargs['axisTitle']
        self.leftright = kwargs['xtickrange']
        self.bottop = kwargs['ytickrange']

        self.margin = 0
        self.minSize = self.wd - self.margin
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)  #hrz,vrt

        self.plotLayout().setSpacing(self.margin)
        self.plotLayout().setCanvasMargin(self.margin)

        self.hAlarm = None
        self.lAlarm = None

        #s.setTitle(kwargs['axisTitle'])
        #s.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)

        # scales
        self.setAxisAutoScale(False)  #position of this statement matters
        self.setAxisScale(self.xBottom, self.leftright[0], self.leftright[1])
        self.setAxisScale(self.yLeft, self.bottop[0], self.bottop[1])

        self.setAxisAutoScale(False)  #position of this statement matters
        self.setAxisScale(self.xBottom, self.leftright[0], self.leftright[1])
        self.setAxisScale(self.yLeft, self.bottop[0], self.bottop[1])

        #s.setAxisScale(s.xBottom, -10, 14400)

        #s.setAxisTitle(s.xBottom, 'X volts')
        #s.setAxisTitle(s.yLeft,   'Y volts')
        #s.plotLayout().setAlignCanvasToScales(True)

        self.cnv = self.canvas()
        self.cnv.setFrameStyle(QFrame.Box | QFrame.Plain)
        pal = self.cnv.palette()

        # stylesheet items 'color', gridline-color,background-color,
        # set plot backgound
        self.setCanvasBackground(QColor(Kst.TTPLOTBACKGROUND))
        #s.setCanvasBackground(QColor('#FFFFFF'))
        #s.setCanvasBackground(QColor(Kst.TTPLOTGRID))

        # set foreground color
        self.setStyleSheet("color:%s" % '#00FF00')

        # create & attach grid
        self.grid = qwt.QwtPlotGrid()

        pen = QPen(QColor(Kst.STRIPCHARTGRID))  # create pen & set color
        pen.setDashPattern([1, 6])  # set pen linestyle

        #s.grid.setMajPen(QPen(Qt.green,  0, Qt.DotLine))
        self.grid.setMajPen(pen)
        #s.grid.setMinPen(QPen(Qt.green,  0, Qt.DotLine))
        self.grid.enableXMin(True)
        self.grid.enableYMin(True)
        self.grid.attach(self)

        # plot
        self.plot = qwt.QwtPlotCurve()
        self.plot.attach(self)

        # no x/y scale line, ticks, labels
        for i in range(qwt.QwtPlot.axisCnt):
            scaleDraw = self.axisScaleDraw(i)
            scaleDraw.enableComponent(qwt.QwtAbstractScaleDraw.Backbone, False)

            scaleDraw.enableComponent(qwt.QwtAbstractScaleDraw.Ticks, False)

            scaleDraw.enableComponent(qwt.QwtAbstractScaleDraw.Labels, False)

        #s.plot.setPen(QPen(Qt.green))
        self.plot.setSymbol(
                qwt.QwtSymbol(qwt.QwtSymbol.Ellipse, QBrush(Qt.green),
                              QPen(Qt.white), QSize(12, 12)))

        # Cartesian axes
        xaxis = CartesianAxis(self.xBottom, self.yLeft)
        yaxis = CartesianAxis(self.yLeft, self.xBottom)

        xaxis.attach(self)
        yaxis.attach(self)

        self.phase = 0.0
        self.dataready_count = 0
        self.frameN = None
        self.frameCount = 0
        self.rawData = None
        self.fdata = None
        self.displayRate = 1  # plot after this many frames

        self.nDots = 1
        self.xv = zeros(self.nDots, dtype=float)
        self.yv = zeros(self.nDots, dtype=float)

        self.timerId = None
        self.fakeData = False
        #s.sizePolicy().setHeightForWidth(True)

    #...........................................................................
    #
    #...........................................................................
    def timerEvent(self, e):
        self.xv[0] = random.uniform(-1, 1)
        self.yv[0] = random.uniform(-1, 1)
        self.plot.setData(self.xv[:1], self.yv[:1])
        self.replot()

    #...........................................................................
    # data_ready x,y :
    # s.xv[0] = data[Kst.DM_TTMOUNTX]
    # s.yv[0] = data[Kst.DM_TTMOUNTY]
    #...........................................................................
    def data_ready(self, x, y):

        if self.fakeData: return
        self.xv[0] = x
        self.yv[0] = y

        if self.cfg.debug >= Kst.DBGLEVEL_RATE1:
            print(self.name, "Tt Mount:", self.xv[0], self.yv[0])

        self.checkAlarms(x, y)
        self.plot.setData(self.xv[:1], self.yv[:1])
        self.replot()

    # Check X/Y hi & low alarms
    # If alarm-state is unchanged, do nothing.
    # If alarm-state is True and is a new state, set new state
    # and color background alarm color.
    # If alarm-state is False and is a new state, set alarm
    # and color background no-alarm color
    def checkAlarms(self, x, y):
        alarmState = Kst.NOALARM

        #print ("%s: %f,%f"% (s.name,x,y))

        # High X Alarm?
        if self.MountXDct['alarmHi' ]['enable'] \
        and x >= self.MountXDct['alarmHi' ]['value']:
            alarmState = Kst.HIGHALARM

        # Low X Alarm?
        elif self.MountXDct['alarmLow']['enable'] \
        and x <= self.MountXDct['alarmLow']['value']:
            alarmState = Kst.LOWALARM

        # High Y Alarm?
        if self.MountYDct['alarmHi' ]['enable'] \
        and y >= self.MountYDct['alarmHi' ]:
            alarmState = Kst.HIGHALARM

        # Low Y Alarm?
        elif self.MountYDct['alarmLow']['enable'] \
        and y <= self.MountYDct['alarmLow']:
            alarmState = Kst.LOWALARM

        # Set alarm colors only if alarm state transitions.
        # If alarm-state is unchanged, do nothing
        if alarmState == self.alarmState:
            pass  # do nothing if same state

        # New state: if alarm-state HIGH set high alarm color
        elif alarmState == Kst.HIGHALARM:
            self.lg.warn("%s : High Alarm x:%f y%f" % (self.name, x, y))
            self.setStyleSheet(" QWidget {background-color:%s}" % Kst.ALARMRED)
            #s.setStyleSheet("color:%s"%Kst.ALARMRED )
            #s.setStyleSheet("color:%s"%'#00FF00')

        # New state: if alarm-state low set low alarm color
        elif alarmState == Kst.LOWALARM:
            self.lg.warn("%s : Low Alarm x:%f y%f" % (self.name, x, y))
            self.setStyleSheet(" QWidget {background-color:%s}" %
                               Kst.ALARMYELLOW)

        # New state: if no-alarm, set no-alarm color
        else:
            self.lg.warn("%s : Alarm Off x:%f y%f" % (self.name, x, y))
            self.setStyleSheet("color:%s" % '#00FF00')

        self.alarmState = alarmState

    #...........................................................................
    #
    #...........................................................................
    def heightForWidth(self, w):
        return (w)

    def heightForWidth(self, w):
        return (w)

    def sizeHint(self):
        return QSize(self.minSize, self.minSize)

    def minimumSizeHint(self):
        return QSize(self.minSize, self.minSize)

    #...........................................................................
    #
    #...........................................................................
    def setFakeData(self):
        if self.fakeData:
            self.fakeData = False
            self.killTimer(self.timerId)  # see QObject

        else:
            self.fakeData = True
            self.timerId = self.startTimer(1000)  # see QObject


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class CartesianAxis(qwt.QwtPlotItem):
    """Supports a Cartesian coordinate system
    """

    #...........................................................................
    def __init__(self, masterAxis, slaveAxis):
        """Valid input values for masterAxis and slaveAxis are QwtPlot.yLeft,
        QwtPlot.yRight, QwtPlot.xBottom, and QwtPlot.xTop. When masterAxis is
        an x-axis, slaveAxis must be an y-axis; and vice versa.
        """
        qwt.QwtPlotItem.__init__(self)
        self.__axis = masterAxis
        if masterAxis in (qwt.QwtPlot.yLeft, qwt.QwtPlot.yRight):
            self.setAxis(slaveAxis, masterAxis)
        else:
            self.setAxis(masterAxis, slaveAxis)
        self.scaleDraw = qwt.QwtScaleDraw()
        self.scaleDraw.setAlignment(
                (qwt.QwtScaleDraw.LeftScale, qwt.QwtScaleDraw.RightScale,
                 qwt.QwtScaleDraw.BottomScale,
                 qwt.QwtScaleDraw.TopScale)[masterAxis])

    #...........................................................................
    def draw(self, painter, xMap, yMap, rect):
        """Draw an axis on the plot canvas
        """
        if self.__axis in (qwt.QwtPlot.yLeft, qwt.QwtPlot.yRight):
            self.scaleDraw.move(round(xMap.transform(0.0)), yMap.p2())
            self.scaleDraw.setLength(yMap.p1() - yMap.p2())
        elif self.__axis in (qwt.QwtPlot.xBottom, qwt.QwtPlot.xTop):
            self.scaleDraw.move(xMap.p1(), round(yMap.transform(0.0)))
            self.scaleDraw.setLength(xMap.p2() - xMap.p1())

        self.scaleDraw.setScaleDiv(self.plot().axisScaleDiv(self.__axis))
        self.scaleDraw.draw(painter, self.plot().palette())


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication
    #from PyQt4 import Qt

    app = QApplication(sys.argv)
    #--------------------------------------
    wdg = TTplotWidget(wd=300, ht=300, name='TipTilt', xtickrange=[-1, 1],
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
