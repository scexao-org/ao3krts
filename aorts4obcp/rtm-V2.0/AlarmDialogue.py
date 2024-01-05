#===============================================================================
# File : AlarmDialog.py
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QDialog, QDoubleSpinBox, QPushButton,
                             QGridLayout, QHBoxLayout, QCheckBox, QFrame)

import Constants as Kst


#-------------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------------
class AlarmDialog(QDialog):

    def __init__(s, alarmName, dct, parent=None):

        super(AlarmDialog, s).__init__(parent,
                                       Qt.Dialog | Qt.FramelessWindowHint)

        s.alarmName = "%s" % alarmName  # set name
        s.dct = dct  # set parameters dictionary

        # set popup-window bkg color
        s.setStyleSheet("QDialog{ background-color: %s }" %
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
        s.setLblStyle(hAlarmLbl)
        s.setLblStyle(lAlarmLbl)

        # Create alarm-enable checkboxes
        s.hAlarmEnableCheckbox = QCheckBox("Enable")  # create checkbox
        s.lAlarmEnableCheckbox = QCheckBox("Enable")  # create checkbox

        # Spinboxes
        s.hAlarmSbx = QDoubleSpinBox()  # create double spinbox
        s.lAlarmSbx = QDoubleSpinBox()  # create double spinbox
        s.hAlarmSbx.setDecimals(3)
        s.lAlarmSbx.setDecimals(3)
        s.hAlarmSbx.setRange(-9999.0,
                             9999.0)  # min/max high-alarm spinbox value
        s.lAlarmSbx.setRange(-9999.0,
                             9999.0)  # min/max low-alarm  spinbox value
        le = s.hAlarmSbx.lineEdit()
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
        layout.addWidget(s.hAlarmSbx, 2, 0, 1, 2)
        layout.addWidget(s.hAlarmEnableCheckbox, 2, 2)

        layout.addWidget(lAlarmLbl, 4, 0)
        layout.addWidget(s.lAlarmSbx, 5, 0, 1, 2)
        layout.addWidget(s.lAlarmEnableCheckbox, 5, 2)
        layout.addLayout(buttonLayout, 7, 0, 1, 3)

        s.setLayout(layout)

        # Wire Ok/Cancel buttons to handlers
        # These would also work using builtin slots, 'accept'  & 'reject'
        s.connect(okButton, SIGNAL('clicked()'), s.ok)
        s.connect(cancelButton, SIGNAL('clicked()'), s, SLOT("reject()"))

    #...........................................................................
    def popup(s, qp):
        s.setDictValues()  # apply new values every time
        s.move(qp.x(), qp.y())
        s.show()

    def setLblStyle(s, lbl):
        fg = " QLabel {color:%s}" % Kst.LBLFGCOLOR
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'
        lbl.setStyleSheet(fg + bg + border)

    #...........................................................................
    # get new alarm&enable values from dict
    # checkbox signals stateChanged when box checked/unchecked
    #...........................................................................
    def setDictValues(s):
        s.hAlarmSbx.setValue(s.dct['alarmHi']['value'])
        s.lAlarmSbx.setValue(s.dct['alarmLow']['value'])

        # Set High alarm enable checkbox
        if s.dct['alarmHi']['enable']:
            s.hAlarmEnableCheckbox.setCheckState(Qt.Checked)
        else:
            s.hAlarmEnableCheckbox.setCheckState(Qt.Unchecked)

        # Low alarm enable enable checkbox
        if s.dct['alarmLow']['enable']:
            s.lAlarmEnableCheckbox.setCheckState(Qt.Checked)
        else:
            s.lAlarmEnableCheckbox.setCheckState(Qt.Unchecked)

    #...........................................................................
    # Ok button handler: get values to dict
    #...........................................................................
    def ok(s):
        s.dct['alarmHi']['value'] = s.hAlarmSbx.value()
        s.dct['alarmHi']['enable'] = s.hAlarmEnableCheckbox.isChecked()
        s.dct['alarmLow']['value'] = s.lAlarmSbx.value()
        s.dct['alarmLow']['enable'] = s.lAlarmEnableCheckbox.isChecked()
        s.emit(SIGNAL('ConfigChanged'))

        s.accept()  # dismiss dialogue w. QDialog.accept()

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
