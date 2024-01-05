#===============================================================================
# File : MirrorWidget.py
#      : Offers class 'MirrorWidget'. A painted polygon map modelling
#        Subaru adaptive optics deformable mirror,
#
# Notes:
# o if cfg.debug == 8: dump various buffers
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import sys, time, random


from PyQt4.QtCore import (Qt,SIGNAL,SLOT,QPointF,QLine,QRect,QTimer, \
     QString,QPoint,QSize,QEvent)

from PyQt4.QtGui import (QRegion,QColor,QPolygon,QWidget,QPolygonF,\
     QFrame,QLabel,QStyleOption,QGridLayout,QSizePolicy,QSplitter, \
     QPainter,QPainterPath, QHelpEvent)

from math import *
import numpy as np
#import MirrorWidget_loader as loader
import loadPolygons as loader
import CmdlineOptions as opts
import Configuration
import Constants as Kst
import MirrorCellMap as cellMap  # map of device cells to display cells
import sys

# Mouse buttons
LMB = 1
MMB = 4
RMB = 2


#------------------------------------------------------------------------------
# MirrorWidget
#------------------------------------------------------------------------------
class MirrorWidget(QWidget):

    #.......................................................................
    def __init__(s, name="noname", parent=None, flags=Qt.WindowFlags()):
        super(MirrorWidget, s).__init__(parent)

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<MirrorWidget.__init__>:", name)
        s.name = name
        s.alarmDlg = None  # to be set by instantiater

        # read mirror polygons. Subtract 30 from coords for each vertex
        s.poly = loader.MirrorWidget_loader(pfactor=-30)

        # dump polygon list to stdout if debug greater than five
        if s.cfg.debug > 5:
            s.poly.prnPolygons()

        s.minSize = 244
        s.marginSize = 6
        s.logicalSize = s.minSize + s.marginSize
        s.marginSize = 0
        s.scaleX = 0.4
        s.scaleY = 0.4
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #.......................................................................
        s.xlate_x = s.xlate_y = 0  # mirror x/y translation
        s.n_mrr_cells = Kst.NMRRCELLS  # Number of mirror cells
        s.polygons = []
        s.mousepoint = QPoint(0, 0)
        s.contrast = 0
        s.brightness = 0
        #s.contrastK       = 2
        #s.brightnessK     = 2

        s.contrastK = 1.2  #  mouse delta to contrast constant
        s.brightnessK = 1.2  #  mouse delta to brightness constant

        s.firstdata = True
        s.constantMin = None  # set once by instantiator
        s.constantMax = None  # set once by instantiator
        s.cellDataMin = 0  # sent with each dataframe
        s.cellDataMax = 0  # sent with each dataframe
        s.mins = np.zeros(600, dtype=float)
        s.maxs = np.zeros(600, dtype=float)
        s.vars = np.zeros(600, dtype=float)

        #.......................................................................
        s.init_colormaps()

        #s.set_normalization_constants(0, 1880)# set dataMin,dataMax,dataRange
        s.frameCount = 0  # Our private data-frame counter

        # cellData   is raw mirror-data per dataFrame
        # cellSCData is fiddled data for display
        # intData    is cell-data scaled to colormap indexes
        s.cellData = np.zeros((s.n_mrr_cells + 1), dtype=float)
        s.cellSCData = np.zeros((s.n_mrr_cells), dtype=float)
        s.intData = np.zeros((s.n_mrr_cells), dtype=int)

        # Create artificial celldata for cell paint at startup.
        # Bump intensity toward high end of color scale.
        for i in range(0, s.n_mrr_cells):
            s.intData[i] = i + 255 - s.n_mrr_cells

        # Because there is more than 1 mirror display (DM,CRV,APD),
        # offsets into commonRTData are set by the frame displaying
        # this widget
        s.ndxMin = None
        s.ndxMax = None
        s.ndxVar = None
        s.ndxAvg = None
        s.ndxDataStart = None
        s.ndxDataEnd = None

        s.hAlarm = 0
        s.lAlarm = 0
        s.lAlarmEnable = False
        s.hAlarmEnable = False

        s.HighAlarmColor = QColor(Kst.CELLALARMRED)  # color of high alarm
        s.LowAlarmColor = QColor(Kst.CELLALARMYLW)  # color of low alarm

        #.......................................................................
        s.wheelVal = 0  # mouse delta value = +1:foreward, -1:backward
        s.wheelAccumVal = 0  # mousewheel accrued value after wheel event
        s.wheelIncr = 120  # probable delta from wheel event=ev.delta
        #.......................................................................
        s.painter = QPainter()
        s.ppath = QPainterPath()

        s.pencolor = Qt.black
        s.brushcolor = Qt.green
        s.paintcount = 0
        #.......................................................................
        s.polygons = s.poly.polygons  # read mirror polygons from config file

        s.firstPlot = 1

        # add polygon to paint-path for paint-path painting
        # s.ppath.addPolygon(QPolygonF(QPolygon(points_array)))

        #.......................................................................
        s.cell = 0
        s.timerId = None
        s.selectedCell = None  # no cell selected to show
        s.selectedGuiCell = None
        s.blankCells = False
        s.safetyMode = False

        s.setWhatsThis(
                QString("LeftClick&Drag to set Contrast & Brightness. Double left click to select/unselect cell."
                        ))

        # set normal cellmap (i.e. non-inverted) for natural-guide-star mode
        s.cellMapState = Kst.NGS_MATRIX
        s.cellMap = cellMap.normalCellMap

    #...........................................................................
    def paintEvent(s, ev):
        s.paint()
        ev.accept()

    #...........................................................................
    # Paint
    # s.painter.scale(s.scale_x,s.scale_y)
    #...........................................................................
    def paint(s):
        wd = s.width()
        ht = s.height()
        s.side = min(wd, ht)

        # Paint
        try:
            s.painter.begin(s)
        except Exception as e:
            s.lg.error("Mrr paint exception #1:", e)
            s.painter.end(s)
            return

        s.painter.setPen(s.pencolor)
        s.painter.setBrush(s.brushcolor)
        s.painter.setViewport(0, 0, s.side, s.side)
        s.painter.setWindow(0, 0, s.logicalSize, s.logicalSize)

        # paint polygons
        # 'i' is index to polygon list
        for i in range(0, s.n_mrr_cells):

            # translate polygon index to actual mirrorcell number
            # Cellmap is normal for Natural Guide Star (NGS)
            # or inverted for Laser Guide Star (LGS)
            cell = s.cellMap[i]

            # set value for this cell from zero-based celldata array
            cellval = s.cellData[cell - 1]

            # High alarm check
            if s.hAlarmEnable and cellval >= s.hAlarm:
                try:
                    s.painter.setBrush(s.HighAlarmColor)  #set hAlarm color
                except Exception as e:
                    s.lg.error("Mirror alarm Paint exception:%s" % e)
                    s.lg.error("%s MirroWidget.  Polygon:%d" % (s.name, i))
                    s.painter.end()
                    return

            # Low alarm check
            elif s.lAlarmEnable and cellval <= s.lAlarm:
                try:
                    s.painter.setBrush(s.LowAlarmColor)  # set lAlarm color
                except Exception as e:
                    s.lg.error("Mirror alarm Paint exception:%s" % e)
                    s.lg.error("%s MirroWidget.  Polygon:%d" % (s.name, i))
                    s.painter.end()
                    return

            # No alarms. set cell-color from normal colormap
            else:
                try:
                    s.painter.setBrush(s.colormap[s.intData[cell - 1]])
                except Exception as e:
                    s.lg.error("Mirror paint exception #2:%s. Cell:%d" %
                               (e, cell))
                    s.lg.error("%s MirroWidget.  Polygon:%d" % (s.name, i))
                    s.painter.end()
                    return

            # paint the cell
            s.painter.drawPolygon(s.polygons[i])

        # Indicate selected-cell

        if s.selectedCell is not None:
            if s.blankCells:
                s.blankCells = False
                colormap = s.colormaps[s.graduatedCmap]
                for i in range(0, s.n_mrr_cells):
                    s.painter.setBrush(colormap[i])
                    s.painter.drawPolygon(s.polygons[i])

            s.cellRect = s.polygons[s.selectedCell].boundingRect()
            s.painter.setPen(QColor('#00FF00'))  # over the cell text
            s.painter.setBrush(QColor('#00FF00'))
            s.painter.drawText(s.selectedCellPoint,
                               QString(" %d" % s.selectedGuiCell))

            # print cell number and value on frame
            s.painter.drawEllipse(QPointF(s.cellRect.center()), 4.0, 4.0)
            s.painter.setPen(QColor('#000000'))  # text color
            s.painter.drawText(
                    QPoint(0, 250),
                    QString("cell %3d: %8.2f" %
                            (s.selectedGuiCell,
                             s.cellData[s.selectedGuiCell - 1])))

        if s.safetyMode:
            s.painter.drawText(QPoint(0, 20), QString("SAFETY"))

        # Brightness & Contrast
        #s.painter.drawText(QPoint(0,225),QString("b:%.2f\nc:%.2f"%(s.brightness,s.contrast)))

        # Display brightness and contrast
        s.painter.drawText(QPoint(0, 225), QString("b: %5.2f" % (s.brightness)))
        s.painter.drawText(QPoint(0, 235), QString("c: %5.2f" % (s.contrast)))

        s.painter.end()

    #----------------------------------------------------------------------
    def setAlarms(s, lAlarm, lEnable, hAlarm, hEnable):
        #print("<MirrorWidget>.setAlarms", s.name, lAlarm, lEnable, hAlarm, hEnable)
        s.lAlarm = float(lAlarm)
        s.lAlarmEnable = bool(lEnable)
        s.hAlarm = float(hAlarm)
        s.hAlarmEnable = bool(hEnable)

    #.............................................
    # Raise set-alarms popup
    def setAlarmsPopup(s):
        qp = QWidget.mapToGlobal(s, QPoint(0 + 30, 0 + 30))  # where to pop up
        s.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def heightForWidth(s, w):
        return (w)

    #-----------------------------------------------------------------------
    def sizeHint(s):
        return QSize(s.minSize, s.minSize)

    #-----------------------------------------------------------------------
    def minimumSizeHint(s):
        return QSize(s.minSize, s.minSize)

    #-----------------------------------------------------------------------
    def set_name(s, name):
        s.name = name

    #-----------------------------------------------------------------------
    def set_debug(s, value):
        s.cfg.debug = value

    #-----------------------------------------------------------------------
    def update(s):
        s.newsize()

    #-----------------------------------------------------------------------
    def resizeEvent(s, ev):
        return
        print("<mrrwidget Resize>:", ev.size().width(), ev.size().height())
        print("    s.width(),s.height():", s.width(), s.height())

    #-----------------------------------------------------------------------
    def newsize(s):
        pass
        #s.scale_x = s.scale_y = float( s.height()  / s.minSize )
        #s.update() # s.repaint()

    #-----------------------------------------------------------------------
    def dump_list(s):

        for i in s.cfg.point_list:
            print("point_list:", i)
            print("---------------------------------------------")
            for i in s.cfg.element_list:
                print("element_list:", i)

    #-----------------------------------------------------------------------
    def zeroContrastAndBrightness(s):
        s.contrast = 0
        s.brightness = 0

    #-----------------------------------------------------------------------
    # buttons: L:1 M:4 R:2
    def mouseDoubleClickEvent(s, ev):
        button = ev.button()
        if button == LMB:  # Left Button
            ev.accept()
            x = ev.posF().x()
            y = ev.posF().y()
            ratio = s.logicalSize / s.width()
            x1 = x * ratio
            y1 = y * ratio

            s.mouseOverCell(x1, y1)

        #elif button == MMB: # Middle Button
        #   s.zeroContrastAndBrightness()

        #elif button == RMB:  # Right Button
        #    s.setAlarmsPopup()

    #-----------------------------------------------------------------------
    # buttons: L:1 M:4 R:2
    def mouseReleaseEvent(s, ev):

        button = ev.button()

        #if button == LMB: # Left Button
        #    s.mouseOverCell(x1,y1)

        if button == MMB:  # Middle Button
            ev.accept()
            s.zeroContrastAndBrightness()

        elif button == RMB:  # Right Button
            ev.accept()
            s.setAlarmsPopup()

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
        #print("BC", s.brightness, s.contrast)
        ev.accept()

    #----------------------------------------------------------------------
    def wheelEvent(s, we):
        #print("< %s wheelEvent >" % s.name )
        delta = we.delta()  # foreward:128 backware:-128
        s.wheelVal = we.delta() / s.wheelIncr
        s.wheelAccumVal += s.wheelVal
        #s.qhevent = QHelpEvent(QEvent.WhatsThis)
        #print("Delta:",we.delta(),"Val:",s.wheelVal,"Accum:",s.wheelAccumVal)
    # QWheelEvent.accept()

    #-----------------------------------------------------------------------
    #def ColorbarWheel(s): # called on action from mousewheel on colorbar
    #    print("< MirrorWidget.colorbarWheelEvent >")
    #

    #-----------------------------------------------------------------------
    # Initialize Colormaps
    #  #s.colormaps[s.cmapN][i] = QColor(hue,hue,hue)

    def init_colormaps(s):
        NCOLORCELLS = 255
        NINTENSITIES = 255
        NHSVHUES = 360
        NALPHAS = 255  # transparency. 255 = opaque

        s.colormaps = []
        s.maxCmaps = 6  # Maximum number of colormaps
        s.cmapN = Kst.GREYCMAP  # set startup colormap

        s.brightness = 0  # -1 to 1
        s.contrast = 0  # -1 to 1
        s.hsv_hue_range = NHSVHUES  # N Hues in hsv color system
        s.hsv_intensity_range = NINTENSITIES  # N intensities in hsv sys
        s.n_colormap_cells = NCOLORCELLS

        # monochrome greyscale
        s.hsvHue = 0  # color hue        =  color;
        s.hsvSat = 0  # color saturation =  color density
        s.hsvVal = 0  # color value      =  brightness
        s.hsvAph = NALPHAS  # color alpha      = transparency

        # make maxCmaps greyscale colormaps
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

        # Set operational colormap.
        s.colormap = s.colormaps[s.cmapN]

    #-----------------------------------------------------------------------
    def set_colormap(s, cmapN):
        s.cmapN = cmapN
        s.colormap = s.colormaps[cmapN]
        s.repaint()
        #s.update()

    #-----------------------------------------------------------------------
    def set_hsv(s, cmapN, hue, sat, val):
        s.colormap = s.colormaps[cmapN]
        alpha = 255  # transparency
        for i in range(0, s.n_colormap_cells):
            s.colormap[i] = QColor.fromHsv(hue, i, 255, alpha)

    #----------------------------------------------------------------------
    #    brightness = -1 to 1
    #    contrast   = -1 to 1
    def set_contrast(s, contrast):
        s.contrast = contrast

    #----------------------------------------------------------------------
    def set_brightness(s, brightness):
        s.brightness = brightness

    #-----------------------------------------------------------------------
    def set_normalization_constants(s):
        #s.cellDataRange  = s.constantMax - s.constantMin
        s.cellDataRange = s.cellDataMax - s.cellDataMin

        if s.cellDataRange <= 0:
            s.cellDataRange = 1
        s.cellDataK = s.hsv_intensity_range / s.cellDataRange
        #s.cellDataK      = s.cellDataRange / s.hsv_intensity_range
        if s.cfg.debug == 8:
            print("cellDataK    : ", s.name, s.cellDataK)
            print("cellDataRange: ", s.name, s.cellDataRange)

    #-----------------------------------------------------------------------
    def scale_and_contrast(s):

        s.set_normalization_constants()
        s.cellSCData = s.cellData * s.cellDataK
        if s.cfg.debug == 10: print(s.name, "SCdata 1:\n", s.cellSCData)
        if s.brightness < 0.0:
            s.cellSCData *= (1.0 + s.brightness)
        else:
            s.cellSCData = s.cellSCData + ((1 - s.cellSCData) * s.brightness)
        s.cellSCData = (s.cellSCData - 0.5) * (tan(
                (s.contrast + 1) * pi / 4)) + 0.5
        s.cellSCData /= s.cellDataK

        # convert to range within hsv_intensity_range
        #s.cellSCData = (s.cellSCData - s.constantMin)
        s.cellSCData = (s.cellSCData - s.cellDataMin)
        s.intData = s.cellSCData * s.cellDataK  # 0 based
        s.intData = s.intData.astype(int).clip(min=0, max=254)

        s.repaint()

    #-----------------------------------------------------------------------
    def data_ready(s, data):

        # Get cell data frame
        s.cellData = data[s.ndxDataStart:s.ndxDataEnd].copy()

        # point to general data section
        gendata = data[Kst.GENDATASTART:Kst.GENDATAEND]

        # get various data
        s.frameN = gendata[Kst.FRAME_NUMBER]
        s.cellDataMin = gendata[s.ndxMin]  # cellData.min()
        s.cellDataMax = gendata[s.ndxMax]  # cellData.max()
        s.cellDataVar = gendata[s.ndxVar]  # cellData.var()
        s.cellDataAvg = gendata[s.ndxAvg]  # cellData average
        s.ctrlmtrx = gendata[Kst.CTRLMTRXSIDE]  # NGS/LGS : normal/inverted

        # Print data for debugging ?
        if s.cfg.debug > Kst.DBGLEVEL_RATE1:
            print("...........................................................")
            print(s.name, "data:\n", s.cellData)
            print("%s: Frame:%d Min:%.2f Max:%.2f Var:%.2f Avg:%.2f" %
                       (s.name, s.frameN, s.cellDataMin, s.cellDataMax, \
                       s.cellDataVar,s.cellDataAvg) )

        # Invert cellmap?
        # If cellMap state does not correspond to controlMatrix state,
        # if s.invertable then,
        # change cellMaps :
        # normal for NGS, inverted for LGS

        if s.invertable and s.cellMapState != s.ctrlmtrx:
            s.cellMapState = s.ctrlmtrx
            if s.ctrlmtrx == Kst.LGS_MATRIX:
                s.cellMap = cellMap.invertedCellMap

            elif s.ctrlmtrx == Kst.NGS_MATRIX:
                s.cellMap = cellMap.normalCellMap

            if s.selectedGuiCell is not None:
                s.selectedGuiCell = s.cellMap[
                        s.selectedCell]  #actual cell-number

        # enter safety mode?
        if s.ndxSafety is not None:
            safety = gendata[s.ndxSafety]  # current safety mode= On or Off?

            if safety:  # if safety
                if not s.safetyMode:  # if safety mode not already on
                    s.safetyMode = True  # turn on safety Mode
                    s.parent().safetyFrame(True)  # redden mirrorframe
                    s.colormap = s.colormaps[Kst.SAFETYCMAP]  # set safety cmap
                    s.lg.warn("%s Safety ON" % s.name)  # log event

            elif not safety:
                if s.safetyMode:  # if safety mode is on
                    s.safetyMode = False  # turn off safety Mode
                    s.parent().safetyFrame(False)  # turn off red frame
                    s.colormap = s.colormaps[Kst.GREYCMAP]  # set normal cmap
                    s.lg.warn("%s Safety OFF" % s.name)  # log event

        #
        s.scale_and_contrast()

        s.repaint()
        #s.update()
        #std =  sqrt(s.cellDataVar)

    #...........................................................................
    #
    #...........................................................................
    def startRotateCount(s):

        for cell in range(s.n_mrr_cells):
            s.intData[cell] = 254

        s.cell = 0
        s.timerId = s.startTimer(50)

    def rotateCount(s):
        if s.cell >= s.n_mrr_cells:
            s.cell = 0

        s.cellval = s.intData[s.cell]
        s.intData[s.cell] = 0
        s.selectedCell = s.cell
        s.selectedGuiCell = s.cellMap[s.cell]  #actual cell-number
        s.selectedCellPoint = s.polygons[s.cell].point(0)
        if s.cell > 0:
            s.intData[s.cell - 1] = s.cellval
        s.blankCells = False  # unused
        s.update()  #s.repaint()
        s.cell += 1

    #...........................................................................
    #
    #...........................................................................
    def timerEvent(s, e):
        if s.cell >= s.n_mrr_cells:
            s.killTimer(s.timerId)
            s.cell = 0
        else:
            s.rotateCount()

    def mouseOverCell(s, mx, my):
        #s.rotateCount()
        qp = QPoint(int(mx + 0.5), int(my + 0.5))  # qp = x,y of mouse click

        # for all mirror display cells
        for cell in range(s.n_mrr_cells):

            # if cell contains mouseclick point,
            #   o Remember selected-cell number
            #   o update (repaint)
            currently_selected = s.selectedCell
            if s.polygons[cell].containsPoint(qp, Qt.OddEvenFill):
                s.selectedCell = cell  #gui/drawing cell number
                s.selectedGuiCell = s.cellMap[cell]  #actual cell-number
                s.selectedCellPoint = qp
                s.blankCells = False
                s.cellRect = s.polygons[s.selectedCell].boundingRect()
                #s.ppath.addEllipse(QPointF(s.cellRect.center()), 4.0, 4.0)
                if currently_selected == s.selectedCell:
                    s.selectedCell = None

                #s.update() #
                s.repaint()

                break

    #----------------------------------------------------------------------
    #def test_contrast (s, brightness, contrast ):
    #   for i in range (0,s.n_mrr_cells):
    #       val = s.data[i]/254
    #       if s.brightness < 0.0:
    #           val = val * (1.0 + s.brightness)
    #       else:
    #           val = val + ((1 - val) * s.brightness)
    #
    #       val = (val - 0.5) * (tan((s.contrast+1) * pi/4) ) + 0.5
    #
    #       s.tmpData[i] = val * 254
    #

    #   s.update()   #   s.repaint()
    #
    #-----------------------------------------------------------------------
    # xlate cellData to integer range 0 - ncolorvals:
    # Called after scale_and_contrast, above
    #def xlate(s):
    #    s.cellSCData = (s.cellSCData - s.constantMin) * s.cellDataK
    #    s.intData = s.cellSCData.astype(int).clip(min=0, max=254)

    #-----------------------------------------------------------------------
    #def colorSelected(s,color):
    #    print("ColorSelected")
    #    hue = color.hsvHue()
    #    sat = color.saturation()
    #    val =  color.value()
    #    print("Hue:", hue)
    #    print("Sat:", sat)
    #    print("Val:", val)
    #    s.set_hsv(s.cmapN, hue,sat,val)
    #    s.update() # s.repaint()

    #...........................................................................
    #def colorChoice(s,color):
    #    print("ColorChoice")
    #    hue = color.hsvHue()
    #    sat = color.saturation()
    #    val = color.value()
    #    print("Hue:", color.hsvHue())
    #    print("Sat:", color.saturation())
    #    print("Val:", color.value())
    #
