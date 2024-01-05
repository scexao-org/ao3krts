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
import Configuration

from PyQt4.QtCore import (Qt, SIGNAL, QString, QPoint)
from PyQt4.QtGui import (QColor,QWidget,QFrame,QLabel,QStyleOption, \
                        QGridLayout,QVBoxLayout,QHBoxLayout,QSizePolicy,\
                        QSplitter,QMenuBar,QMenu,QAction,QPalette,QSlider)
import MirrorWidget
import Labels
import Constants as Kst
import AlarmDialogue


#-------------------------------------------------------------------------------
# MirrorFrame
#
#-------------------------------------------------------------------------------
class MirrorFrame(QFrame):

    def __init__(s, name="noname", parent=None):

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.lg.debug("<MirrorFrame.__init__>:", name)

        #............................................................
        super(MirrorFrame, s).__init__(parent)
        s.name = name
        s.lg.debug("*    %s wd/ht>" % (name))
        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)
        #............................................................
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  #hrz,vrt
        #............................................................
        s.layout = QVBoxLayout(parent)
        s.setLayout(s.layout)
        s.topLayout = QHBoxLayout(parent)
        s.midLayout = QHBoxLayout(parent)
        #............................................................
        s.lbl_title = QLabel(s.name)
        s.lbl_title.setSizePolicy(QSizePolicy.Fixed,
                                  QSizePolicy.Fixed)  #hrz,vrt
        #s.lbl_title.setMaximumHeight(16)
        #............................................................
        s.sld = None
        s.hzSplit00 = QSplitter(Qt.Horizontal)

        s.mrr = MirrorWidget.MirrorWidget(name)
        s.mrr.setWhatsThis(
                QString("LeftClick&Drag to set Contrast & Brightness. Double left click to select/unselect cell."
                        ))
        s.create_label_frame()
        s.createMenu()

        #............................................................
        s.topLayout.addWidget(s.lbl_title)
        s.topLayout.addWidget(s.hzSplit00)
        s.topLayout.addWidget(s.menubar)
        #s.topLayout.addWidget(s.menu)
        #.........
        if s.sld is not None:
            s.midLayout.addWidget(s.sld)
        else:
            s.midLayout.addSpacing(40)
        s.midLayout.addWidget(s.mrr)

        #.........
        s.layout.addLayout(s.topLayout)
        s.layout.addLayout(s.midLayout)
        s.layout.addWidget(s.labelsFrame)

        s.configChangeHandler()  # force alarm values updata from current config

    #-----------------------------------------------------------------------
    def startRotateCount(s):
        s.mrr.startRotateCount()

    #-----------------------------------------------------------------------
    def displaySelectedCell(s):
        s.mrr.displaySelected = s.act_displaySelected.isChecked()
        s.mrr.repaint()

    #-----------------------------------------------------------------------
    def unselectCell(s):
        s.mrr.showCellNumber = False
        s.mrr.selectedCell = None
        s.mrr.selectedGuiCell = None
        s.mrr.repaint()

    #-----------------------------------------------------------------------
    def configChangeHandler(s):
        #print("<MirrorFrame.configChangeHandler>", s.name)
        if s.name == 'DM':
            dct = s.cfg.cfgD['dmeye']
        elif s.name == 'Curvature':
            dct = s.cfg.cfgD['crveye']
        elif s.name == 'HOWFS/APD':
            dct = s.cfg.cfgD['apdeye']

        else:
            s.lg.error(
                    "<MirrorFrame.configChangeHandler> ERROR:Unrecognized name:"
                    % s.name)
        # set eye alarms/enables
        s.mrr.setAlarms(dct['alarmLow']['value' ], dct['alarmLow']['enable'], \
                        dct['alarmHi' ]['value' ], dct['alarmHi' ]['enable']  )

    #------------------------------------------------------------------------
    # There are three possible frames: dm,crv,apd
    def create_label_frame(s):
        if s.name == 'DM':

            s.labelsFrame = Labels.DmLabelsFrame()  #create label/values frame
            s.mrr.ndxDataStart = Kst.DM_CELLDATASTART  #start of mirrorcell data
            s.mrr.ndxDataEnd = Kst.DM_CELLDATAEND  #end   of mirrorcell data

            # set labelled value offsets
            s.mrr.ndxMin = Kst.DM_CELLDATAMIN
            s.mrr.ndxMax = Kst.DM_CELLDATAMAX
            s.mrr.ndxVar = Kst.DM_CELLDATAVAR
            s.mrr.ndxAvg = Kst.DM_CELLDATAAVG
            s.mrr.ndxSafety = Kst.DMSAFETY
            s.defocusNdx = Kst.DM_DEFOCUS
            s.mrr.constantMin = Kst.DMMIN
            s.mrr.constantMax = Kst.DMMAX
            s.mrr.invertable = False  # do not invert mirror on gsmode change
            s.mrr.set_normalization_constants()
            s.create_defocus_indicator()  # create defocus slider on left

            dct = s.cfg.cfgD['dmeye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            s.mrr.alarmDlg = AlarmDialogue.AlarmDialog('DM-EYE ALARMS', dct, s)

        elif s.name == 'Curvature':
            s.labelsFrame = Labels.CrvLabelsFrame()

            # set start/end of mirrorcell data
            s.mrr.ndxDataStart = Kst.CRV_CELLDATASTART
            s.mrr.ndxDataEnd = Kst.CRV_CELLDATAEND

            # set labelled value offsets
            s.mrr.ndxMin = Kst.CRV_CELLDATAMIN
            s.mrr.ndxMax = Kst.CRV_CELLDATAMAX
            s.mrr.ndxVar = Kst.CRV_CELLDATAVAR
            s.mrr.ndxAvg = Kst.CRV_CELLDATAAVG
            s.mrr.ndxSafety = None
            s.defocusNdx = Kst.CRV_DEFOCUS
            s.mrr.constantMin = Kst.CRVMIN
            s.mrr.constantMax = Kst.CRVMAX
            s.mrr.invertable = True  # do invert mirror-map on gsmode change

            s.mrr.set_normalization_constants()
            s.create_defocus_indicator()
            dct = s.cfg.cfgD['crveye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            s.mrr.alarmDlg = AlarmDialogue.AlarmDialog('CRV-EYE ALARMS', dct, s)

        elif s.name == 'HOWFS/APD':
            s.labelsFrame = Labels.ApdLabelsFrame()

            # set start/end of mirrorcell data
            s.mrr.ndxDataStart = Kst.APD_CELLDATASTART
            s.mrr.ndxDataEnd = Kst.APD_CELLDATAEND

            # set labelled value offsets
            s.mrr.ndxMin = Kst.APD_CELLDATAMIN
            s.mrr.ndxMax = Kst.APD_CELLDATAMAX
            s.mrr.ndxVar = Kst.APD_CELLDATAVAR
            s.mrr.ndxAvg = Kst.APD_CELLDATAAVG
            s.mrr.ndxSafety = Kst.APDSAFETY
            s.defocusNdx = None
            s.mrr.constantMin = Kst.APDMIN
            s.mrr.constantMax = Kst.APDMAX

            s.mrr.invertable = True  # do invert mirror-map on gsmode change
            s.mrr.set_normalization_constants()
            dct = s.cfg.cfgD['apdeye']  # set values dict for this frame

            # create popup alarm dialog for mirrorMap widget
            s.mrr.alarmDlg = AlarmDialogue.AlarmDialog('APD-EYE ALARMS', dct, s)

        else:
            s.lg.error(
                    "<frm_MirrorFrame.creat_label_frame> Unrecognized name: %s"
                    % s.name)
            sys.exit()
        # notify on alarm edit
        s.connect(s.mrr.alarmDlg, SIGNAL('ConfigChanged'),
                  s.configChangeHandler)

    #------------------------------------------------------------------------
    # safety alarm
    def safetyFrame(s, state):
        if state:  # set red background if safety-state True
            #s.setStyleSheet('background-color:red')
            s.setStyleSheet('background-color:%s' % Kst.DESATRED)
        else:  # set normal background on not True safety-state
            s.setStyleSheet('background-color:%s' % Kst.LBLBKGCOLOR)

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

        # 'selection-color', 'selection-background-color'
        # 'alternate-background-color', 'border-color'
        # 'gridline-color', ''

        s.sld.setStyleSheet(fg + bg)
        #s.sld.setToolTip(QString("Defocus ToolTip"))
        s.sld.setWhatsThis(QString("Defocus Indicator"))
        s.sld.setToolTip(QString("Defocus Indicator"))

    #-----------------------------------------------------------------------
    def defocus_data_ready(s, data):

        if s.defocusNdx is None:
            return

        val = data[Kst.GENDATASTART + s.defocusNdx]
        if s.cfg.debug >= Kst.DBGLEVEL_RATE2:
            print(s.name, "defocus data:", val)

        # value rangecheck
        if val > 1.0:
            s.sld.setRange(0, val + val * 0.1)

        if val < -1.0:
            s.sld.setRange(val - val * 0.1, 0 + val * 0.1)
        else:
            s.sld.setRange(-0.1, 0.1)

        s.sld.setValue(val)

    #...........................................................................
    def setGreyCmap(s):
        s.mrr.set_colormap(1)

    #...........................................................................
    def setGreenCmap(s):
        s.mrr.set_colormap(3)

    #...........................................................................
    def createMenu(s):

        s.menubar = QMenuBar()
        s.menu = QMenu('Menu')

        # Colarmaps menu
        s.cmapMenu = QMenu('Colormaps')
        s.cmapMenu.addAction("Grey", s.setGreyCmap)
        s.cmapMenu.addAction("Green", s.setGreenCmap)
        s.menu.addMenu(s.cmapMenu)

        # Alarms menu
        #s.alarmsMenu    = QMenu('Alarms')
        #s.alarmsMenu.addAction("Set",  s.setAlarmsPopup )
        #s.menu.addMenu(s.alarmsMenu)
        s.menubar.addMenu(s.menu)  # add menu to menubar

    #-----------------------------------------------------------------------
    # Event.button values are Left-button:1 Middle button: 4, right button:2
    #def mouseDoubleClickEvent(s,event):


#    def mouseReleaseEvent(s,event):
#        print("FRAME RELEASE EVENT")
#        button = event.button()
#        if button == 1:   # left button: 1
#            return
#        elif button == 4: # middle button is 4
#            return
#        elif button == 2: # right button is 2
#            pass
#
#        # get x,y for set-alarm-poup
#        qp = s.mapToGlobal (QPoint(0,0))
#        #print("XY:", s.x(), s.y())
#        y = qp.y() + 20
#        qp.setY(y)
#        x = qp.x() - 40
#        qp.setX(x)
#
#        s.setAlarmsPopup()
#        #s.clickAction(qp)   # act as instructed
#
#        event.accept()

# buttons: L:1 M:4 R:2
# Event.button values are Left-button:1 Middle button: 4, right button:2
#def mouseDoubleClickEvent(s, ev):
#def mouseReleaseEvent(s,event):
#    button = ev.button()
#    #x = ev.posF().x()
#    #y = ev.posF().y()
#    #ratio = s.logicalSize / s.width()
#    #x1 = x * ratio
#    #y1 = y * ratio
#
#    if button == 1:   # left button: 1
#        print("LB")
#    elif button == 4: # middle button is 4
#        print("MB")
#    elif button == 2: # right button is 2
#        print("RB")

#s.menubar.setPalette(QPalette(QColor ( 160 , 176, 201 )));
#s.menubar.setStyleSheet('background-color:%s'%Kst.LBLBKGCOLOR)
#s.menubar.setStyleSheet('color:%s'%Kst.LBLBKGCOLOR)
#fg     = " QLabel {color:red}"
#bg     = " QLabel {background-color:%s}" % Kst.LBLBKGCOLOR
#bg     = " QLabel {background-color:blue}"
#border = " QLabel {border-color:%s}" % '#000000'
#s.menubar.setStyleSheet('background-color:red')
#s.menu.setStyleSheet('background-color:%s'%Kst.LBLBKGCOLOR)
#s.act_displaySelected = s.menu.addAction("Display Selected Cell",
#                                          s.displaySelectedCell)
#s.act_displaySelected.setCheckable(True)
#s.act_unselectCell = s.menu.addAction("Unselect Cell",
#                                          s.unselectCell)
#s.menu.addAction("Count", s.startRotateCount)
#............................................................

# Create set-alarms popup
# Pass name and alarm parameters dictionary

#geom = s.frameGeometry()
#print("GEOM", geom)
