#===============================================================================
# File : DMLabelsFrame.py
#
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

import Configuration
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QFrame, QGridLayout, QSizePolicy, QHBoxLayout)

import Constants as Kst
import nameValueColumn as nvc


#------------------------------------------------------------------------------
# DMLabelsFrame
#------------------------------------------------------------------------------
class DmLabelsFrame(QFrame):

    #.......................................................................
    def __init__(self, parent=None):
        super(DmLabelsFrame, self).__init__(parent)

        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<DMLabels.__init__>")

        self.columns = []
        self.layout = QHBoxLayout(self)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

        self.columns.append( nvc.nameValueColumn( \
            ('dmDefocus','dmTiltX', 'dmTiltY', )))

        self.columns.append( nvc.nameValueColumn( \
            ('dmMin','dmMax','dmAvg') ))

        self.layout.addLayout(self.columns[0])
        self.layout.addLayout(self.columns[1])

    #.......................................................................
    def data_ready(self, data):
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in self.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# CrvLabelsFrame
#------------------------------------------------------------------------------
class CrvLabelsFrame(QFrame):

    #.......................................................................
    def __init__(self, parent=None):
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<CrvLabels.__init__>")

        #............................................................
        super(CrvLabelsFrame, self).__init__(parent)
        self.columns = []
        self.layout = QHBoxLayout(self)
        self.columns.append( nvc.nameValueColumn( \
            ('crvDefocus', 'crvTiltX', 'crvTiltY',) ) )

        self.columns.append( nvc.nameValueColumn( \
            ('crvMin','crvMax','crvAvg') ))

        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)
        self.layout.addLayout(self.columns[0])
        self.layout.addLayout(self.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(self, data):
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<CRVLabels.data_ready>")
        for column in self.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# ApdLabelsFrame
#------------------------------------------------------------------------------
class ApdLabelsFrame(QFrame):

    #.......................................................................
    def __init__(self, parent=None):
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<ApdLabels.__init__>")

        #............................................................
        super(ApdLabelsFrame, self).__init__(parent)
        self.columns = []
        self.layout = QHBoxLayout(self)

        #s.columns.append( nvc.nameValueColumn( \
        #    ('xxx', 'xxx',)) )

        #        s.columns.append( nvc.nameValueColumn( \
        #            ('apdMax','apdAvg','apdRmag') ))
        self.columns.append( nvc.nameValueColumn( \
            ('apdMax','apdAvg') ))

        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)
        self.layout.addLayout(self.columns[0])
        #s.layout.addLayout(s.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(self, data):
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in self.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# ApdLabelsFrame
#------------------------------------------------------------------------------
class SHLabelsFrame(QFrame):

    #.......................................................................
    def __init__(self, parent=None):
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        if self.cfg.debug: print("<SHLabels.__init__>")

        #............................................................
        super(SHLabelsFrame, self).__init__(parent)
        self.columns = []
        self.layout = QHBoxLayout(self)

        self.columns.append( nvc.nameValueColumn( \
            ('shDefocus', 'shTiltX', 'shTiltY' )) )

        #        s.columns.append( nvc.nameValueColumn( \
        #            ('shAvg', 'shMax','shRmag',) ))

        self.columns.append( nvc.nameValueColumn( \
            ('shAvg', 'shMax') ))

        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        self.setLineWidth(1)
        self.layout.addLayout(self.columns[0])
        self.layout.addLayout(self.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(self, data):
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in self.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class GainsLabelFrame(QFrame):

    def __init__(self, name="noname", parent=None, flags=Qt.WindowFlags()):
        super(GainsLabelFrame, self).__init__(parent, flags)

        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        self.name = name
        self.wd = 400
        self.ht = 300

        # Set frame style
        self.setFrameStyle(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)

        # frame size
        self.setMinimumSize(self.wd, self.ht)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        #............................................................
        # make labeled columns
        # Single column entries require a comma
        self.columns = []

        self.topcol1 = nvc.nameValueColumn(('loopStatus', ))
        self.topcol2 = nvc.nameValueColumn(('GsMode', ))

        self.col2l = nvc.nameValueColumn(('dmgain', 'psbgain'))
        self.col2r = nvc.nameValueColumn(('ttgain', ))

        self.midcol1 = nvc.nameValueColumn(('httgain', 'lttgain', 'wttgain'))
        self.midcol2 = nvc.nameValueColumn(('hdfgain', 'ldfgain', 'adfgain'))
        #ADFGAIN
        self.botcol1 = nvc.nameValueColumn(('vmdrive', 'vmvolt'))
        self.botcol2 = nvc.nameValueColumn(('vmfreq', 'vmphase'))

        #............................................................
        self.columns.append(self.topcol1)
        self.columns.append(self.topcol2)

        self.columns.append(self.col2l)
        self.columns.append(self.col2r)

        self.columns.append(self.midcol1)
        self.columns.append(self.midcol2)

        self.columns.append(self.botcol1)
        self.columns.append(self.botcol2)

        #............................................................
        self.layout = QGridLayout(self)
        #s.layout.addStretch()

        cw = 5  # column width
        self.layout.addLayout(self.topcol1, 0, 0, 1, cw)
        self.layout.addLayout(self.topcol2, 0, cw + 1, 1, cw)

        self.layout.addLayout(self.col2l, 2, 0, 2, cw)
        self.layout.addLayout(self.col2r, 2, cw + 1, 2, cw)

        self.layout.addLayout(self.midcol1, 5, 0, 4, cw)
        self.layout.addLayout(self.midcol2, 5, cw + 1, 4, cw)

        self.layout.addLayout(self.botcol1, 8, 0, 2, cw)
        self.layout.addLayout(self.botcol2, 8, cw + 1, 2, cw)

    #............................................................
    def data_ready(self, data):
        if self.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<TtLabels.data_ready>")

        for column in self.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def fixLabelStyle(lbf):

    for col in lbf.columns:
        for key in col.D.keys():
            lbl = col.D[key]['vlbl']
            item = col.D[key]
            col.setAlarmStyleHigh(lbl)
            col.setAlarmStyleNone(lbl)
