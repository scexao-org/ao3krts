#!/usr/bin/python

from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.pyqtconfig import Configuration

cfg = Configuration()

print("Qt version  :", QT_VERSION_STR)
print("SIP version :", cfg.sip_version_str)
print("PyQt version:", cfg.pyqt_version_str)
