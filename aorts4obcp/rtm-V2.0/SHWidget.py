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
from __future__ import absolute_import, print_function, division

from PyQt4.QtCore import (
        Qt,
        QPoint,
        QPointF,
        QRectF,
        QSize,
)
from PyQt4.QtGui import (QColor, QPainter, QWidget, QSizePolicy, QPen)

import math

import numpy as np
import Configuration
import Constants as Kst
#import rotationArrow
#import rotatePixmap

# Mouse buttons
LMB = 1
MMB = 4
RMB = 2


#------------------------------------------------------------------------------
# LensletWidget
#------------------------------------------------------------------------------
class SHWidget(QWidget):

    #.......................................................................
    def __init__(self, parent=None):
        super(SHWidget, self).__init__(parent)

        self.cfg = Configuration.cfg
        if self.cfg.debug: print("<SHWidget.__init__>")
        self.name = "SHwdg"
        self.alarmDlg = None  # to be set by instantiater
        self.minSize = 200
        self.margin = 4
        self.LogicalSize = self.minSize + self.margin
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #------------------------------------------------------------------
        # TTMODE Vectors : 4 rotation vectors for display as variable length
        # lines from 4 centers of rotation
        # see TTMODEX, TTMODEY data
        #

        offset = 50 + self.margin
        k2 = 2 * self.margin
        self.xoff1 = offset
        self.yoff1 = offset

        self.xoff2 = offset * 3 - k2
        self.yoff2 = offset

        self.xoff3 = offset
        self.yoff3 = offset * 3 - k2

        self.xoff4 = offset * 3 - k2
        self.yoff4 = offset * 3 - k2

        self.arw1qp0 = QPointF(float(self.xoff1),
                               float(self.yoff1))  #rotation base
        self.arw1qp1 = QPointF(float(self.xoff1),
                               float(self.yoff1))  #tip @ zero len @startup

        self.arw2qp0 = QPointF(float(self.xoff2), float(self.yoff2))
        self.arw2qp1 = QPointF(float(self.xoff2), float(self.yoff2))

        self.arw3qp0 = QPointF(float(self.xoff3), float(self.yoff3))
        self.arw3qp1 = QPointF(float(self.xoff3), float(self.yoff3))

        self.arw4qp0 = QPointF(float(self.xoff4), float(self.yoff4))
        self.arw4qp1 = QPointF(float(self.xoff4), float(self.yoff4))

        self.linePen = QPen()  # pen for vector linedraw
        self.linePen.setColor(Qt.green)
        self.linePen.setCapStyle(Qt.RoundCap)
        self.linePen.setWidth(3)
        self.paintVectors = True  # these will be four dots at startup

        #.......................................................................
        self.load_rects()
        self.nCells = 16  # number of shack-hartmann cells in 4x4 array
        self.mousepoint = QPoint(0, 0)
        self.contrastK = 1
        self.brightnessK = 1
        self.datacount = 0

        self.firstdata = True
        self.mins = np.zeros(600, dtype=float)
        self.maxs = np.zeros(600, dtype=float)
        self.vars = np.zeros(600, dtype=float)

        self.hAlarm = 0
        self.lAlarm = 0
        self.lAlarmEnable = False
        self.hAlarmEnable = False

        self.HighAlarmColor = QColor(Kst.CELLALARMRED)  # color of high alarm
        self.LowAlarmColor = QColor(Kst.CELLALARMYLW)  # color of low alarm

        #.......................................................................
        self.constantMin = Kst.SHMIN
        self.constantMax = Kst.SHMAX
        self.init_colormaps()
        #s.set_normalization_constants()

        self.frameN = 0  # Dataframe number sent with data
        self.frameCount = 0  # Our private data-frame counter
        self.cellData = np.zeros((self.nCells), dtype=float)
        self.cellSCData = np.zeros((self.nCells), dtype=float)
        self.intData = np.zeros((self.nCells), dtype=int)

        # bump intensity toward high end of color scale
        self.colorOffset = 100
        for i in range(0, self.nCells):
            self.intData[i] = i + self.colorOffset

        self.cellDataMin = None
        self.cellDataMax = None
        self.cellDataVar = None
        self.cellDataAvg = None

        self.TtModeX = 0  # plotDotX
        self.TtModeY = 0  # plotDotY
        self.pdk = float(300)
        self.tmpData = np.zeros((self.nCells), dtype=float)
        self.stats = np.zeros((600), dtype=float)  # 60sec * 10Hz
        #.......................................................................
        self.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        self.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        self.wheelIncr = 120  # probable delta from wheel event=ev.delta
        #.......................................................................
        self.painter = QPainter()
        self.paintcount = 0
        #s.ppath        = QPainterPath()
        self.pencolor = Qt.black
        self.brushcolor = Qt.green
        self.selectedCell = None
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
        self.cellMap = (6, 5, 8, 7, 2, 1, 4, 3, 14, 13, 16, 15, 10, 9, 12, 11)

    #...........................................................................
    def heightForWidth(self, w):
        #print("<SHWidget>.heightForWidth>",w)
        return (w)

    #...........................................................................
    def sizeHint(self):
        return QSize(self.minSize, self.minSize)

    #...........................................................................
    def minimumSizeHint(self):
        return QSize(self.minSize, self.minSize)

    #...........................................................................
    def resizeEvent(self, ev):
        pass

    #...........................................................................
    def paintEvent(self, ev):
        self.paint()
        ev.accept()

    #-----------------------------------------------------------------------
    def paint(self):
        wd = self.width()
        ht = self.height() * 0.8
        side = min(wd, ht)
        self.painter.begin(self)
        self.painter.setPen(self.pencolor)
        self.painter.setBrush(self.brushcolor)

        self.painter.setViewport((wd - side) / 2, (wd - side) / 2, side, side)
        self.painter.setWindow(0, 0, self.LogicalSize, self.LogicalSize)

        # i is index of 16 x 16 matrix
        # actual device index of the cell is s.cellMap[i]
        for i in range(0, self.nCells):
            cell = self.cellMap[i]  # map graphics cell index to cell number
            cellval = self.cellData[cell - 1]

            # High alarm check
            if self.hAlarmEnable and cellval >= self.hAlarm:
                try:
                    self.painter.setBrush(
                            self.HighAlarmColor)  #set hAlarm color
                except Exception as e:
                    self.lg.error("SHWidget alarm Paint exception:%s" % e)
                    self.lg.error("SHWidget Polygon:%d" % (i))
                    self.painter.end()
                    return

            # Low alarm check
            elif self.lAlarmEnable and cellval <= self.lAlarm:
                try:
                    self.painter.setBrush(
                            self.LowAlarmColor)  # set lAlarm color
                except Exception as e:
                    self.lg.error("SHWidget alarm Paint exception:%s" % e)
                    self.lg.error("SHWidget.  Polygon:%d" % (i))
                    self.painter.end()
                    return

            else:
                self.painter.setBrush(self.colormap[self.intData[cell - 1]])
            self.painter.drawRect(self.rects[i])

        if self.paintVectors:
            self.drawVectors()

        #..................................................................
        # Selected Cell
        #..................................................................
        if self.selectedCell is not None:
            if self.blankCells:
                self.blankCells = False
                for i in range(0, self.nCells):
                    self.painter.setBrush(self.colormap[i + self.colorOffset])
                    self.painter.drawRect(self.rects[i])

            self.painter.setPen(QColor('#00FF00'))  # over the cell text
            self.painter.setBrush(QColor('#00FF00'))
            self.painter.drawText(self.selectedCellPoint,
                                  " %d" % self.selectedDmCell)

            # Paint Dot and cell number in selected cell
            self.painter.setPen(Qt.black)
            qp = QPointF(self.selectedCellCenter)
            self.painter.drawEllipse(qp, 4.0, 4.0)

            # Paint cell number and value on frame
            self.painter.drawText(
                    QPoint(0, 250), "cell %3d: %5.2f" %
                    (self.selectedDmCell,
                     self.cellData[self.selectedDmCell - 1]))

        # Display brightness/contrast values
        self.painter.setPen(Qt.black)
        self.painter.drawText(QPoint(0, 225), "b: %5.2f" % (self.brightness))
        self.painter.drawText(QPoint(0, 235), "c: %5.2f" % (self.contrast))

        # Display TTMode Dot
        self.painter.setPen(Qt.green)
        x = (self.TtModeX * 100) + 100
        y = (self.TtModeY * 100) + 100
        self.painter.drawEllipse(QPointF(x, y), 8.0, 8.0)

        self.painter.end()

    #------------------------------------------------------------------------
    def drawVectors(self):

        self.painter.setPen(QColor('#000000'))
        self.painter.setBrush(QColor('#00FF00'))
        self.painter.setPen(self.linePen)
        #s.painter.setOpacity(0.9)

        self.painter.drawLine(self.arw1qp0, self.arw1qp1)
        self.painter.drawLine(self.arw2qp0, self.arw2qp1)
        self.painter.drawLine(self.arw3qp0, self.arw3qp1)
        self.painter.drawLine(self.arw4qp0, self.arw4qp1)

        #s.painter.drawEllipse(s.qp0, s.qp1)
        dotsize = 2
        self.painter.drawEllipse(self.arw1qp0, dotsize, dotsize)
        self.painter.drawEllipse(self.arw2qp0, dotsize, dotsize)
        self.painter.drawEllipse(self.arw3qp0, dotsize, dotsize)
        self.painter.drawEllipse(self.arw4qp0, dotsize, dotsize)

        #s.painter.setOpacity(1.0)

    #----------------------------------------------------------------------
    def setAlarms(self, lAlarm, lEnable, hAlarm, hEnable):
        #print("<SHWidget>.setAlarms",s.name,lAlarm, lEnable, hAlarm, hEnable)
        self.lAlarm = float(lAlarm)
        self.lAlarmEnable = bool(lEnable)
        self.hAlarm = float(hAlarm)
        self.hAlarmEnable = bool(hEnable)

    #.............................................
    # Raise set-alarms popup
    def setAlarmsPopup(self):
        qp = QWidget.mapToGlobal(self, QPoint(0, 0))  # where to pop up
        self.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def colorSelected(self, color):
        #print("ColorSelected")
        hue = color.hsvHue()
        sat = color.saturation()
        val = color.value()
        #print("Hue:", hue)
        #print("Sat:", sat)
        #print("Val:", val)
        self.set_hsv(self.cmapN, hue, sat, val)
        self.update()  # s.repaint()

    #...........................................................................
    def colorChoice(self, color):
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
    def load_rects(self):
        self.rects = []
        xoff = self.margin
        yoff = self.margin
        sz = self.minSize / 4  # cell size

        # upper left 4x4 array
        self.rects.append(QRectF(0 + xoff, 0 + yoff, sz, sz))
        self.rects.append(QRectF(sz + xoff, 0 + yoff, sz, sz))
        self.rects.append(QRectF(0 + xoff, sz + yoff, sz, sz))
        self.rects.append(QRectF(sz + xoff, sz + yoff, sz, sz))

        # upper right 4x4 array
        self.rects.append(QRectF(2 * sz + xoff, 0 + yoff, sz, sz))
        self.rects.append(QRectF(3 * sz + xoff, 0 + yoff, sz, sz))
        self.rects.append(QRectF(2 * sz + xoff, sz + yoff, sz, sz))
        self.rects.append(QRectF(3 * sz + xoff, sz + yoff, sz, sz))

        # lower left 4x4 array
        self.rects.append(QRectF(0 + xoff, 2 * sz + yoff, sz, sz))
        self.rects.append(QRectF(sz + xoff, 2 * sz + yoff, sz, sz))
        self.rects.append(QRectF(0 + xoff, 3 * sz + yoff, sz, sz))
        self.rects.append(QRectF(sz + xoff, 3 * sz + yoff, sz, sz))

        # lower right 4x4 array
        self.rects.append(QRectF(2 * sz + xoff, 2 * sz + yoff, sz, sz))
        self.rects.append(QRectF(3 * sz + xoff, 2 * sz + yoff, sz, sz))
        self.rects.append(QRectF(2 * sz + xoff, 3 * sz + yoff, sz, sz))
        self.rects.append(QRectF(3 * sz + xoff, 3 * sz + yoff, sz, sz))

    #-----------------------------------------------------------------------
    # Initialize Colormaps
    #  #s.colormaps[s.cmapN][i] = QColor(hue,hue,hue)
    def init_colormaps(self):

        NCOLORCELLS = 255
        NINTENSITIES = 255
        NHSVHUES = 360
        NALPHAS = 255  # transparency. 255 = opaque

        self.colormaps = []  # cmaps list
        self.maxCmaps = 6  # Maximum number of colormaps

        self.cmapN = Kst.GREYCMAP  # set startup colormap

        self.brightness = 0  # -1 to 1
        self.contrast = 0  # -1 to 1
        self.hsv_hue_range = NHSVHUES  # N Hues in hsv color system
        self.hsv_intensity_range = NINTENSITIES  # N intensities in hsv sys
        self.n_colormap_cells = NCOLORCELLS

        # make maxCmaps greyscale colormaps
        # monochrome/greyscale
        self.hsvHue = 0  # hue        =  color;
        self.hsvSat = 0  # saturation =  color density
        self.hsvVal = 0  # value      =  brightness
        self.hsvAph = NALPHAS  # alpha      = transparency
        for i in range(0, self.maxCmaps):
            self.colormaps.append([])
            for j in range(0, self.n_colormap_cells):
                self.colormaps[i].append(
                        QColor.fromHsv(self.hsvHue, self.hsvSat, j,
                                       self.hsvAph))

        # make a red, 'Safety' colormap
        Hue = 1  # color hue        =  color;
        Sat = 255  # color saturation =  color density
        Val = 0  # color value      =  brightness
        Aph = 255  # color alpha      = transparency
        colormap = self.colormaps[Kst.SAFETYCMAP]
        ndx = 0
        for val in range(0, self.n_colormap_cells):
            self.colormaps[Kst.SAFETYCMAP][ndx] = \
               QColor.fromHsv( Hue, Sat, val, Aph)
            ndx += 1

        # make a gren monochrome colormap
        # green:  80 - 120
        Hue = 100  # color hue        =  color;
        Sat = 255  # color saturation =  color density
        Val = 0  # color value      =  brightness
        Aph = 255  # color alpha      = transparency
        self.colormap = self.colormaps[Kst.GREENCMAP]
        ndx = 0
        for val in range(0, self.n_colormap_cells):
            self.colormaps[Kst.GREENCMAP][ndx] = \
               QColor.fromHsv( Hue, Sat, val, Aph)
            ndx += 1

        self.colormap = self.colormaps[self.cmapN]

    #-----------------------------------------------------------------------
    def set_colormap(self, cmapN):
        self.cmapN = cmapN
        self.colormap = self.colormaps[cmapN]
        self.update()  # s.repaint()

    #-----------------------------------------------------------------------
    def set_hsv(self, cmapN, hue, sat, val):
        self.colormap = self.colormaps[cmapN]
        alpha = 255  # transparency
        for i in range(0, self.n_colormap_cells):
            self.colormap[i] = QColor.fromHsv(hue, i, 255, alpha)

    #----------------------------------------------------------------------
    #    brigthness = -1 to 1
    #    contrast   = -1 to 1
    def set_contrast(self, contrast):
        self.contrast = contrast

    #----------------------------------------------------------------------
    def set_brigthness(self, brightness):
        self.brigthness = brightness

    #-----------------------------------------------------------------------
    def set_normalization_constants(self):

        self.cellDataRange = self.cellDataMax - self.cellDataMin  # point to data

        if self.cellDataRange <= 0:
            self.cellDataRange = 1

        self.cellDataK = self.hsv_intensity_range / self.cellDataRange

        if self.cfg.debug == 8:
            print("cellDataK    : ", self.name, self.cellDataK)
            print("cellDataRange: ", self.name, self.cellDataRange)

    #-----------------------------------------------------------------------
    def scale_and_contrast(self):

        self.set_normalization_constants()

        self.cellSCData = self.cellData * self.cellDataK

        # Brightness
        if self.brightness < 0.0:
            self.cellSCData *= (1.0 + self.brightness)
        else:
            self.cellSCData = self.cellSCData + (
                    (1 - self.cellSCData) * self.brightness)

        # Contrast
        self.cellSCData = (self.cellSCData - 0.5) * (math.tan(
                (self.contrast + 1) * math.pi / 4)) + 0.5
        self.cellSCData /= self.cellDataK

        if self.cfg.debug == 8: print(self.name, "SCdata 2:\n", self.cellSCData)

        # convert to range within hsv_intensity_range
        self.cellSCData = (self.cellSCData - self.cellDataMin)
        self.intData = self.cellSCData * self.cellDataK  # 0 based
        self.intData = self.intData.astype(int).clip(min=0, max=254)

    #-----------------------------------------------------------------------
    def data_ready(self, data):
        self.cellData = data[Kst.SH_CELLDATASTART:Kst.SH_CELLDATAEND].copy()
        if self.cfg.debug > Kst.DBGLEVEL_RATE1:
            print("SHwidget data_ready", self.cellData)

        gendata = data[Kst.GENDATASTART:Kst.GENDATAEND]
        self.frameN = gendata[Kst.FRAME_NUMBER]
        self.cellDataMin = gendata[Kst.LWF_DATAMIN]  # cellData.min()
        self.cellDataMax = gendata[Kst.LWF_DATAMAX]  # cellData.max()
        self.cellDataVar = gendata[Kst.LWF_DATAVAR]  # cellData.var()
        self.cellDataAvg = gendata[Kst.LWF_COUNTAVG]  # cellData average
        #
        self.scale_and_contrast()

        #
        if not self.frameN % self.cfg.framesPerSHArrow:

            # 4 vectors for display
            self.setVectors(gendata)

            # dot for display
            self.TtModeX = gendata[Kst.LWF_TTMODEX]  # plotDotX
            self.TtModeY = gendata[Kst.LWF_TTMODEY]  # plotDotY

        self.update()  # s.repaint()

    #-----------------------------------------------------------------------
    # Set endpoints of four vectors for display
    def setVectors(self, genData):

        k = 50  # magnitude constant multiplier
        x1 = genData[Kst.SH_Q1TTMODEX]
        y1 = genData[Kst.SH_Q1TTMODEY]

        x2 = genData[Kst.SH_Q2TTMODEX]
        y2 = genData[Kst.SH_Q2TTMODEY]

        x3 = genData[Kst.SH_Q3TTMODEX]
        y3 = genData[Kst.SH_Q3TTMODEY]

        x4 = genData[Kst.SH_Q4TTMODEX]
        y4 = genData[Kst.SH_Q4TTMODEY]

        self.arw1qp1.setX(x1 * k + self.xoff1)
        self.arw1qp1.setY(y1 * k + self.yoff1)

        self.arw2qp1.setX(x2 * k + self.xoff2)
        self.arw2qp1.setY(y2 * k + self.yoff2)

        self.arw3qp1.setX(x3 * k + self.xoff3)
        self.arw3qp1.setY(y3 * k + self.yoff3)

        self.arw4qp1.setX(x4 * k + self.xoff4)
        self.arw4qp1.setY(y4 * k + self.yoff4)
        self.paintVectors = True

        #print(x1,y1, x2,y2, x3,y3, x4,y4, )

    #-----------------------------------------------------------------------
    def zeroContrastAndBrightness(self):
        self.contrast = 0
        self.brightness = 0

    #-----------------------------------------------------------------------
    def mouseDoubleClickEvent(self, ev):
        button = ev.button()
        if button == LMB:
            ev.accept()
            x = ev.posF().x()
            y = ev.posF().y()
            ratio = self.LogicalSize / self.width()
            x1 = x * ratio
            y1 = y * ratio
            self.mouseOverCell(x1, y1)

        #elif button == MMB:
        #   s.zeroContrastAndBrightness()
        #elif button == RMB:

    #-----------------------------------------------------------------------
    def mouseReleaseEvent(self, ev):
        button = ev.button()

        #if button == LMB:
        #

        if button == MMB:
            ev.accept()
            self.zeroContrastAndBrightness()

        elif button == RMB:
            ev.accept()
            self.setAlarmsPopup()

    #----------------------------------------------------------------------
    # On mouse drage, set brightness & contrast -1 to 1
    # Contrast   is vertical axis
    # Brightness is horizontal axis
    def mouseMoveEvent(self, ev):
        kw = self.width() / 2
        kh = self.height() / 2

        self.contrast = (ev.x() - kw) / kw * self.contrastK
        self.brightness = (kw - ev.y()) / kw * self.brightnessK

        if self.contrast >= 1.0:
            self.contrast = 1.0
        if self.contrast <= -1.0:
            self.contrast = -1.0

        if self.brightness >= 1.0:
            self.brightness = 1.0

        if self.brightness <= -1.0:
            self.brightness = -1.0

        ev.accept()

    #----------------------------------------------------------------------
    def mouseOverCell(self, mx, my):
        qp = QPointF(int(mx + 0.5), int(my + 0.5))  # qp = x,y of mouse click
        for cell in range(self.nCells):
            # if cell contains mouseclick point,
            #   o Remember selected-cell number
            #   o repaint

            currently_selected = self.selectedCell
            if self.rects[cell].contains(qp):
                self.selectedCell = cell  #gui rectangle index
                self.selectedDmCell = self.cellMap[cell]  #actual cell-number
                self.selectedCellPoint = qp
                self.blankCells = False
                self.selectedCellCenter = self.rects[cell].center()
                if currently_selected == self.selectedCell:
                    self.selectedCell = None

                #s.update() # s.repaint()
                self.repaint()  # s.repaint()
                break
