#===============================================================================
# File : SHFrame.py
#      : Shack-Hartmann LensletWidget, and  labels, a 4X4 map of Shack-Hartmann
#      : Lenslet array used by Subaru adaptive optics.
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
from PyQt4.QtCore import (Qt, QRect, QString, SIGNAL, QPoint)
from PyQt4.QtGui import (QColor,QWidget,QFrame,QLabel,QStyleOption, \
                 QGridLayout,QBoxLayout,QSizePolicy,QSplitter, \
                 QMenuBar,QMenu,QAction, QVBoxLayout,QHBoxLayout, \
                 QActionGroup)
import PyQt4.Qwt5 as Qwt

import Constants as Kst
import Configuration
import SHWidget
import Labels
import AlarmDialogue


#------------------------------------------------------------------------------
# SHFrame
#------------------------------------------------------------------------------
class SHFrame(QFrame):

    def __init__(s, name="noname", parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.lg.debug("<SHFrame.__init__>:%s" % name)
        if s.cfg.debug: print("<SHFrame.__init__>:%s" % name)
        #............................................................
        super(SHFrame, s).__init__(parent)
        s.name = name
        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Raised)
        s.setMidLineWidth(1)
        s.setLineWidth(1)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  #hrz,vrt

        #............................................................
        s.layout = QVBoxLayout()
        s.setLayout(s.layout)
        s.topLayout = QHBoxLayout()
        s.midLayout = QHBoxLayout()
        #............................................................
        s.lbl_title = QLabel(s.name, s)
        s.lbl_title.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)  #hrz,vrt
        s.lbl_title.setMaximumHeight(16)
        #............................................................
        s.hzSplit00 = QSplitter(Qt.Horizontal)
        s.shw = SHWidget.SHWidget(s)
        s.sldfrm = QFrame(s)

        # Menu
        s.createMenu()

        # Defocus Slider
        s.create_defocus_indicator()

        # Labelled-values frame
        s.labelsFrame = Labels.SHLabelsFrame()

        # Layout
        s.topLayout.addWidget(s.lbl_title)
        s.topLayout.addWidget(s.hzSplit00)
        s.topLayout.addWidget(s.menubar)
        s.midLayout.addWidget(s.sld)
        s.midLayout.addWidget(s.shw)

        s.layout.addLayout(s.topLayout)
        s.layout.addLayout(s.midLayout)
        s.layout.addWidget(s.labelsFrame)
        #-----------------------------------------------------------------------
        #fg     = " QFrame {color:red}"
        #bg     = " QFrame {background-color:%s}" % '#00FF00'
        #s.sldfrm.setStyleSheet(fg+bg)
        #s.sldfrm.setFrameRect(QRect(0,0,20,100))
        #-----------------------------------------------------------------------
        s.configChangeHandler()  # force alarm values updata from current config

    #-----------------------------------------------------------------------
    def defocus_data_ready(s, data):
        val = data[Kst.GENDATASTART + Kst.LWF_DEFOCUS]
        if s.cfg.debug >= Kst.DBGLEVEL_RATE2:
            print("SH defocus data:", val)

        # value rangecheck
        if val > 1.0:
            s.sld.setRange(0, val + val * 0.1)

        if val < -1.0:
            s.sld.setRange(val - val * 0.1, 0 + val * 0.1)

        else:
            s.sld.setRange(-0.1, 0.1)

        s.sld.setValue(val)

    #-----------------------------------------------------------------------
    # Defocus slider
    #
    # Notes:
    # stylesheet:
    # color,background-color,alternate-background-color
    # border-color,
    # border-top-color,border-bottom-color,border-right-color,border-left-color,
    # gridline-color,
    # selection-color, selection-background-color
    #s.sld.setScaleEngine(Qwt.QwtLog10ScaleEngine())
    #s.sld.setScaleMaxMinor(0.1)

    #s.sld.setScaleEngine(Qwt.QwtLog10ScaleEngine())
    #s.sld.setRange(0.0, 4.0, 0.01)
    #s.sld.setScale(1, 1.0e3)

    #s.slw.setHandleSize(10,10) # no such attribute
    #s.setScale(0,10)     # NO such... #Visible scale min/max
    #seg s.sld=Qwt.QwtSlider(s,ScalePos=Qt.Vertical|Qwt.QwtSlider.LeftScale)
    #print("scalepos:", s.sld.scalePosition())
    #s.slw.setStep(0.1)
    #s.slw.setRange( 0.0,100.0)
    #s.slw.setScale(0.0, 100.0, 10.0)

    #s.scw = Qwt.QwtScaleWidget()
    #s.scw.setScaleDiv(0,100, )
    #s.scw.setAlignment(Qwt.QwtScaleDraw.RightScale)
    #       bgStyle=Qwt.QwtSlider.Trough)
    #------------------------------------------------------------------------
    def create_defocus_indicator(s):
        import PyQt4.Qwt5 as Qwt
        s.sld = Qwt.QwtSlider(s, Qt.Vertical, Qwt.QwtSlider.RightScale,
                              Qwt.QwtSlider.BgBoth)
        s.sld.ScalePos(2)
        #s.sld.setAutoScale()
        s.sld.setRange(-1, 1.0)
        s.sld.setThumbWidth(15)  #
        s.sld.setThumbLength(10)  # in this case, height
        s.sld.setBorderWidth(1)
        #s.sld.setMargins(20,0) # w,h
        s.sld.setFixedWidth(70)
        s.sld.setReadOnly(True)
        fg = " QwtSlider {color:black}"  # scalenumeral color
        bg = " QwtSlider {background-color:%s}" % '#00FF00'  # thumbgrip color
        abg = " QwtSlider {alternate-background-color:%s}" % '#FF0000'
        s.sld.setStyleSheet(fg + bg + abg)
        #s.sld.setToolTip(QString("Defocus ToolTip"))
        s.sld.setWhatsThis(QString("Defocus Indicator"))
        s.setToolTip(QString("Defocus Indicator"))

    #---------------------------------------------------------------------------
    # 10 frames per update is 1 Hz at 10frames/sec
    def set_1Hz_ArrowUpdate(s):
        s.cfg.framesPerSHArrow = 10
        s.lg.info("SH Arrows update rate: 1 Hz")

    #---------------------------------------------------------------------------
    # 5 frames per update is 2 Hz at 10frames/sec
    def set_2Hz_ArrowUpdate(s):
        s.cfg.framesPerSHArrow = 5
        s.lg.info("SH Arrows update rate: 2 Hz")

    #---------------------------------------------------------------------------
    # 2 frames per update is 5 Hz at 10frames/sec
    def set_5Hz_ArrowUpdate(s):
        s.cfg.framesPerSHArrow = 2
        s.lg.info("SH Arrows update rate: 3.3 Hz")

    #---------------------------------------------------------------------------
    # 1 frame per update is 10 Hz at 10frames/sec
    def set_10Hz_ArrowUpdate(s):
        s.cfg.framesPerSHArrow = 1
        s.lg.info("SH Arrows update rate: 10Hz")

    #...........................................................................
    def setGreyCmap(s):
        s.shw.set_colormap(1)

    #...........................................................................
    def setGreenCmap(s):
        s.shw.set_colormap(3)

    #---------------------------------------------------------------------------
    def createMenu(s):
        s.menubar = QMenuBar()
        s.menu = QMenu('Menu')

        s.cmapMenu = QMenu('Colormaps')
        s.cmapMenu.addAction("Grey", s.setGreyCmap)
        s.cmapMenu.addAction("Green", s.setGreenCmap)
        s.menu.addMenu(s.cmapMenu)
        s.arrowMenu = QMenu('Arrows')

        #.......................................................................
        # Arrow update rate
        #.......................................................................
        act1 = s.arrowMenu.addAction(" 1 Hz Arrows", s.set_1Hz_ArrowUpdate)
        act2 = s.arrowMenu.addAction(" 2 Hz Arrows", s.set_2Hz_ArrowUpdate)
        act3 = s.arrowMenu.addAction(" 5 Hz Arrows", s.set_5Hz_ArrowUpdate)
        act4 = s.arrowMenu.addAction("10 Hz Arrows", s.set_10Hz_ArrowUpdate)
        act1.setCheckable(True)
        act2.setCheckable(True)
        act3.setCheckable(True)
        act4.setCheckable(True)

        # 1  frame per update is 10 Hz at 10frames/sec
        if s.cfg.framesPerSHArrow == 10:
            act1.setChecked(True)
        elif s.cfg.framesPerSHArrow == 5:
            act2.setChecked(True)
        elif s.cfg.framesPerSHArrow == 2:
            act3.setChecked(True)
        else:  # s.shw.framesPerSHArrowsUpdate == 1:
            act4.setChecked(True)

        s.actGroup = QActionGroup(s.arrowMenu)
        s.actGroup.setExclusive(True)
        s.actGroup.addAction(act1)
        s.actGroup.addAction(act2)
        s.actGroup.addAction(act3)
        s.actGroup.addAction(act4)

        s.sep1 = s.arrowMenu.addSeparator()
        s.arrowMenu.addAction(act1)
        s.arrowMenu.addAction(act2)
        s.arrowMenu.addAction(act3)
        s.arrowMenu.addAction(act4)
        s.sep2 = s.arrowMenu.addSeparator()
        s.menu.addMenu(s.arrowMenu)

        #.......................................................................
        # Alarms
        #.......................................................................
        # Alarms menu
        #s.alarmsMenu    = QMenu('Alarms')
        #s.alarmsMenu.addAction("Set",  s.setAlarmsPopup )
        #s.menu.addMenu(s.alarmsMenu)
        s.menubar.addMenu(s.menu)  # add menu to menubar

        dct = s.cfg.cfgD['sheye']
        s.shw.alarmDlg = AlarmDialogue.AlarmDialog('SH-EYE ALARMS', dct)
        s.connect(s.shw.alarmDlg, SIGNAL('ConfigChanged'),
                  s.configChangeHandler)
        s.menubar.addMenu(s.menu)

    #.............................................
    # Set Alarms menu popup
    #def setAlarmsPopup(s):
    #    qp = QWidget.mapToGlobal (s, QPoint(0,0)) # where to pop up
    #    s.shw.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def configChangeHandler(s):
        #print("<SHFrame>.configChangeHandler", s.name)
        dct = s.cfg.cfgD['sheye']
        # set eye alarms/enables
        s.shw.setAlarms(dct['alarmLow']['value' ], dct['alarmLow']['enable'], \
                        dct['alarmHi' ]['value' ], dct['alarmHi' ]['enable']  )
