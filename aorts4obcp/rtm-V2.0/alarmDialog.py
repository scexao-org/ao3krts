#===============================================================================
# File : AlarmDialog.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QDialog, QDoubleSpinBox, QPushButton,
                             QGridLayout, QHBoxLayout, QCheckBox, QFrame)

import constants as Kst


#-------------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------------
class AlarmDialog(QDialog):

    # Custom signal
    configChanged = QtCore.pyqtSignal()

    def __init__(self, alarmName, dct, parent=None):

        super(AlarmDialog, self).__init__(parent,
                                          Qt.Dialog | Qt.FramelessWindowHint)

        self.alarmName = "%s" % alarmName  # set name
        self.dct = dct  # set parameters dictionary

        # set popup-window bkg color
        self.setStyleSheet("QDialog{ background-color: %s }" %
                           Kst.SETALARMPOPUPBKG)

        # Create boxed alarm-name-label
        alarmNameLbl = QLabel(alarmName)
        alarmNameLbl.setFrameStyle(QFrame.Box)
        alarmNameLbl.setMinimumWidth(200)
        alarmNameLbl.setAlignment(Qt.AlignCenter)

        fg = " QLabel {color:%s}" % '#000000'
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'
        alarmNameLbl.setStyleSheet(fg + bg + border)

        #alarmNameLbl.setFrameShadow(QFrame.Raised)
        #s.setMidLineWidth(1)

        # Create high & low alarm labels
        hAlarmLbl = QLabel('High Alarm')  # create high alarm tag
        lAlarmLbl = QLabel('Low Alarm')  # create low  alarm tag
        #s.setLblStyle(alarmNameLbl)
        self.setLblStyle(hAlarmLbl)
        self.setLblStyle(lAlarmLbl)

        # Create alarm-enable checkboxes
        self.hAlarmEnableCheckbox = QCheckBox("Enable")  # create checkbox
        self.lAlarmEnableCheckbox = QCheckBox("Enable")  # create checkbox

        # Spinboxes
        self.hAlarmSbx = QDoubleSpinBox()  # create double spinbox
        self.lAlarmSbx = QDoubleSpinBox()  # create double spinbox
        self.hAlarmSbx.setDecimals(3)
        self.lAlarmSbx.setDecimals(3)
        self.hAlarmSbx.setRange(-9999.0,
                                9999.0)  # min/max high-alarm spinbox value
        self.lAlarmSbx.setRange(-9999.0,
                                9999.0)  # min/max low-alarm  spinbox value
        le = self.hAlarmSbx.lineEdit()
        le.setFocusPolicy(Qt.StrongFocus)

        # Buttons:  OK, Cancel
        okButton = QPushButton('OK')  # create OK button
        cancelButton = QPushButton('Cancel')  # create Cancel buttons

        # Layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout = QGridLayout()

        #----------------------------
        layout.addWidget(alarmNameLbl, 0, 0, 1, 8)
        layout.addWidget(hAlarmLbl, 1, 0)
        layout.addWidget(self.hAlarmSbx, 2, 0, 1, 2)
        layout.addWidget(self.hAlarmEnableCheckbox, 2, 2)

        layout.addWidget(lAlarmLbl, 4, 0)
        layout.addWidget(self.lAlarmSbx, 5, 0, 1, 2)
        layout.addWidget(self.lAlarmEnableCheckbox, 5, 2)
        layout.addLayout(buttonLayout, 7, 0, 1, 3)

        self.setLayout(layout)

        # Wire Ok/Cancel buttons to handlers
        okButton.clicked.connect(self.ok)
        cancelButton.clicked.connect(self.reject)

    #...........................................................................
    def popup(self, qp):
        self.setDictValues()  # apply new values every time
        self.move(qp.x(), qp.y())
        self.show()

    def setLblStyle(self, lbl):
        fg = " QLabel {color:%s}" % Kst.LBLFGCOLOR
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'
        lbl.setStyleSheet(fg + bg + border)

    #...........................................................................
    # get new alarm&enable values from dict
    # checkbox signals stateChanged when box checked/unchecked
    #...........................................................................
    def setDictValues(self):
        self.hAlarmSbx.setValue(self.dct['alarmHi']['value'])
        self.lAlarmSbx.setValue(self.dct['alarmLow']['value'])

        # Set High alarm enable checkbox
        if self.dct['alarmHi']['enable']:
            self.hAlarmEnableCheckbox.setCheckState(Qt.Checked)
        else:
            self.hAlarmEnableCheckbox.setCheckState(Qt.Unchecked)

        # Low alarm enable enable checkbox
        if self.dct['alarmLow']['enable']:
            self.lAlarmEnableCheckbox.setCheckState(Qt.Checked)
        else:
            self.lAlarmEnableCheckbox.setCheckState(Qt.Unchecked)

    #...........................................................................
    # Ok button handler: get values to dict
    #...........................................................................
    def ok(self):
        self.dct['alarmHi']['value'] = self.hAlarmSbx.value()
        self.dct['alarmHi']['enable'] = self.hAlarmEnableCheckbox.isChecked()
        self.dct['alarmLow']['value'] = self.lAlarmSbx.value()
        self.dct['alarmLow']['enable'] = self.lAlarmEnableCheckbox.isChecked()

        from PyQt5 import QtCore

        self.configChanged.emit()

        self.accept()  # dismiss dialogue w. QDialog.accept()

    #----------------------------------------------------------------------
    #def wheelEvent (s, we):
    #
    #print("< %s wheelEvent >" % s.alarmNameLbl )
    #    delta = we.delta() # foreward:128 backware:-128
    #    s.wheelVal       = we.delta()/s.wheelIncr
    #    s.wheelAccumVal += s.wheelVal
    #    #s.qhevent = QHelpEvent(QEvent.WhatsThis)
    #    #print("Delta:",we.delta(),"Val:",s.wheelVal,"Accum:",s.wheelAccumVal)
    #   # QWheelEvent.accept()

    #def closeEvent(s):
    #    print("CLOSE")

    # Set title of popup dialog = name
    #s.setWindowTitle(QString(title))
    #s.setWindowTitle(QString(''))

    # Qt.TextSelectableByKeyboard  Qt.TextEditable Qt.ImhDigitSOnly
    # Qt.ItemIsEditable 	Qt.ItemIsEnabled
    #le.setInputMethodHints(Qt.TextEditable)
    # ao188 problem: le.setInputMethodHints(Qt.ImhDigitsOnly)
    #le.setWindowRole(QString(Qt.EditRole))
    #le.setInputContext()
    #le.setInputMethodHints()
