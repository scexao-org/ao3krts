#===============================================================================
# File : Plotrame.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import Configuration

from PyQt4.QtCore import (Qt, QSize, QPoint)
from PyQt4.QtGui import (QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
                         QSizePolicy)
import ttplotWidget
import Constants as Kst
import AlarmDialogue


#------------------------------------------------------------------------------
# class TTPlotFrame
#------------------------------------------------------------------------------
class TTPlotFrame(QFrame):

    def __init__(self, name="noname", parent=None):
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        self.lg.debug("<TTPlotFrame.__init__>:%s" % name)
        #............................................................
        super(TTPlotFrame, self).__init__(parent)
        self.name = name
        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)
        self.minwd = 400
        self.minht = 200

        #s.setMaximumSize(s.minwd,s.minht)

        #............................................................
        #s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) #hrz,vrt
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        #............................................................
        self.leftlayout = QVBoxLayout()
        self.rightlayout = QVBoxLayout()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        #............................................................
        self.pwdg1_title = QLabel("    DM  Tiptilt Mount", self)
        self.pwdg1_title.setSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Fixed)  #h,v
        self.pwdg1_title.setMaximumHeight(10)

        self.pwdg2_title = QLabel("    WFS Tiptilt Mount", self)
        self.pwdg2_title.setSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Fixed)  #h,v
        self.pwdg2_title.setMaximumHeight(10)
        #............................................................
        #s.hzSplit00 = QSplitter(Qt.Horizontal)
        #............................................................

        self.pwdg1 = ttplotWidget.TTplotWidget(wd=150, ht=150,
                                               name='DmTt-Mount',
                                               axisTitle='Dm Tt-Mount',
                                               xtickrange=[-10.8, 10.8],
                                               ytickrange=[-10.4, 10.4])

        self.pwdg2 = ttplotWidget.TTplotWidget(wd=150, ht=150,
                                               name='wfsTtMount',
                                               axisTitle='wfs Tt-Mount',
                                               xtickrange=[-1.9, 10.8],
                                               ytickrange=[-1.9, 10.8])

        self.pwdg1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pwdg2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set mouse-click handler
        # This will raise set-alarm popup for each widget on right click
        self.pwdg1.mouseReleaseEvent = self.wdg1MouseRelease
        self.pwdg2.mouseReleaseEvent = self.wdg2MouseRelease

        # set x,y alarm dictionaries for each plot-widget
        # the plotWidget will use this to check alarms
        self.pwdg1.MountXDct = self.cfg.cfgD['dmTtMountX']
        self.pwdg1.MountYDct = self.cfg.cfgD['dmTtMountY']
        self.pwdg2.MountXDct = self.cfg.cfgD['wfsTtMountX']
        self.pwdg2.MountYDct = self.cfg.cfgD['wfsTtMountY']

        # prefetch the data index for dm x,y, wfs x,y to save time
        self.dmXDataNdx = self.pwdg1.MountXDct['dataNdx']
        self.dmYDataNdx = self.pwdg1.MountYDct['dataNdx']
        self.wfXDataNdx = self.pwdg2.MountXDct['dataNdx']
        self.wfYDataNdx = self.pwdg2.MountYDct['dataNdx']

        # Create a set-alarm-popup for each widget. Popup on right-click
        self.pwdg1.xAlarmDlg=AlarmDialogue.AlarmDialog( \
            self.pwdg1.MountXDct['label'],  self.pwdg1.MountXDct, self)

        self.pwdg1.yAlarmDlg=AlarmDialogue.AlarmDialog( \
             self.pwdg1.MountYDct['label'], self.pwdg1.MountYDct, self)


        self.pwdg2.xAlarmDlg=AlarmDialogue.AlarmDialog( \
            self.pwdg2.MountXDct['label'],  self.pwdg2.MountXDct, self)

        self.pwdg2.yAlarmDlg=AlarmDialogue.AlarmDialog( \
             self.pwdg2.MountYDct['label'], self.pwdg1.MountYDct, self)

        self.leftlayout.addWidget(self.pwdg1_title)
        self.leftlayout.addWidget(self.pwdg1)

        self.rightlayout.addWidget(self.pwdg2_title)
        self.rightlayout.addWidget(self.pwdg2)

        self.layout.addLayout(self.leftlayout)
        self.layout.addLayout(self.rightlayout)

    #...........................................................................
    #
    #...........................................................................
    def setFakeData(self):
        self.pwdg1.setFakeData()
        self.pwdg2.setFakeData()

    #def heightForWidth(s,w):
    #    return(w)
    #...........................................................................
    def sizeHint(self):
        return QSize(self.minwd, self.minht)

    #...........................................................................
    def minimumSizeHint(self):
        return QSize(self.minwd, self.minht)

    #...........................................................................
    def data_ready(self, data):
        genData = data[Kst.GENDATASTART:Kst.GENDATAEND]

        self.pwdg1.data_ready(genData[self.dmXDataNdx],
                              genData[self.dmYDataNdx])
        self.pwdg2.data_ready(genData[self.wfXDataNdx],
                              genData[self.wfYDataNdx])

        #s.pwdg1.data_ready(genData[Kst.DM_TTMOUNTX],genData[Kst.DM_TTMOUNTY])
        #s.pwdg2.data_ready(genData[Kst.WFS_TTCH1], genData[Kst.WFS_TTCH2])

    #...........................................................................
    def xyAlarmPopup(self, wdg):
        qp = QWidget.mapToGlobal(self, QPoint(30, 30))  # where to pop up
        wdg.xAlarmDlg.popup(qp)  # popup at 0,0 of this widg

        qp = QWidget.mapToGlobal(self, QPoint(30, 200 + 30))  # where to pop up
        wdg.yAlarmDlg.popup(qp)  # popup at 0,0 of this widg

    #...........................................................................
    def wdg1MouseRelease(self, ev):
        if ev.button() == Kst.RB:  # right mouse-button
            ev.accept()
            self.xyAlarmPopup(self.pwdg1)

        #if ev.button() == Kst.LB:
        #    s.colorAlarm()

    #...........................................................................
    def wdg2MouseRelease(self, ev):
        if ev.button() == Kst.RB:  # right mouse-button
            ev.accept()
            self.xyAlarmPopup(self.pwdg2)
