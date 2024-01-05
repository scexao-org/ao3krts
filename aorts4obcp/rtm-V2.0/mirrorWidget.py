#===============================================================================
# File : mirrorWidget.py
#      : Offers class 'mirrorWidget'. A painted polygon map modelling
#        Subaru adaptive optics deformable mirror,
#
# Notes:
# o if cfg.debug == 8: dump various buffers
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

from PyQt5.QtCore import Qt, QPointF, QPoint, QSize

from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QSizePolicy

from math import *
import numpy as np
#import mirrorWidget_loader as loader
import loadPolygons as loader
import cmdLineOptions as opts
import configuration
import constants as Kst
import mirrorCellMap as cellMap  # map of device cells to display cells

# Mouse buttons
LMB = 1
MMB = 4
RMB = 2


#------------------------------------------------------------------------------
# mirrorWidget
#------------------------------------------------------------------------------
class mirrorWidget(QWidget):

    #.......................................................................
    def __init__(self, name="noname", parent=None, flags=Qt.WindowFlags()):
        super(mirrorWidget, self).__init__(parent)

        self.cfg = configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<mirrorWidget.__init__>:", name)
        self.name = name
        self.alarmDlg = None  # to be set by instantiater

        # read mirror polygons. Subtract 30 from coords for each vertex
        self.poly = loader.mirrorWidget_loader(pfactor=-30)

        # dump polygon list to stdout if debug greater than five
        if self.cfg.debug > 5:
            self.poly.prnPolygons()

        self.minSize = 244
        self.marginSize = 6
        self.logicalSize = self.minSize + self.marginSize
        self.marginSize = 0
        self.scaleX = 0.4
        self.scaleY = 0.4
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #.......................................................................
        self.xlate_x = self.xlate_y = 0  # mirror x/y translation
        self.n_mrr_cells = Kst.NMRRCELLS  # Number of mirror cells
        self.polygons = []
        self.mousepoint = QPoint(0, 0)
        self.contrast = 0
        self.brightness = 0
        #s.contrastK       = 2
        #s.brightnessK     = 2

        self.contrastK = 1.2  #  mouse delta to contrast constant
        self.brightnessK = 1.2  #  mouse delta to brightness constant

        self.firstdata = True
        self.constantMin = None  # set once by instantiator
        self.constantMax = None  # set once by instantiator
        self.cellDataMin = 0  # sent with each dataframe
        self.cellDataMax = 0  # sent with each dataframe
        self.mins = np.zeros(600, dtype=float)
        self.maxs = np.zeros(600, dtype=float)
        self.vars = np.zeros(600, dtype=float)

        #.......................................................................
        self.init_colormaps()

        #s.set_normalization_constants(0, 1880)# set dataMin,dataMax,dataRange
        self.frameCount = 0  # Our private data-frame counter

        # cellData   is raw mirror-data per dataFrame
        # cellSCData is fiddled data for display
        # intData    is cell-data scaled to colormap indexes
        self.cellData = np.zeros((self.n_mrr_cells + 1), dtype=float)
        self.cellSCData = np.zeros((self.n_mrr_cells), dtype=float)
        self.intData = np.zeros((self.n_mrr_cells), dtype=int)

        # Create artificial celldata for cell paint at startup.
        # Bump intensity toward high end of color scale.
        for i in range(0, self.n_mrr_cells):
            self.intData[i] = i + 255 - self.n_mrr_cells

        # Because there is more than 1 mirror display (DM,CRV,APD),
        # offsets into commonRTData are set by the frame displaying
        # this widget
        self.ndxMin = None
        self.ndxMax = None
        self.ndxVar = None
        self.ndxAvg = None
        self.ndxDataStart = None
        self.ndxDataEnd = None

        self.hAlarm = 0
        self.lAlarm = 0
        self.lAlarmEnable = False
        self.hAlarmEnable = False

        self.HighAlarmColor = QColor(Kst.CELLALARMRED)  # color of high alarm
        self.LowAlarmColor = QColor(Kst.CELLALARMYLW)  # color of low alarm

        #.......................................................................
        self.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        self.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        self.wheelIncr = 120  # probable delta from wheel event=ev.delta
        #.......................................................................
        self.painter = QPainter()
        self.ppath = QPainterPath()

        self.pencolor = Qt.black
        self.brushcolor = Qt.green
        self.paintcount = 0
        #.......................................................................
        self.polygons = self.poly.polygons  # read mirror polygons from config file

        self.firstPlot = 1

        # add polygon to paint-path for paint-path painting
        # s.ppath.addPolygon(QPolygonF(QPolygon(points_array)))

        #.......................................................................
        self.cell = 0
        self.timerId = None
        self.selectedCell = None  # no cell selected to show
        self.selectedGuiCell = None
        self.blankCells = False
        self.safetyMode = False

        self.setWhatsThis(
                "LeftClick&Drag to set Contrast & Brightness. Double left click to select/unselect cell."
        )

        # set normal cellmap (i.e. non-inverted) for natural-guide-star mode
        self.cellMapState = Kst.NGS_MATRIX
        self.cellMap = cellMap.normalCellMap

    #...........................................................................
    def paintEvent(self, ev):
        self.paint()
        ev.accept()

    #...........................................................................
    # Paint
    # s.painter.scale(s.scale_x,s.scale_y)
    #...........................................................................
    def paint(self):
        wd = self.width()
        ht = self.height()
        self.side = min(wd, ht)

        # Paint
        try:
            self.painter.begin(self)
        except Exception as e:
            self.lg.error("Mrr paint exception #1:", e)
            self.painter.end(self)
            return

        self.painter.setPen(self.pencolor)
        self.painter.setBrush(self.brushcolor)
        self.painter.setViewport(0, 0, self.side, self.side)
        self.painter.setWindow(0, 0, self.logicalSize, self.logicalSize)

        # paint polygons
        # 'i' is index to polygon list
        for i in range(0, self.n_mrr_cells):

            # translate polygon index to actual mirrorcell number
            # Cellmap is normal for Natural Guide Star (NGS)
            # or inverted for Laser Guide Star (LGS)
            cell = self.cellMap[i]

            # set value for this cell from zero-based celldata array
            cellval = self.cellData[cell - 1]

            # High alarm check
            if self.hAlarmEnable and cellval >= self.hAlarm:
                try:
                    self.painter.setBrush(
                            self.HighAlarmColor)  #set hAlarm color
                except Exception as e:
                    self.lg.error("Mirror alarm Paint exception:%s" % e)
                    self.lg.error("%s MirroWidget.  Polygon:%d" %
                                  (self.name, i))
                    self.painter.end()
                    return

            # Low alarm check
            elif self.lAlarmEnable and cellval <= self.lAlarm:
                try:
                    self.painter.setBrush(
                            self.LowAlarmColor)  # set lAlarm color
                except Exception as e:
                    self.lg.error("Mirror alarm Paint exception:%s" % e)
                    self.lg.error("%s MirroWidget.  Polygon:%d" %
                                  (self.name, i))
                    self.painter.end()
                    return

            # No alarms. set cell-color from normal colormap
            else:
                try:
                    self.painter.setBrush(self.colormap[self.intData[cell - 1]])
                except Exception as e:
                    self.lg.error("Mirror paint exception #2:%s. Cell:%d" %
                                  (e, cell))
                    self.lg.error("%s MirroWidget.  Polygon:%d" %
                                  (self.name, i))
                    self.painter.end()
                    return

            # paint the cell
            self.painter.drawPolygon(self.polygons[i])

        # Indicate selected-cell

        if self.selectedCell is not None:
            if self.blankCells:
                self.blankCells = False
                colormap = self.colormaps[self.graduatedCmap]
                for i in range(0, self.n_mrr_cells):
                    self.painter.setBrush(colormap[i])
                    self.painter.drawPolygon(self.polygons[i])

            self.cellRect = self.polygons[self.selectedCell].boundingRect()
            self.painter.setPen(QColor('#00FF00'))  # over the cell text
            self.painter.setBrush(QColor('#00FF00'))
            self.painter.drawText(self.selectedCellPoint,
                                  " %d" % self.selectedGuiCell)

            # print cell number and value on frame
            self.painter.drawEllipse(QPointF(self.cellRect.center()), 4.0, 4.0)
            self.painter.setPen(QColor('#000000'))  # text color
            self.painter.drawText(
                    QPoint(0, 250), "cell %3d: %8.2f" %
                    (self.selectedGuiCell,
                     self.cellData[self.selectedGuiCell - 1]))

        if self.safetyMode:
            self.painter.drawText(QPoint(0, 20), "SAFETY")

        # Brightness & Contrast
        #s.painter.drawText(QPoint(0,225),QString("b:%.2f\nc:%.2f"%(s.brightness,s.contrast)))

        # Display brightness and contrast
        self.painter.drawText(QPoint(0, 225), "b: %5.2f" % (self.brightness))
        self.painter.drawText(QPoint(0, 235), "c: %5.2f" % (self.contrast))

        self.painter.end()

    #----------------------------------------------------------------------
    def setAlarms(self, lAlarm, lEnable, hAlarm, hEnable):
        #print("<mirrorWidget>.setAlarms", s.name, lAlarm, lEnable, hAlarm, hEnable)
        self.lAlarm = float(lAlarm)
        self.lAlarmEnable = bool(lEnable)
        self.hAlarm = float(hAlarm)
        self.hAlarmEnable = bool(hEnable)

    #.............................................
    # Raise set-alarms popup
    def setAlarmsPopup(self):
        qp = QWidget.mapToGlobal(self, QPoint(0 + 30,
                                              0 + 30))  # where to pop up
        self.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def heightForWidth(self, w):
        return (w)

    #-----------------------------------------------------------------------
    def sizeHint(self):
        return QSize(self.minSize, self.minSize)

    #-----------------------------------------------------------------------
    def minimumSizeHint(self):
        return QSize(self.minSize, self.minSize)

    #-----------------------------------------------------------------------
    def set_name(self, name):
        self.name = name

    #-----------------------------------------------------------------------
    def set_debug(self, value):
        self.cfg.debug = value

    #-----------------------------------------------------------------------
    def update(self):
        self.newsize()

    #-----------------------------------------------------------------------
    def resizeEvent(self, ev):
        return
        print("<mrrwidget Resize>:", ev.size().width(), ev.size().height())
        print("    s.width(),s.height():", self.width(), self.height())

    #-----------------------------------------------------------------------
    def newsize(self):
        pass
        #s.scale_x = s.scale_y = float( s.height()  / s.minSize )
        #s.update() # s.repaint()

    #-----------------------------------------------------------------------
    def dump_list(self):

        for i in self.cfg.point_list:
            print("point_list:", i)
            print("---------------------------------------------")
            for i in self.cfg.element_list:
                print("element_list:", i)

    #-----------------------------------------------------------------------
    def zeroContrastAndBrightness(self):
        self.contrast = 0
        self.brightness = 0

    #-----------------------------------------------------------------------
    # buttons: L:1 M:4 R:2
    def mouseDoubleClickEvent(self, ev):
        button = ev.button()
        if button == LMB:  # Left Button
            ev.accept()
            x = ev.posF().x()
            y = ev.posF().y()
            ratio = self.logicalSize / self.width()
            x1 = x * ratio
            y1 = y * ratio

            self.mouseOverCell(x1, y1)

        #elif button == MMB: # Middle Button
        #   s.zeroContrastAndBrightness()

        #elif button == RMB:  # Right Button
        #    s.setAlarmsPopup()

    #-----------------------------------------------------------------------
    # buttons: L:1 M:4 R:2
    def mouseReleaseEvent(self, ev):

        button = ev.button()

        #if button == LMB: # Left Button
        #    s.mouseOverCell(x1,y1)

        if button == MMB:  # Middle Button
            ev.accept()
            self.zeroContrastAndBrightness()

        elif button == RMB:  # Right Button
            ev.accept()
            self.setAlarmsPopup()

    #----------------------------------------------------------------------


#    def mousePressEvent(s, ev):
#        x = ev.posF().x()
#        y = ev.posF().y()
#        ratio = s.logicalSize / s.width()
#        x1 = x * ratio
#        y1 = y * ratio
#s.mouseOverCell(x1,y1)

#print("ratio,wd:", ratio,s.width())
#print("Global Pos:", ev.globalPos())  #screen position
#print("Pos       :", ev.pos())        # relative to widget
#print("PosF      :", ev.posF())
#print("Pos       :", x,y)
#print("PosF      :", x,y)

#----------------------------------------------------------------------
# Mouse Drag : tied to brightness and contrast

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
        #print("BC", s.brightness, s.contrast)
        ev.accept()

    #----------------------------------------------------------------------
    def wheelEvent(self, we):
        #print("< %s wheelEvent >" % s.name )
        delta = we.delta()  # foreward:128 backware:-128
        self.wheelVal = we.delta() / self.wheelIncr
        self.wheelAccumVal += self.wheelVal
        #s.qhevent = QHelpEvent(QEvent.WhatsThis)
        #print("Delta:",we.delta(),"Val:",s.wheelVal,"Accum:",s.wheelAccumVal)

    # QWheelEvent.accept()

    #-----------------------------------------------------------------------
    #def ColorbarWheel(s): # called on action from mousewheel on colorbar
    #    print("< mirrorWidget.colorbarWheelEvent >")
    #

    #-----------------------------------------------------------------------
    # Initialize Colormaps
    #  #s.colormaps[s.cmapN][i] = QColor(hue,hue,hue)

    def init_colormaps(self):
        NCOLORCELLS = 255
        NINTENSITIES = 255
        NHSVHUES = 360
        NALPHAS = 255  # transparency. 255 = opaque

        self.colormaps = []
        self.maxCmaps = 6  # Maximum number of colormaps
        self.cmapN = Kst.GREYCMAP  # set startup colormap

        self.brightness = 0  # -1 to 1
        self.contrast = 0  # -1 to 1
        self.hsv_hue_range = NHSVHUES  # N Hues in hsv color system
        self.hsv_intensity_range = NINTENSITIES  # N intensities in hsv sys
        self.n_colormap_cells = NCOLORCELLS

        # monochrome greyscale
        self.hsvHue = 0  # color hue        =  color;
        self.hsvSat = 0  # color saturation =  color density
        self.hsvVal = 0  # color value      =  brightness
        self.hsvAph = NALPHAS  # color alpha      = transparency

        # make maxCmaps greyscale colormaps
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

        # Set operational colormap.
        self.colormap = self.colormaps[self.cmapN]

    #-----------------------------------------------------------------------
    def set_colormap(self, cmapN):
        self.cmapN = cmapN
        self.colormap = self.colormaps[cmapN]
        self.repaint()
        #s.update()

    #-----------------------------------------------------------------------
    def set_hsv(self, cmapN, hue, sat, val):
        self.colormap = self.colormaps[cmapN]
        alpha = 255  # transparency
        for i in range(0, self.n_colormap_cells):
            self.colormap[i] = QColor.fromHsv(hue, i, 255, alpha)

    #----------------------------------------------------------------------
    #    brightness = -1 to 1
    #    contrast   = -1 to 1
    def set_contrast(self, contrast):
        self.contrast = contrast

    #----------------------------------------------------------------------
    def set_brightness(self, brightness):
        self.brightness = brightness

    #-----------------------------------------------------------------------
    def set_normalization_constants(self):
        #s.cellDataRange  = s.constantMax - s.constantMin
        self.cellDataRange = self.cellDataMax - self.cellDataMin

        if self.cellDataRange <= 0:
            self.cellDataRange = 1
        self.cellDataK = self.hsv_intensity_range / self.cellDataRange
        #s.cellDataK      = s.cellDataRange / s.hsv_intensity_range
        if self.cfg.debug == 8:
            print("cellDataK    : ", self.name, self.cellDataK)
            print("cellDataRange: ", self.name, self.cellDataRange)

    #-----------------------------------------------------------------------
    def scale_and_contrast(self):

        self.set_normalization_constants()
        self.cellSCData = self.cellData * self.cellDataK
        if self.cfg.debug == 10:
            print(self.name, "SCdata 1:\n", self.cellSCData)
        if self.brightness < 0.0:
            self.cellSCData *= (1.0 + self.brightness)
        else:
            self.cellSCData = self.cellSCData + (
                    (1 - self.cellSCData) * self.brightness)
        self.cellSCData = (self.cellSCData - 0.5) * (tan(
                (self.contrast + 1) * pi / 4)) + 0.5
        self.cellSCData /= self.cellDataK

        # convert to range within hsv_intensity_range
        #s.cellSCData = (s.cellSCData - s.constantMin)
        self.cellSCData = (self.cellSCData - self.cellDataMin)
        self.intData = self.cellSCData * self.cellDataK  # 0 based
        self.intData = self.intData.astype(int).clip(min=0, max=254)

        self.repaint()

    #-----------------------------------------------------------------------
    def data_ready(self, data):

        # Get cell data frame
        self.cellData = data[self.ndxDataStart:self.ndxDataEnd].copy()

        # point to general data section
        gendata = data[Kst.GENDATASTART:Kst.GENDATAEND]

        # get various data
        self.frameN = gendata[Kst.FRAME_NUMBER]
        self.cellDataMin = gendata[self.ndxMin]  # cellData.min()
        self.cellDataMax = gendata[self.ndxMax]  # cellData.max()
        self.cellDataVar = gendata[self.ndxVar]  # cellData.var()
        self.cellDataAvg = gendata[self.ndxAvg]  # cellData average
        self.ctrlmtrx = gendata[Kst.CTRLMTRXSIDE]  # NGS/LGS : normal/inverted

        # Print data for debugging ?
        if self.cfg.debug > Kst.DBGLEVEL_RATE1:
            print("...........................................................")
            print(self.name, "data:\n", self.cellData)
            print("%s: Frame:%d Min:%.2f Max:%.2f Var:%.2f Avg:%.2f" %
                       (self.name, self.frameN, self.cellDataMin, self.cellDataMax, \
                       self.cellDataVar,self.cellDataAvg) )

        # Invert cellmap?
        # If cellMap state does not correspond to controlMatrix state,
        # if s.invertable then,
        # change cellMaps :
        # normal for NGS, inverted for LGS

        if self.invertable and self.cellMapState != self.ctrlmtrx:
            self.cellMapState = self.ctrlmtrx
            if self.ctrlmtrx == Kst.LGS_MATRIX:
                self.cellMap = cellMap.invertedCellMap

            elif self.ctrlmtrx == Kst.NGS_MATRIX:
                self.cellMap = cellMap.normalCellMap

            if self.selectedGuiCell is not None:
                self.selectedGuiCell = self.cellMap[
                        self.selectedCell]  #actual cell-number

        # enter safety mode?
        if self.ndxSafety is not None:
            safety = gendata[self.ndxSafety]  # current safety mode= On or Off?

            if safety:  # if safety
                if not self.safetyMode:  # if safety mode not already on
                    self.safetyMode = True  # turn on safety Mode
                    self.parent().safetyFrame(True)  # redden mirrorframe
                    self.colormap = self.colormaps[
                            Kst.SAFETYCMAP]  # set safety cmap
                    self.lg.warn("%s Safety ON" % self.name)  # log event

            elif not safety:
                if self.safetyMode:  # if safety mode is on
                    self.safetyMode = False  # turn off safety Mode
                    self.parent().safetyFrame(False)  # turn off red frame
                    self.colormap = self.colormaps[
                            Kst.GREYCMAP]  # set normal cmap
                    self.lg.warn("%s Safety OFF" % self.name)  # log event

        #
        self.scale_and_contrast()

        self.repaint()
        #s.update()
        #std =  sqrt(s.cellDataVar)

    #...........................................................................
    #
    #...........................................................................
    def startRotateCount(self):

        for cell in range(self.n_mrr_cells):
            self.intData[cell] = 254

        self.cell = 0
        self.timerId = self.startTimer(50)

    def rotateCount(self):
        if self.cell >= self.n_mrr_cells:
            self.cell = 0

        self.cellval = self.intData[self.cell]
        self.intData[self.cell] = 0
        self.selectedCell = self.cell
        self.selectedGuiCell = self.cellMap[self.cell]  #actual cell-number
        self.selectedCellPoint = self.polygons[self.cell].point(0)
        if self.cell > 0:
            self.intData[self.cell - 1] = self.cellval
        self.blankCells = False  # unused
        self.update()  #s.repaint()
        self.cell += 1

    #...........................................................................
    #
    #...........................................................................
    def timerEvent(self, e):
        if self.cell >= self.n_mrr_cells:
            self.killTimer(self.timerId)
            self.cell = 0
        else:
            self.rotateCount()

    def mouseOverCell(self, mx, my):
        #s.rotateCount()
        qp = QPoint(int(mx + 0.5), int(my + 0.5))  # qp = x,y of mouse click

        # for all mirror display cells
        for cell in range(self.n_mrr_cells):

            # if cell contains mouseclick point,
            #   o Remember selected-cell number
            #   o update (repaint)
            currently_selected = self.selectedCell
            if self.polygons[cell].containsPoint(qp, Qt.OddEvenFill):
                self.selectedCell = cell  #gui/drawing cell number
                self.selectedGuiCell = self.cellMap[cell]  #actual cell-number
                self.selectedCellPoint = qp
                self.blankCells = False
                self.cellRect = self.polygons[self.selectedCell].boundingRect()
                #s.ppath.addEllipse(QPointF(s.cellRect.center()), 4.0, 4.0)
                if currently_selected == self.selectedCell:
                    self.selectedCell = None

                #s.update() #
                self.repaint()

                break
