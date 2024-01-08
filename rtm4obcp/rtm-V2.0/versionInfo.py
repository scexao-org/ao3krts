#!/usr/bin/python

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.Qt import sip_version_str

print("Qt version  :", QT_VERSION_STR)
print("SIP version :", sip_version_str)
print("PyQt version:", PYQT_VERSION_STR)
