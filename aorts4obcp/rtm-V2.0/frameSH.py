#===============================================================================
# File : SHFrame.py
#      : Shack-Hartmann LensletWidget, and  labels, a 4X4 map of Shack-Hartmann
#      : Lenslet array used by Subaru adaptive optics.
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QLabel, QSlider, QSizePolicy, QSplitter,
                             QMenuBar, QMenu, QVBoxLayout, QHBoxLayout,
                             QActionGroup)

import constants as Kst
import configuration
import shWidget
import labels
import alarmDialog


#------------------------------------------------------------------------------
# SHFrame
#------------------------------------------------------------------------------
class SHFrame(QFrame):

    def __init__(self, name="noname", parent=None):
        self.cfg = configuration.cfg
        self.lg = self.cfg.lg
        self.lg.debug("<SHFrame.__init__>:%s" % name)
        if self.cfg.debug: print("<SHFrame.__init__>:%s" % name)
        #............................................................
        super(SHFrame, self).__init__(parent)
        self.name = name
        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setMidLineWidth(1)
        self.setLineWidth(1)
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)  #hrz,vrt

        #............................................................
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.topLayout = QHBoxLayout()
        self.midLayout = QHBoxLayout()
        #............................................................
        self.lbl_title = QLabel(self.name, self)
        self.lbl_title.setSizePolicy(QSizePolicy.Fixed,
                                     QSizePolicy.Fixed)  #hrz,vrt
        self.lbl_title.setMaximumHeight(16)
        #............................................................
        self.hzSplit00 = QSplitter(Qt.Horizontal)
        self.shw = shWidget.SHWidget(self)
        self.sldfrm = QFrame(self)

        # Menu
        self.createMenu()

        # Defocus Slider
        self.create_defocus_indicator()

        # Labelled-values frame
        self.labelsFrame = labels.SHLabelsFrame()

        # Layout
        self.topLayout.addWidget(self.lbl_title)
        self.topLayout.addWidget(self.hzSplit00)
        self.topLayout.addWidget(self.menubar)
        self.midLayout.addWidget(self.sld)
        self.midLayout.addWidget(self.shw)

        self.layout.addLayout(self.topLayout)
        self.layout.addLayout(self.midLayout)
        self.layout.addWidget(self.labelsFrame)
        #-----------------------------------------------------------------------
        #fg     = " QFrame {color:red}"
        #bg     = " QFrame {background-color:%s}" % '#00FF00'
        #s.sldfrm.setStyleSheet(fg+bg)
        #s.sldfrm.setFrameRect(QRect(0,0,20,100))
        #-----------------------------------------------------------------------
        self.configChangeHandler(
        )  # force alarm values updata from current config

    #-----------------------------------------------------------------------
    def defocus_data_ready(self, data):
        val = data[Kst.GENDATASTART + Kst.LWF_DEFOCUS]
        if self.cfg.debug >= Kst.DBGLEVEL_RATE2:
            print("SH defocus data:", val)

        # value rangecheck
        if val > 1.0:
            self.sld.setRange(0, val + val * 0.1)

        if val < -1.0:
            self.sld.setRange(val - val * 0.1, 0 + val * 0.1)

        else:
            self.sld.setRange(-0.1, 0.1)

        self.sld.setValue(val)

    #------------------------------------------------------------------------
    def create_defocus_indicator(self):

        self.sld = QSlider(Qt.Vertical, self)
        self.sld.setTickPosition(QSlider.TicksRight)

        #self.sld.ScalePos(2)
        #s.sld.setAutoScale()
        self.sld.setRange(-1, 1.0)
        #self.sld.setThumbWidth(15)  #
        #self.sld.setThumbLength(10)  # in this case, height

        #self.sld.setBorderWidth(1)
        #s.sld.setMargins(20,0) # w,h
        self.sld.setFixedWidth(70)
        #self.sld.setReadOnly(True)
        fg = " QSlider {color:black}"  # scalenumeral color
        bg = " QSlider {background-color:%s}" % '#00FF00'  # thumbgrip color
        abg = " QSlider {alternate-background-color:%s}" % '#FF0000'

        self.sld.setStyleSheet(fg + bg + abg)
        self.sld.setWhatsThis("Defocus Indicator")
        self.setToolTip("Defocus Indicator")

    #---------------------------------------------------------------------------
    # 10 frames per update is 1 Hz at 10frames/sec
    def set_1Hz_ArrowUpdate(self):
        self.cfg.framesPerSHArrow = 10
        self.lg.info("SH Arrows update rate: 1 Hz")

    #---------------------------------------------------------------------------
    # 5 frames per update is 2 Hz at 10frames/sec
    def set_2Hz_ArrowUpdate(self):
        self.cfg.framesPerSHArrow = 5
        self.lg.info("SH Arrows update rate: 2 Hz")

    #---------------------------------------------------------------------------
    # 2 frames per update is 5 Hz at 10frames/sec
    def set_5Hz_ArrowUpdate(self):
        self.cfg.framesPerSHArrow = 2
        self.lg.info("SH Arrows update rate: 3.3 Hz")

    #---------------------------------------------------------------------------
    # 1 frame per update is 10 Hz at 10frames/sec
    def set_10Hz_ArrowUpdate(self):
        self.cfg.framesPerSHArrow = 1
        self.lg.info("SH Arrows update rate: 10Hz")

    #...........................................................................
    def setGreyCmap(self):
        self.shw.set_colormap(1)

    #...........................................................................
    def setGreenCmap(self):
        self.shw.set_colormap(3)

    #---------------------------------------------------------------------------
    def createMenu(self):
        self.menubar = QMenuBar()
        self.menu = QMenu('Menu')

        self.cmapMenu = QMenu('Colormaps')
        self.cmapMenu.addAction("Grey", self.setGreyCmap)
        self.cmapMenu.addAction("Green", self.setGreenCmap)
        self.menu.addMenu(self.cmapMenu)
        self.arrowMenu = QMenu('Arrows')

        #.......................................................................
        # Arrow update rate
        #.......................................................................
        act1 = self.arrowMenu.addAction(" 1 Hz Arrows",
                                        self.set_1Hz_ArrowUpdate)
        act2 = self.arrowMenu.addAction(" 2 Hz Arrows",
                                        self.set_2Hz_ArrowUpdate)
        act3 = self.arrowMenu.addAction(" 5 Hz Arrows",
                                        self.set_5Hz_ArrowUpdate)
        act4 = self.arrowMenu.addAction("10 Hz Arrows",
                                        self.set_10Hz_ArrowUpdate)
        act1.setCheckable(True)
        act2.setCheckable(True)
        act3.setCheckable(True)
        act4.setCheckable(True)

        # 1  frame per update is 10 Hz at 10frames/sec
        if self.cfg.framesPerSHArrow == 10:
            act1.setChecked(True)
        elif self.cfg.framesPerSHArrow == 5:
            act2.setChecked(True)
        elif self.cfg.framesPerSHArrow == 2:
            act3.setChecked(True)
        else:  # s.shw.framesPerSHArrowsUpdate == 1:
            act4.setChecked(True)

        self.actGroup = QActionGroup(self.arrowMenu)
        self.actGroup.setExclusive(True)
        self.actGroup.addAction(act1)
        self.actGroup.addAction(act2)
        self.actGroup.addAction(act3)
        self.actGroup.addAction(act4)

        self.sep1 = self.arrowMenu.addSeparator()
        self.arrowMenu.addAction(act1)
        self.arrowMenu.addAction(act2)
        self.arrowMenu.addAction(act3)
        self.arrowMenu.addAction(act4)
        self.sep2 = self.arrowMenu.addSeparator()
        self.menu.addMenu(self.arrowMenu)

        #.......................................................................
        # Alarms
        #.......................................................................
        # Alarms menu
        #s.alarmsMenu    = QMenu('Alarms')
        #s.alarmsMenu.addAction("Set",  s.setAlarmsPopup )
        #s.menu.addMenu(s.alarmsMenu)
        self.menubar.addMenu(self.menu)  # add menu to menubar

        dct = self.cfg.cfgD['sheye']
        self.shw.alarmDlg = alarmDialog.AlarmDialog('SH-EYE ALARMS', dct)
        self.connect(self.shw.alarmDlg, SIGNAL('ConfigChanged'),
                     self.configChangeHandler)
        self.menubar.addMenu(self.menu)

    #.............................................
    # Set Alarms menu popup
    #def setAlarmsPopup(s):
    #    qp = QWidget.mapToGlobal (s, QPoint(0,0)) # where to pop up
    #    s.shw.alarmDlg.popup(qp)  # popup at 0,0 of this widg

    #-----------------------------------------------------------------------
    def configChangeHandler(self):
        #print("<SHFrame>.configChangeHandler", s.name)
        dct = self.cfg.cfgD['sheye']
        # set eye alarms/enables
        self.shw.setAlarms(dct['alarmLow']['value' ], dct['alarmLow']['enable'], \
                        dct['alarmHi' ]['value' ], dct['alarmHi' ]['enable']  )
