#===============================================================================
# File : ClickableLabel.py
#      :
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

from PyQt4.QtCore import QPoint
from PyQt4.QtGui import QLabel


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class ClickableLabel(QLabel):

    def __init__(s, parent=None):

        super(ClickableLabel, s).__init__(parent)

        # To be set by caller
        # What to do on mouse click over this label
        s.clickAction = None

    def setClickAction(s, action):
        s.clickAction = action

    # perform click-Action on mouse release over label
    # Event.button values are Left-button:1 Middle button: 4, right button:2
    #def mouseDoubleClickEvent(s,event):
    def mouseReleaseEvent(s, event):

        button = event.button()

        if button == 1:  # left button: 1
            return
        elif button == 4:  # middle button is 4
            return
        elif button == 2:  # right button is 2
            event.accept()

        if s.clickAction is not None:
            qp = s.mapToGlobal(QPoint(0, 0))
            y = qp.y() + 20
            qp.setY(y)

            x = qp.x() - 40
            qp.setX(x)

            s.clickAction(qp)  # act as instructed

    #----------------------------------------------------------------------
    #def wheelEvent (s, we):
    #
    #print("< %s wheelEvent >" % s.name )
    #    delta = we.delta() # foreward:128 backware:-128
    #    s.wheelVal       = we.delta()/s.wheelIncr
    #    s.wheelAccumVal += s.wheelVal
    #    #s.qhevent = QHelpEvent(QEvent.WhatsThis)
    #    #print("Delta:",we.delta(),"Val:",s.wheelVal,"Accum:",s.wheelAccumVal)
    #   # QWheelEvent.accept()
