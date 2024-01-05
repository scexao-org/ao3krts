#===============================================================================
# File : LensletWidget.py
#      : Offers class 'LensletWidget'. A 4X4 map of Shack-Hartmann Lenslet array
#        used with Subaru adaptive optics.
#
# Notes:
#
# o Quadrants are numbered as:
#        Q2 Q1
#        Q4 Q3
#
# o Element on device are numbered as follows:
#         6,5    2,1
#         8,7    4 3
#
#        14,13  10  9
#        16,15  12 11
#
#===============================================================================
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import sys, time, random

from PyQt4.QtCore import (
        Qt,
        SIGNAL,
        SLOT,
        QPoint,
        QPointF,
        QRect,
        QRectF,
        QLine,
        QTimer,
        QString,
        QSize,
)
from PyQt4.QtGui import (QRegion, QColor, QColorDialog, QPainter, QPainterPath,
                         QPixmap, QWidget, QFrame, QPalette, QStyleOption,
                         QSizePolicy, QMenu, QSplitter, QVBoxLayout, QPolygon,
                         QPen)

from math import *
import numpy as np
import Configuration
import Constants as Kst
#import rotationArrow
#import rotatePixmap
import ttplotWidget

# Mouse buttons
LMB = 1
MMB = 4
RMB = 2


#------------------------------------------------------------------------------
# LensletWidget
#------------------------------------------------------------------------------
class SHWidget(QWidget):

    #.......................................................................
    def __init__(s, parent=None):
        super(SHWidget, s).__init__(parent)

        s.cfg = Configuration.cfg
        if s.cfg.debug: print("<SHWidget.__init__>")
        s.name = "SHwdg"
        s.alarmDlg = None  # to be set by instantiater
        s.minSize = 200
        s.margin = 4
        s.LogicalSize = s.minSize + s.margin
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #------------------------------------------------------------------
        # TTMODE Vectors : 4 rotation vectors for display as variable length
        # lines from 4 centers of rotation
        # see TTMODEX, TTMODEY data
        #

        offset = 50 + s.margin
        k2 = 2 * s.margin
        s.xoff1 = offset
        s.yoff1 = offset

        s.xoff2 = offset * 3 - k2
        s.yoff2 = offset

        s.xoff3 = offset
        s.yoff3 = offset * 3 - k2

        s.xoff4 = offset * 3 - k2
        s.yoff4 = offset * 3 - k2

        s.arw1qp0 = QPointF(float(s.xoff1), float(s.yoff1))  #rotation base
        s.arw1qp1 = QPointF(float(s.xoff1),
                            float(s.yoff1))  #tip @ zero len @startup

        s.arw2qp0 = QPointF(float(s.xoff2), float(s.yoff2))
        s.arw2qp1 = QPointF(float(s.xoff2), float(s.yoff2))

        s.arw3qp0 = QPointF(float(s.xoff3), float(s.yoff3))
        s.arw3qp1 = QPointF(float(s.xoff3), float(s.yoff3))

        s.arw4qp0 = QPointF(float(s.xoff4), float(s.yoff4))
        s.arw4qp1 = QPointF(float(s.xoff4), float(s.yoff4))

        s.linePen = QPen()  # pen for vector linedraw
        s.linePen.setColor(Qt.green)
        s.linePen.setCapStyle(Qt.RoundCap)
        s.linePen.setWidth(3)
        s.paintVectors = True  # these will be four dots at startup

        #.......................................................................
        s.load_rects()
        s.nCells = 16  # number of shack-hartmann cells in 4x4 array
        s.mousepoint = QPoint(0, 0)
        s.contrastK = 1
        s.brightnessK = 1
        s.datacount = 0

        s.firstdata = True
        s.mins = np.zeros(600, dtype=float)
        s.maxs = np.zeros(600, dtype=float)
        s.vars = np.zeros(600, dtype=float)

        s.hAlarm = 0
        s.lAlarm = 0
        s.lAlarmEnable = False
        s.hAlarmEnable = False

        s.HighAlarmColor = QColor(Kst.CELLALARMRED)  # color of high alarm
        s.LowAlarmColor = QColor(Kst.CELLALARMYLW)  # color of low alarm

        #.......................................................................
        s.constantMin = Kst.SHMIN
        s.constantMax = Kst.SHMAX
        s.init_colormaps()
        #s.set_normalization_constants()

        s.frameN = 0  # Dataframe number sent with data
        s.frameCount = 0  # Our private data-frame counter
        s.cellData = np.zeros((s.nCells), dtype=float)
        s.cellSCData = np.zeros((s.nCells), dtype=float)
        s.intData = np.zeros((s.nCells), dtype=int)

        # bump intensity toward high end of color scale
        s.colorOffset = 100
        for i in range(0, s.nCells):
            s.intData[i] = i + s.colorOffset

        s.cellDataMin = None
        s.cellDataMax = None
        s.cellDataVar = None
        s.cellDataAvg = None

        s.TtModeX = 0  # plotDotX
        s.TtModeY = 0  # plotDotY
        s.pdk = float(300)
        s.tmpData = np.zeros((s.nCells), dtype=float)
        s.stats = np.zeros((600), dtype=float)  # 60sec * 10Hz
        #.......................................................................
        s.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        s.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        s.wheelIncr = 120  # probable delta from wheel event=ev.delta
        #.......................................................................
        s.painter = QPainter()
        s.paintcount = 0
        #s.ppath        = QPainterPath()
        s.pencolor = Qt.black
        s.brushcolor = Qt.green
        s.selectedCell = None
        #s.plotwdg = ttplotWidget.ttplotWidget(
        #             parent    = s.parent,
        #             wd=100,ht=100,
        #             name='TipTilt',
        #             xtickrange=[-1,1], ytickrange=[-1,1],
        #             axisTitle ='Error'  )
        #
        #  0,1 |  4, 5
        #  2,3 |  6, 7
        #  ----+------
        #  8, 9|  12,13
        # 10,11|  14,15
        #
        #
        #   Q2   Q1
        #  6,5 | 2, 1
        #  8,7 | 4, 3
        # -----+------
        # 14,13| 10, 9
        # 16,15| 12,11
        #   Q4    Q3
        s.cellMap = (6, 5, 8, 7, 2, 1, 4, 3, 14, 13, 16, 15, 10, 9, 12, 11)

    #...........................................................................
    def heightForWidth(s, w):
        #print("<SHWidget>.heightForWidth>",w)
        return (w)

    #...........................................................................
    def sizeHint(s):
        return QSize(s.minSize, s.minSize)

    #...........................................................................
    def minimumSizeHint(s):
        return QSize(s.minSize, s.minSize)

    #...........................................................................
    def resizeEvent(s, ev):
        pass

    #...........................................................................
    def paintEvent(s, ev):
        s.paint()
        ev.accept()

    #-----------------------------------------------------------------------
    def paint(s):
        wd = s.width()
        ht = s.height() * 0.8
        side = min(wd, ht)
        s.painter.begin(s)
        s.painter.setPen(s.pencolor)
        s.painter.setBrush(s.brushcolor)

        s.painter.setViewport((wd - side) / 2, (wd - side) / 2, side, side)
        s.painter.setWindow(0, 0, s.LogicalSize, s.LogicalSize)

        # i is index of 16 x 16 matrix
        # actual device index of the cell is s.cellMap[i]
        for i in range(0, s.nCells):
            cell = s.cellMap[i]  # map graphics cell index to cell number
            cellval = s.cellData[cell - 1]

            # High alarm check
            if s.hAlarmEnable and cellval >= s.hAlarm:
                try:
                    s.painter.setBrush(s.HighAlarmColor)  #set hAlarm color
                except Exception as e:
                    s.lg.error("SHWidget alarm Paint exception:%s" % e)
                    s.lg.error("SHWidget Polygon:%d" % (i))
                    s.painter.end()
                    return

            # Low alarm check
            elif s.lAlarmEnable and cellval <= s.lAlarm:
                try:
                    s.painter.setBrush(s.LowAlarmColor)  # set lAlarm color
                except Exception as e:
                    s.lg.error("SHWidget alarm Paint exception:%s" % e)
                    s.lg.error("SHWidget.  Polygon:%d" % (i))
                    s.painter.end()
                    return

            else:
                s.painter.setBrush(s.colormap[s.intData[cell - 1]])
            s.painter.drawRect(s.rects[i])

        if s.paintVectors:
            s.drawVectors()

        #..................................................................
        # Selected Cell
        #..................................................................
        if s.selectedCell is not None:
            if s.blankCells:
                s.blankCells = False
                for i in range(0, s.nCells):
                    s.painter.setBrush(s.colormap[i + s.colorOffset])
                    s.painter.drawRect(s.rects[i])

            s.painter.setPen(QColor('#00FF00'))  # over the cell text
            s.painter.setBrush(QColor('#00FF00'))
            s.painter.drawText(s.selectedCellPoint,
                               QString(" %d" % s.selectedDmCell))

            # Paint Dot and cell number in selected cell
            s.painter.setPen(Qt.black)
            qp = QPointF(s.selectedCellCenter)
            s.painter.drawEllipse(qp, 4.0, 4.0)

            # Paint cell number and value on frame
            s.painter.drawText(
                    QPoint(0, 250),
                    QString("cell %3d: %5.2f" %
                            (s.selectedDmCell,
                             s.cellData[s.selectedDmCell - 1])))

        # Display brightness/contrast values
        s.painter.setPen(Qt.black)
        s.painter.drawText(QPoint(0, 225), QString("b: %5.2f" % (s.brightness)))
        s.painter.drawText(QPoint(0, 235), QString("c: %5.2f" % (s.contrast)))

        # Display TTMode Dot
        s.painter.setPen(Qt.green)
        x = (s.TtModeX * 100) + 100
        y = (s.TtModeY * 100) + 100
        s.painter.drawEllipse(QPointF(x, y), 8.0, 8.0)

        s.painter.end()

    #------------------------------------------------------------------------
    def drawVectors(s):

        s.painter.setPen(QColor('#000000'))
        s.painter.setBrush(QColor('#00FF00'))
        s.painter.setPen(s.linePen)
        #s.painter.setOpacity(0.9)

        s.painter.drawLine(s.arw1qp0, s.arw1qp1)
        s.painter.drawLine(s.arw2qp0, s.arw2qp1)
        s.painter.drawLine(s.arw3qp0, s.arw3qp1)
        s.painter.drawLine(s.arw4qp0, s.arw4qp1)

        #s.painter.drawEllipse(s.qp0, s.qp1)
        dotsize = 2
        s.painter.drawEllipse(s.arw1qp0, dotsize, dotsize)
        s.painter.drawEllipse(s.arw2qp0, dotsize, dotsize)
        s.painter.drawEllipse(s.arw3qp0, dotsize, dotsize)
        s.painter.drawEllipse(s.arw4qp0, dotsize, dotsize)

        #s.painter.setOpacity(1.0)

    #----------------------------------------------------------------------
    def setAlarms(s, lAlarm, lEnable, hAlarm, hEnable):
        #print("<SHWidget>.setAlarms",s.name,lAlarm, lEnable, hAlarm, hEnable)
        s.lAlarm = float(lAlarm)
        s.lAlarmEnable = bool(lEnable)
        s.hAlarm = float(hAlarm)
        s.hAlarmEnable = bool(hEnable)

    #.............................................
    # Raise set-alarms popup
    def setAlarmsPopup(s):
        qp = QWidget.mapToGlobal(s, QPoint(0, 0))  # where to pop up
        s.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def colorSelected(s, color):
        #print("ColorSelected")
        hue = color.hsvHue()
        sat = color.saturation()
        val = color.value()
        #print("Hue:", hue)
        #print("Sat:", sat)
        #print("Val:", val)
        s.set_hsv(s.cmapN, hue, sat, val)
        s.update()  # s.repaint()

    #...........................................................................
    def colorChoice(s, color):
        #print("ColorChoice")
        hue = color.hsvHue()
        sat = color.saturation()
        val = color.value()
        #print("Hue:", color.hsvHue())
        #print("Sat:", color.saturation())
        #print("Val:", color.value())

    #-----------------------------------------------------------------------
    # create polygonlist for 4x4 matrix display
    #
    #   Q2    Q1                   Q2   Q1
    #  0,1  |  4, 5              6,5 | 2, 1
    #  2,3  |  6, 7              8,7 | 4, 3
    #  -----+-------     =      -----+------ (this is actul numbering on device)
    #  8, 9 |  12,13            14,13| 10, 9
    # 10,11 |  14,15            16,15| 12,11
    #   Q4    Q3                  Q4    Q3
    #
    def load_rects(s):
        s.rects = []
        xoff = s.margin
        yoff = s.margin
        sz = s.minSize / 4  # cell size

        # upper left 4x4 array
        s.rects.append(QRectF(0 + xoff, 0 + yoff, sz, sz))
        s.rects.append(QRectF(sz + xoff, 0 + yoff, sz, sz))
        s.rects.append(QRectF(0 + xoff, sz + yoff, sz, sz))
        s.rects.append(QRectF(sz + xoff, sz + yoff, sz, sz))

        # upper right 4x4 array
        s.rects.append(QRectF(2 * sz + xoff, 0 + yoff, sz, sz))
        s.rects.append(QRectF(3 * sz + xoff, 0 + yoff, sz, sz))
        s.rects.append(QRectF(2 * sz + xoff, sz + yoff, sz, sz))
        s.rects.append(QRectF(3 * sz + xoff, sz + yoff, sz, sz))

        # lower left 4x4 array
        s.rects.append(QRectF(0 + xoff, 2 * sz + yoff, sz, sz))
        s.rects.append(QRectF(sz + xoff, 2 * sz + yoff, sz, sz))
        s.rects.append(QRectF(0 + xoff, 3 * sz + yoff, sz, sz))
        s.rects.append(QRectF(sz + xoff, 3 * sz + yoff, sz, sz))

        # lower right 4x4 array
        s.rects.append(QRectF(2 * sz + xoff, 2 * sz + yoff, sz, sz))
        s.rects.append(QRectF(3 * sz + xoff, 2 * sz + yoff, sz, sz))
        s.rects.append(QRectF(2 * sz + xoff, 3 * sz + yoff, sz, sz))
        s.rects.append(QRectF(3 * sz + xoff, 3 * sz + yoff, sz, sz))

    #-----------------------------------------------------------------------
    # Initialize Colormaps
    #  #s.colormaps[s.cmapN][i] = QColor(hue,hue,hue)
    def init_colormaps(s):

        NCOLORCELLS = 255
        NINTENSITIES = 255
        NHSVHUES = 360
        NALPHAS = 255  # transparency. 255 = opaque

        s.colormaps = []  # cmaps list
        s.maxCmaps = 6  # Maximum number of colormaps

        s.cmapN = Kst.GREYCMAP  # set startup colormap

        s.brightness = 0  # -1 to 1
        s.contrast = 0  # -1 to 1
        s.hsv_hue_range = NHSVHUES  # N Hues in hsv color system
        s.hsv_intensity_range = NINTENSITIES  # N intensities in hsv sys
        s.n_colormap_cells = NCOLORCELLS

        # make maxCmaps greyscale colormaps
        # monochrome/greyscale
        s.hsvHue = 0  # hue        =  color;
        s.hsvSat = 0  # saturation =  color density
        s.hsvVal = 0  # value      =  brightness
        s.hsvAph = NALPHAS  # alpha      = transparency
        for i in range(0, s.maxCmaps):
            s.colormaps.append([])
            for j in range(0, s.n_colormap_cells):
                s.colormaps[i].append(
                        QColor.fromHsv(s.hsvHue, s.hsvSat, j, s.hsvAph))

        # make a red, 'Safety' colormap
        Hue = 1  # color hue        =  color;
        Sat = 255  # color saturation =  color density
        Val = 0  # color value      =  brightness
        Aph = 255  # color alpha      = transparency
        colormap = s.colormaps[Kst.SAFETYCMAP]
        ndx = 0
        for val in range(0, s.n_colormap_cells):
            s.colormaps[Kst.SAFETYCMAP][ndx] = \
               QColor.fromHsv( Hue, Sat, val, Aph)
            ndx += 1

        # make a gren monochrome colormap
        # green:  80 - 120
        Hue = 100  # color hue        =  color;
        Sat = 255  # color saturation =  color density
        Val = 0  # color value      =  brightness
        Aph = 255  # color alpha      = transparency
        s.colormap = s.colormaps[Kst.GREENCMAP]
        ndx = 0
        for val in range(0, s.n_colormap_cells):
            s.colormaps[Kst.GREENCMAP][ndx] = \
               QColor.fromHsv( Hue, Sat, val, Aph)
            ndx += 1

        s.colormap = s.colormaps[s.cmapN]

    #-----------------------------------------------------------------------
    def set_colormap(s, cmapN):
        s.cmapN = cmapN
        s.colormap = s.colormaps[cmapN]
        s.update()  # s.repaint()

    #-----------------------------------------------------------------------
    def set_hsv(s, cmapN, hue, sat, val):
        s.colormap = s.colormaps[cmapN]
        alpha = 255  # transparency
        for i in range(0, s.n_colormap_cells):
            s.colormap[i] = QColor.fromHsv(hue, i, 255, alpha)

    #----------------------------------------------------------------------
    #    brigthness = -1 to 1
    #    contrast   = -1 to 1
    def set_contrast(s, contrast):
        s.contrast = contrast

    #----------------------------------------------------------------------
    def set_brigthness(s, brightness):
        s.brigthness = brigthness

    #-----------------------------------------------------------------------
    def set_normalization_constants(s):

        s.cellDataRange = s.cellDataMax - s.cellDataMin  # point to data

        if s.cellDataRange <= 0:
            s.cellDataRange = 1

        s.cellDataK = s.hsv_intensity_range / s.cellDataRange

        if s.cfg.debug == 8:
            print("cellDataK    : ", s.name, s.cellDataK)
            print("cellDataRange: ", s.name, s.cellDataRange)

    #-----------------------------------------------------------------------
    def scale_and_contrast(s):

        s.set_normalization_constants()

        s.cellSCData = s.cellData * s.cellDataK

        # Brightness
        if s.brightness < 0.0:
            s.cellSCData *= (1.0 + s.brightness)
        else:
            s.cellSCData = s.cellSCData + ((1 - s.cellSCData) * s.brightness)

        # Contrast
        s.cellSCData = (s.cellSCData - 0.5) * (tan(
                (s.contrast + 1) * pi / 4)) + 0.5
        s.cellSCData /= s.cellDataK

        if s.cfg.debug == 8: print(s.name, "SCdata 2:\n", s.cellSCData)

        # convert to range within hsv_intensity_range
        s.cellSCData = (s.cellSCData - s.cellDataMin)
        s.intData = s.cellSCData * s.cellDataK  # 0 based
        s.intData = s.intData.astype(int).clip(min=0, max=254)

    #-----------------------------------------------------------------------
    def data_ready(s, data):
        s.cellData = data[Kst.SH_CELLDATASTART:Kst.SH_CELLDATAEND].copy()
        if s.cfg.debug > Kst.DBGLEVEL_RATE1:
            print("SHwidget data_ready", s.cellData)

        gendata = data[Kst.GENDATASTART:Kst.GENDATAEND]
        s.frameN = gendata[Kst.FRAME_NUMBER]
        s.cellDataMin = gendata[Kst.LWF_DATAMIN]  # cellData.min()
        s.cellDataMax = gendata[Kst.LWF_DATAMAX]  # cellData.max()
        s.cellDataVar = gendata[Kst.LWF_DATAVAR]  # cellData.var()
        s.cellDataAvg = gendata[Kst.LWF_COUNTAVG]  # cellData average
        #
        s.scale_and_contrast()

        #
        if not s.frameN % s.cfg.framesPerSHArrow:

            # 4 vectors for display
            s.setVectors(gendata)

            # dot for display
            s.TtModeX = gendata[Kst.LWF_TTMODEX]  # plotDotX
            s.TtModeY = gendata[Kst.LWF_TTMODEY]  # plotDotY

        s.update()  # s.repaint()

    #-----------------------------------------------------------------------
    # Set endpoints of four vectors for display
    def setVectors(s, genData):

        k = 50  # magnitude constant multiplier
        x1 = genData[Kst.SH_Q1TTMODEX]
        y1 = genData[Kst.SH_Q1TTMODEY]

        x2 = genData[Kst.SH_Q2TTMODEX]
        y2 = genData[Kst.SH_Q2TTMODEY]

        x3 = genData[Kst.SH_Q3TTMODEX]
        y3 = genData[Kst.SH_Q3TTMODEY]

        x4 = genData[Kst.SH_Q4TTMODEX]
        y4 = genData[Kst.SH_Q4TTMODEY]

        s.arw1qp1.setX(x1 * k + s.xoff1)
        s.arw1qp1.setY(y1 * k + s.yoff1)

        s.arw2qp1.setX(x2 * k + s.xoff2)
        s.arw2qp1.setY(y2 * k + s.yoff2)

        s.arw3qp1.setX(x3 * k + s.xoff3)
        s.arw3qp1.setY(y3 * k + s.yoff3)

        s.arw4qp1.setX(x4 * k + s.xoff4)
        s.arw4qp1.setY(y4 * k + s.yoff4)
        s.paintVectors = True

        #print(x1,y1, x2,y2, x3,y3, x4,y4, )

    #-----------------------------------------------------------------------
    def zeroContrastAndBrightness(s):
        s.contrast = 0
        s.brightness = 0

    #-----------------------------------------------------------------------
    def mouseDoubleClickEvent(s, ev):
        button = ev.button()
        if button == LMB:
            ev.accept()
            x = ev.posF().x()
            y = ev.posF().y()
            ratio = s.LogicalSize / s.width()
            x1 = x * ratio
            y1 = y * ratio
            s.mouseOverCell(x1, y1)

        #elif button == MMB:
        #   s.zeroContrastAndBrightness()
        #elif button == RMB:

    #-----------------------------------------------------------------------
    def mouseReleaseEvent(s, ev):
        button = ev.button()

        #if button == LMB:
        #

        if button == MMB:
            ev.accept()
            s.zeroContrastAndBrightness()

        elif button == RMB:
            ev.accept()
            s.setAlarmsPopup()

        #print("ratio,wd:", ratio,s.width())
        #print("Global Pos:", ev.globalPos())  #screen position
        #print("Pos       :", ev.pos())        # relative to widget
        #print("PosF      :", ev.posF())
        #print("Pos       :", x,y)
        #print("PosF      :", x,y)

    #----------------------------------------------------------------------
    # On mouse drage, set brightness & contrast -1 to 1
    # Contrast   is vertical axis
    # Brightness is horizontal axis
    def mouseMoveEvent(s, ev):
        kw = s.width() / 2
        kh = s.height() / 2

        s.contrast = (ev.x() - kw) / kw * s.contrastK
        s.brightness = (kw - ev.y()) / kw * s.brightnessK

        if s.contrast >= 1.0:
            s.contrast = 1.0
        if s.contrast <= -1.0:
            s.contrast = -1.0

        if s.brightness >= 1.0:
            s.brightness = 1.0

        if s.brightness <= -1.0:
            s.brightness = -1.0

        ev.accept()

    #----------------------------------------------------------------------
    def mouseOverCell(s, mx, my):
        qp = QPointF(int(mx + 0.5), int(my + 0.5))  # qp = x,y of mouse click
        for cell in range(s.nCells):
            # if cell contains mouseclick point,
            #   o Remember selected-cell number
            #   o repaint

            currently_selected = s.selectedCell
            if s.rects[cell].contains(qp):
                s.selectedCell = cell  #gui rectangle index
                s.selectedDmCell = s.cellMap[cell]  #actual cell-number
                s.selectedCellPoint = qp
                s.blankCells = False
                s.selectedCellCenter = s.rects[cell].center()
                if currently_selected == s.selectedCell:
                    s.selectedCell = None

                #s.update() # s.repaint()
                s.repaint()  # s.repaint()
                break

    #----------------------------------------------------------------------

    #s.painter.setPen(QColor('#000000')) # text color
