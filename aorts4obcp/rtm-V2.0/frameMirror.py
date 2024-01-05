#===============================================================================
# File : MirrorFrame.py
#
#
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

import sys
import configuration

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSlider, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
                             QSizePolicy, QSplitter, QMenuBar, QMenu)
import mirrorWidget
import labels
import constants as Kst
import alarmDialog


#-------------------------------------------------------------------------------
# MirrorFrame
#
#-------------------------------------------------------------------------------
class MirrorFrame(QFrame):

    def __init__(self, name="noname", parent=None):

        self.cfg = configuration.cfg
        self.lg = self.cfg.lg
        self.lg.debug("<MirrorFrame.__init__>:", name)

        #............................................................
        super(MirrorFrame, self).__init__(parent)
        self.name = name
        self.lg.debug("*    %s wd/ht>" % (name))
        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)
        #............................................................
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)  #hrz,vrt
        #............................................................
        self.layout = QVBoxLayout(parent)
        self.setLayout(self.layout)
        self.topLayout = QHBoxLayout(parent)
        self.midLayout = QHBoxLayout(parent)
        #............................................................
        self.lbl_title = QLabel(self.name)
        self.lbl_title.setSizePolicy(QSizePolicy.Fixed,
                                     QSizePolicy.Fixed)  #hrz,vrt
        #s.lbl_title.setMaximumHeight(16)
        #............................................................
        self.sld = None
        self.hzSplit00 = QSplitter(Qt.Horizontal)

        self.mrr = mirrorWidget.MirrorWidget(name)
        self.mrr.setWhatsThis(
                "LeftClick&Drag to set Contrast & Brightness. Double left click to select/unselect cell."
        )
        self.create_label_frame()
        self.createMenu()

        #............................................................
        self.topLayout.addWidget(self.lbl_title)
        self.topLayout.addWidget(self.hzSplit00)
        self.topLayout.addWidget(self.menubar)
        #s.topLayout.addWidget(s.menu)
        #.........
        if self.sld is not None:
            self.midLayout.addWidget(self.sld)
        else:
            self.midLayout.addSpacing(40)
        self.midLayout.addWidget(self.mrr)

        #.........
        self.layout.addLayout(self.topLayout)
        self.layout.addLayout(self.midLayout)
        self.layout.addWidget(self.labelsFrame)

        self.configChangeHandler(
        )  # force alarm values updata from current config

    #-----------------------------------------------------------------------
    def startRotateCount(self):
        self.mrr.startRotateCount()

    #-----------------------------------------------------------------------
    def displaySelectedCell(self):
        self.mrr.displaySelected = self.act_displaySelected.isChecked()
        self.mrr.repaint()

    #-----------------------------------------------------------------------
    def unselectCell(self):
        self.mrr.showCellNumber = False
        self.mrr.selectedCell = None
        self.mrr.selectedGuiCell = None
        self.mrr.repaint()

    #-----------------------------------------------------------------------
    def configChangeHandler(self):
        #print("<MirrorFrame.configChangeHandler>", s.name)
        if self.name == 'DM':
            dct = self.cfg.cfgD['dmeye']
        elif self.name == 'Curvature':
            dct = self.cfg.cfgD['crveye']
        elif self.name == 'HOWFS/APD':
            dct = self.cfg.cfgD['apdeye']

        else:
            self.lg.error(
                    "<MirrorFrame.configChangeHandler> ERROR:Unrecognized name:"
                    % self.name)
        # set eye alarms/enables
        self.mrr.setAlarms(dct['alarmLow']['value' ], dct['alarmLow']['enable'], \
                        dct['alarmHi' ]['value' ], dct['alarmHi' ]['enable']  )

    #------------------------------------------------------------------------
    # There are three possible frames: dm,crv,apd
    def create_label_frame(self):
        if self.name == 'DM':

            self.labelsFrame = labels.DmLabelsFrame(
            )  #create label/values frame
            self.mrr.ndxDataStart = Kst.DM_CELLDATASTART  #start of mirrorcell data
            self.mrr.ndxDataEnd = Kst.DM_CELLDATAEND  #end   of mirrorcell data

            # set labelled value offsets
            self.mrr.ndxMin = Kst.DM_CELLDATAMIN
            self.mrr.ndxMax = Kst.DM_CELLDATAMAX
            self.mrr.ndxVar = Kst.DM_CELLDATAVAR
            self.mrr.ndxAvg = Kst.DM_CELLDATAAVG
            self.mrr.ndxSafety = Kst.DMSAFETY
            self.defocusNdx = Kst.DM_DEFOCUS
            self.mrr.constantMin = Kst.DMMIN
            self.mrr.constantMax = Kst.DMMAX
            self.mrr.invertable = False  # do not invert mirror on gsmode change
            self.mrr.set_normalization_constants()
            self.create_defocus_indicator()  # create defocus slider on left

            dct = self.cfg.cfgD['dmeye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            self.mrr.alarmDlg = alarmDialog.AlarmDialog('DM-EYE ALARMS', dct,
                                                        self)

        elif self.name == 'Curvature':
            self.labelsFrame = labels.CrvLabelsFrame()

            # set start/end of mirrorcell data
            self.mrr.ndxDataStart = Kst.CRV_CELLDATASTART
            self.mrr.ndxDataEnd = Kst.CRV_CELLDATAEND

            # set labelled value offsets
            self.mrr.ndxMin = Kst.CRV_CELLDATAMIN
            self.mrr.ndxMax = Kst.CRV_CELLDATAMAX
            self.mrr.ndxVar = Kst.CRV_CELLDATAVAR
            self.mrr.ndxAvg = Kst.CRV_CELLDATAAVG
            self.mrr.ndxSafety = None
            self.defocusNdx = Kst.CRV_DEFOCUS
            self.mrr.constantMin = Kst.CRVMIN
            self.mrr.constantMax = Kst.CRVMAX
            self.mrr.invertable = True  # do invert mirror-map on gsmode change

            self.mrr.set_normalization_constants()
            self.create_defocus_indicator()
            dct = self.cfg.cfgD['crveye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            self.mrr.alarmDlg = alarmDialog.AlarmDialog('CRV-EYE ALARMS', dct,
                                                        self)

        elif self.name == 'HOWFS/APD':
            self.labelsFrame = labels.ApdLabelsFrame()

            # set start/end of mirrorcell data
            self.mrr.ndxDataStart = Kst.APD_CELLDATASTART
            self.mrr.ndxDataEnd = Kst.APD_CELLDATAEND

            # set labelled value offsets
            self.mrr.ndxMin = Kst.APD_CELLDATAMIN
            self.mrr.ndxMax = Kst.APD_CELLDATAMAX
            self.mrr.ndxVar = Kst.APD_CELLDATAVAR
            self.mrr.ndxAvg = Kst.APD_CELLDATAAVG
            self.mrr.ndxSafety = Kst.APDSAFETY
            self.defocusNdx = None
            self.mrr.constantMin = Kst.APDMIN
            self.mrr.constantMax = Kst.APDMAX

            self.mrr.invertable = True  # do invert mirror-map on gsmode change
            self.mrr.set_normalization_constants()
            dct = self.cfg.cfgD['apdeye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            self.mrr.alarmDlg = alarmDialog.AlarmDialog('APD-EYE ALARMS', dct,
                                                        self)

        else:
            self.lg.error(
                    "<frameMirror.creat_label_frame> Unrecognized name: %s" %
                    self.name)
            sys.exit()
        # notify on alarm edit
        self.mrr.alarmDlg.configChanged.connect(self.configChangeHandler)

    #------------------------------------------------------------------------
    # safety alarm
    def safetyFrame(self, state):
        if state:  # set red background if safety-state True
            #s.setStyleSheet('background-color:red')
            self.setStyleSheet('background-color:%s' % Kst.DESATRED)
        else:  # set normal background on not True safety-state
            self.setStyleSheet('background-color:%s' % Kst.LBLBKGCOLOR)

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

        # 'selection-color', 'selection-background-color'
        # 'alternate-background-color', 'border-color'
        # 'gridline-color', ''

        self.sld.setStyleSheet(fg + bg)
        #s.sld.setToolTip(QString("Defocus ToolTip"))
        self.sld.setWhatsThis("Defocus Indicator")
        self.sld.setToolTip("Defocus Indicator")

    #-----------------------------------------------------------------------
    def defocus_data_ready(self, data):

        if self.defocusNdx is None:
            return

        val = data[Kst.GENDATASTART + self.defocusNdx]
        if self.cfg.debug >= Kst.DBGLEVEL_RATE2:
            print(self.name, "defocus data:", val)

        # value rangecheck
        if val > 1.0:
            self.sld.setRange(0, val + val * 0.1)

        if val < -1.0:
            self.sld.setRange(val - val * 0.1, 0 + val * 0.1)
        else:
            self.sld.setRange(-0.1, 0.1)

        self.sld.setValue(val)

    #...........................................................................
    def setGreyCmap(self):
        self.mrr.set_colormap(1)

    #...........................................................................
    def setGreenCmap(self):
        self.mrr.set_colormap(3)

    #...........................................................................
    def createMenu(self):

        self.menubar = QMenuBar()
        self.menu = QMenu('Menu')

        # Colarmaps menu
        self.cmapMenu = QMenu('Colormaps')
        self.cmapMenu.addAction("Grey", self.setGreyCmap)
        self.cmapMenu.addAction("Green", self.setGreenCmap)
        self.menu.addMenu(self.cmapMenu)

        # Alarms menu
        #s.alarmsMenu    = QMenu('Alarms')
        #s.alarmsMenu.addAction("Set",  s.setAlarmsPopup )
        #s.menu.addMenu(s.alarmsMenu)
        self.menubar.addMenu(self.menu)  # add menu to menubar
