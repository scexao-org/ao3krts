#===============================================================================
# File : DMLabelsFrame.py
#
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import sys
import Configuration
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QColor, QWidget, QFrame, QLabel, QStyleOption,
                         QGridLayout, QBoxLayout, QSizePolicy, QSplitter,
                         QHBoxLayout)
import util
import Constants as Kst
import nameValueColumn as nvc
import Configuration as cfg


#------------------------------------------------------------------------------
# DMLabelsFrame
#------------------------------------------------------------------------------
class DmLabelsFrame(QFrame):

    #.......................................................................
    def __init__(s, parent=None):
        super(DmLabelsFrame, s).__init__(parent)

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<DMLabels.__init__>")

        s.columns = []
        s.layout = QHBoxLayout(s)
        s.setFrameShape(QFrame.Box)
        s.setFrameShadow(QFrame.Sunken)
        s.setLineWidth(1)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

        s.columns.append( nvc.nameValueColumn( \
            ('dmDefocus','dmTiltX', 'dmTiltY', )))

        s.columns.append( nvc.nameValueColumn( \
            ('dmMin','dmMax','dmAvg') ))

        s.layout.addLayout(s.columns[0])
        s.layout.addLayout(s.columns[1])

    #.......................................................................
    def data_ready(s, data):
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in s.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# CrvLabelsFrame
#------------------------------------------------------------------------------
class CrvLabelsFrame(QFrame):

    #.......................................................................
    def __init__(s, parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<CrvLabels.__init__>")

        #............................................................
        super(CrvLabelsFrame, s).__init__(parent)
        s.columns = []
        s.layout = QHBoxLayout(s)
        s.columns.append( nvc.nameValueColumn( \
            ('crvDefocus', 'crvTiltX', 'crvTiltY',) ) )

        s.columns.append( nvc.nameValueColumn( \
            ('crvMin','crvMax','crvAvg') ))

        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)
        s.layout.addLayout(s.columns[0])
        s.layout.addLayout(s.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(s, data):
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<CRVLabels.data_ready>")
        for column in s.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# ApdLabelsFrame
#------------------------------------------------------------------------------
class ApdLabelsFrame(QFrame):

    #.......................................................................
    def __init__(s, parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<ApdLabels.__init__>")

        #............................................................
        super(ApdLabelsFrame, s).__init__(parent)
        s.columns = []
        s.layout = QHBoxLayout(s)

        #s.columns.append( nvc.nameValueColumn( \
        #    ('xxx', 'xxx',)) )

        #        s.columns.append( nvc.nameValueColumn( \
        #            ('apdMax','apdAvg','apdRmag') ))
        s.columns.append( nvc.nameValueColumn( \
            ('apdMax','apdAvg') ))

        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)
        s.layout.addLayout(s.columns[0])
        #s.layout.addLayout(s.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(s, data):
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in s.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
# ApdLabelsFrame
#------------------------------------------------------------------------------
class SHLabelsFrame(QFrame):

    #.......................................................................
    def __init__(s, parent=None):
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        if s.cfg.debug: print("<SHLabels.__init__>")

        #............................................................
        super(SHLabelsFrame, s).__init__(parent)
        s.columns = []
        s.layout = QHBoxLayout(s)

        s.columns.append( nvc.nameValueColumn( \
            ('shDefocus', 'shTiltX', 'shTiltY' )) )

        #        s.columns.append( nvc.nameValueColumn( \
        #            ('shAvg', 'shMax','shRmag',) ))

        s.columns.append( nvc.nameValueColumn( \
            ('shAvg', 'shMax') ))

        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Sunken)
        #s.setMidLineWidth(1)
        s.setLineWidth(1)
        s.layout.addLayout(s.columns[0])
        s.layout.addLayout(s.columns[1])

        # frame size
        #s.setMaximumWidth(340)
        s.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt

    #.......................................................................
    def data_ready(s, data):
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<DmLabels.data_ready>")
        for column in s.columns:
            column.updateData(data)


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class gainsLabelFrame(QFrame):

    def __init__(s, name="noname", parent=None, flags=Qt.WindowFlags()):
        super(gainsLabelFrame, s).__init__(parent, flags)

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        s.name = name
        s.wd = 400
        s.ht = 300

        # Set frame style
        s.setFrameStyle(QFrame.Box)
        s.setFrameShadow(QFrame.Raised)
        s.setLineWidth(1)

        # frame size
        s.setMinimumSize(s.wd, s.ht)
        s.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        #............................................................
        # make labeled columns
        # Single column entries require a comma
        s.columns = []

        s.topcol1 = nvc.nameValueColumn(('loopStatus', ))
        s.topcol2 = nvc.nameValueColumn(('GsMode', ))

        s.col2l = nvc.nameValueColumn(('dmgain', 'psbgain'))
        s.col2r = nvc.nameValueColumn(('ttgain', ))

        s.midcol1 = nvc.nameValueColumn(('httgain', 'lttgain', 'wttgain'))
        s.midcol2 = nvc.nameValueColumn(('hdfgain', 'ldfgain', 'adfgain'))
        #ADFGAIN
        s.botcol1 = nvc.nameValueColumn(('vmdrive', 'vmvolt'))
        s.botcol2 = nvc.nameValueColumn(('vmfreq', 'vmphase'))

        #............................................................
        s.columns.append(s.topcol1)
        s.columns.append(s.topcol2)

        s.columns.append(s.col2l)
        s.columns.append(s.col2r)

        s.columns.append(s.midcol1)
        s.columns.append(s.midcol2)

        s.columns.append(s.botcol1)
        s.columns.append(s.botcol2)

        #............................................................
        s.layout = QGridLayout(s)
        #s.layout.addStretch()

        cw = 5  # column width
        s.layout.addLayout(s.topcol1, 0, 0, 1, cw)
        s.layout.addLayout(s.topcol2, 0, cw + 1, 1, cw)

        s.layout.addLayout(s.col2l, 2, 0, 2, cw)
        s.layout.addLayout(s.col2r, 2, cw + 1, 2, cw)

        s.layout.addLayout(s.midcol1, 5, 0, 4, cw)
        s.layout.addLayout(s.midcol2, 5, cw + 1, 4, cw)

        s.layout.addLayout(s.botcol1, 8, 0, 2, cw)
        s.layout.addLayout(s.botcol2, 8, cw + 1, 2, cw)

    #............................................................
    def data_ready(s, data):
        if s.cfg.debug > Kst.DBGLEVEL_RATE2:
            print("<TtLabels.data_ready>")

        for column in s.columns:
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
