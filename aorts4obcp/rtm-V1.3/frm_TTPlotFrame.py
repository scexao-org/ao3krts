#===============================================================================
# File : Plotrame.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import Configuration

from PyQt4.QtCore import (Qt, QSize, QPoint)
from PyQt4.QtGui import (QColor,QWidget,QFrame,QLabel,QStyleOption,\
                         QVBoxLayout,QHBoxLayout,QSizePolicy,QSplitter,\
                         QMenuBar,QMenu,QAction,QPalette)
import ttplotWidget
import Constants as Kst
import AlarmDialogue


#------------------------------------------------------------------------------
# class TTPlotFrame
#------------------------------------------------------------------------------
class TTPlotFrame(QFrame):

    def __init__(s, name="noname", parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.lg.debug("<TTPlotFrame.__init__>:%s" % name)
        #............................................................
        super(TTPlotFrame, s).__init__(parent)
        s.name = name
        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)
        s.minwd = 400
        s.minht = 200

        #s.setMaximumSize(s.minwd,s.minht)

        #............................................................
        #s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) #hrz,vrt
        s.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        #............................................................
        s.leftlayout = QVBoxLayout()
        s.rightlayout = QVBoxLayout()
        s.layout = QHBoxLayout()
        s.setLayout(s.layout)
        #............................................................
        s.pwdg1_title = QLabel("    DM  Tiptilt Mount", s)
        s.pwdg1_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #h,v
        s.pwdg1_title.setMaximumHeight(10)

        s.pwdg2_title = QLabel("    WFS Tiptilt Mount", s)
        s.pwdg2_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #h,v
        s.pwdg2_title.setMaximumHeight(10)
        #............................................................
        #s.hzSplit00 = QSplitter(Qt.Horizontal)
        #............................................................

        s.pwdg1 = ttplotWidget.ttplotWidget(wd=150, ht=150, name='DmTt-Mount',
                                            axisTitle='Dm Tt-Mount',
                                            xtickrange=[-10.8, 10.8],
                                            ytickrange=[-10.4, 10.4])

        s.pwdg2 = ttplotWidget.ttplotWidget(wd=150, ht=150, name='wfsTtMount',
                                            axisTitle='wfs Tt-Mount',
                                            xtickrange=[-1.9, 10.8],
                                            ytickrange=[-1.9, 10.8])

        s.pwdg1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        s.pwdg2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set mouse-click handler
        # This will raise set-alarm popup for each widget on right click
        s.pwdg1.mouseReleaseEvent = s.wdg1MouseRelease
        s.pwdg2.mouseReleaseEvent = s.wdg2MouseRelease

        # set x,y alarm dictionaries for each plot-widget
        # the plotWidget will use this to check alarms
        s.pwdg1.MountXDct = s.cfg.cfgD['dmTtMountX']
        s.pwdg1.MountYDct = s.cfg.cfgD['dmTtMountY']
        s.pwdg2.MountXDct = s.cfg.cfgD['wfsTtMountX']
        s.pwdg2.MountYDct = s.cfg.cfgD['wfsTtMountY']

        # prefetch the data index for dm x,y, wfs x,y to save time
        s.dmXDataNdx = s.pwdg1.MountXDct['dataNdx']
        s.dmYDataNdx = s.pwdg1.MountYDct['dataNdx']
        s.wfXDataNdx = s.pwdg2.MountXDct['dataNdx']
        s.wfYDataNdx = s.pwdg2.MountYDct['dataNdx']

        # Create a set-alarm-popup for each widget. Popup on right-click
        s.pwdg1.xAlarmDlg=AlarmDialogue.AlarmDialog( \
            s.pwdg1.MountXDct['label'],  s.pwdg1.MountXDct, s)

        s.pwdg1.yAlarmDlg=AlarmDialogue.AlarmDialog( \
             s.pwdg1.MountYDct['label'], s.pwdg1.MountYDct, s)


        s.pwdg2.xAlarmDlg=AlarmDialogue.AlarmDialog( \
            s.pwdg2.MountXDct['label'],  s.pwdg2.MountXDct, s)

        s.pwdg2.yAlarmDlg=AlarmDialogue.AlarmDialog( \
             s.pwdg2.MountYDct['label'], s.pwdg1.MountYDct, s)

        #s.pwdg2.xAlarmDlg = AlarmDialogue.AlarmDialog('WFS-TT-MOUNT  X',
        #    s.cfg.cfgD['shTiltX'], s)
        #s.pwdg2.yAlarmDlg = AlarmDialogue.AlarmDialog('WFS-TT-MOUNT  Y',
        #    s.cfg.cfgD['shTiltY'], s)

        #s.pwdg2.setAxisLabelRotation(0,90)
        #s.pwdg1.resize(size, size)

        #............................................................
        # Menus
        #s.menubar = QMenuBar()
        #s.menu    = QMenu('Menu')
        #s.menu.addAction("Toggle Fake Data (1 Hz)", s.setFakeData)
        #s.menubar.addMenu(s.menu)
        #.......................................................................
        #s.topLayout.addWidget(s.pwdg1_title)
        #s.topLayout.addWidget(s.menubar)
        #s.midLayout.addWidget(s.pwdg1_title)
        #s.midLayout.addWidget(s.pwdg1)
        #s.midLayout.addWidget(s.pwdg2_title)
        #s.midLayout.addWidget(s.pwdg2)

        #s.layout.addLayout(s.topLayout)
        #s.layout.addLayout(s.midLayout)
        #s.layout.addLayout(s.labelsLayout)

        s.leftlayout.addWidget(s.pwdg1_title)
        s.leftlayout.addWidget(s.pwdg1)

        s.rightlayout.addWidget(s.pwdg2_title)
        s.rightlayout.addWidget(s.pwdg2)

        s.layout.addLayout(s.leftlayout)
        s.layout.addLayout(s.rightlayout)

    #...........................................................................
    #
    #...........................................................................
    def setFakeData(s):
        s.pwdg1.setFakeData()
        s.pwdg2.setFakeData()

    #def heightForWidth(s,w):
    #    return(w)
    #...........................................................................
    def sizeHint(s):
        return QSize(s.minwd, s.minht)

    #...........................................................................
    def minimumSizeHint(s):
        return QSize(s.minwd, s.minht)

    #...........................................................................
    def data_ready(s, data):
        genData = data[Kst.GENDATASTART:Kst.GENDATAEND]

        s.pwdg1.data_ready(genData[s.dmXDataNdx], genData[s.dmYDataNdx])
        s.pwdg2.data_ready(genData[s.wfXDataNdx], genData[s.wfYDataNdx])

        #s.pwdg1.data_ready(genData[Kst.DM_TTMOUNTX],genData[Kst.DM_TTMOUNTY])
        #s.pwdg2.data_ready(genData[Kst.WFS_TTCH1], genData[Kst.WFS_TTCH2])

    #...........................................................................
    def xyAlarmPopup(s, wdg):
        qp = QWidget.mapToGlobal(s, QPoint(30, 30))  # where to pop up
        wdg.xAlarmDlg.popup(qp)  # popup at 0,0 of this widg

        qp = QWidget.mapToGlobal(s, QPoint(30, 200 + 30))  # where to pop up
        wdg.yAlarmDlg.popup(qp)  # popup at 0,0 of this widg

    #...........................................................................
    def wdg1MouseRelease(s, ev):
        if ev.button() == Kst.RB:  # right mouse-button
            ev.accept()
            s.xyAlarmPopup(s.pwdg1)

        #if ev.button() == Kst.LB:
        #    s.colorAlarm()

    #...........................................................................
    def wdg2MouseRelease(s, ev):
        if ev.button() == Kst.RB:  # right mouse-button
            ev.accept()
            s.xyAlarmPopup(s.pwdg2)

    #def checkAlarm(s):
    #    bg     = " QWidget {background-color:%s}" % Kst.DESATRED
    #    s.pwdg1.setStyleSheet( bg )
