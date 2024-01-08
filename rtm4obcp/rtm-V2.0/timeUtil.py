#!/usr/bin/python
#===============================================================================
# File : QtTimes.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
from PyQt5.QtCore import (Qt, QDateTime, QTime)

import constants as Kst


# convert our timezone-strings to Qt timezone code
# Recognized codes are 'UTC' else time is localtime
def zoneToSpec(zone):
    if zone == Kst.TZONE_UTC:
        #print("UTC  :", Qt.UTC)
        return (Qt.UTC)
    else:
        #print("LOC  :", Qt.LocalTime)
        return (Qt.LocalTime)


def prnTimeSpec(timeSpec):
    if timeSpec == Kst.TZONE_UTC:
        QtZone = Qt.UTC
        ZoneStr = 'UTC'
    else:
        QtZone = Qt.LocalTime
        ZoneStr = 'LOC'

    print(ZoneStr, ':', QtZone)
    return ZoneStr


def prnTime(qdt):
    timeSpec = qdt.timeSpec()
    if timeSpec == Qt.UTC:
        timespecStr = 'UTC'
    else:
        timespecStr = 'LOCAL TIME'
    print("DateTime:", qdt.toString('yyyy MM dd hh:mm:ss'),
          prnTimeSpec(timeSpec))


def setTime(when='now', timeSpec=Qt.LocalTime):

    if when == 'now' and timeSpec == Qt.LocalTime:
        return (QDateTime().currentDateTime())

    elif when == 'now' and timeSpec == UTC:
        return (QDateTime().currentDateTimeUTC())

    # assume when is a QDateTime instance
    else:
        return QDateTime(when)


#...........................................................................
def setTimeI(qdt, h, m, s):
    time = QTime()
    time.setHMS(h, m, s)
    qdt.setTime(time)
