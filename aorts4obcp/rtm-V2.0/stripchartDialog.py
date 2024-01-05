#===============================================================================
# File : stripchartDialog.py
#
# Notes:
# http://qt-project.org/doc/qt-4.8/qdatetime.html
#===============================================================================
from __future__ import (absolute_import, print_function, division)

import PyQt5
from PyQt5.QtCore import (Qt, QRect)
from PyQt5.QtWidgets import (QLabel, QDialog, QDoubleSpinBox, QPushButton,
                             QGridLayout, QHBoxLayout, QFrame, QButtonGroup,
                             QRadioButton, QFrame)
import constants as Kst


#-------------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------------
class stripchartDialog(QDialog):

    def __init__(self, titleStr, pDct, parent=None):

        super(stripchartDialog,
              self).__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.pwdg = parent
        self.pDct = pDct  # stripchart parameters dictionary
        self.id = self.pDct['Id']
        self.scaleMaxv = self.pDct['fixedScaleMax']['value']
        self.scaleMinv = self.pDct['fixedScaleMin']['value']
        self.spinnerStep = 1.0
        #s.scaleWheelMin = s.pDct['scaleWheelMin']['value']
        #s.scaleWheelMax = s.pDct['scaleWheelMax']['value']

        # set popup bkg color
        self.setStyleSheet("QDialog{ background-color: %s }" %
                           Kst.SETALARMPOPUPBKG)

        # Create boxed Title
        titleLbl = QLabel(titleStr)
        titleLbl.setFrameStyle(QFrame.Box)
        titleLbl.setMinimumWidth(200)
        titleLbl.setAlignment(Qt.AlignCenter)

        fg = " QLabel {color:%s}" % '#000000'
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'

        # Y-Axis Fixed Scale spinboxes
        self.topSpinnerLbl = QLabel('Upper Fixed Scale:')
        self.topSpinner = QDoubleSpinBox()
        self.topSpinner.setToolTip("Set top fixed Y-axis value")
        self.topSpinner.setRange(-100000, 10000)
        self.topSpinner.setValue(self.scaleMaxv)
        self.topSpinner.setDecimals(1)
        self.topSpinner.setSingleStep(1.0)
        self.topSpinner.Xid = 'SP1'  # our tag: spinner-1

        self.btmSpinnerLbl = QLabel('Lower Fixed Scale:')

        self.btmSpinner = QDoubleSpinBox()
        self.topSpinner.setToolTip("Set bottom fixed Y-axis value")
        self.btmSpinner.setDecimals(1)
        self.btmSpinner.setSingleStep(1.0)
        self.btmSpinner.setRange(-100000, 10000)
        self.btmSpinner.setValue(self.scaleMinv)
        self.btmSpinner.Xid = 'SP2'  # our tag: spinner-2

        self.topSpinner.valueChanged.connect(self.pwdg.fixedScaleHandler)
        self.btmSpinner.valueChanged.connect(self.pwdg.fixedScaleHandler)

        # 3 radio buttons
        self.rBtnLbl = QLabel('Step:')
        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(True)
        self.rBtn1 = QRadioButton("10")
        self.rBtn2 = QRadioButton(" 1")
        self.rBtn3 = QRadioButton("0.1")
        self.rBtn2.setChecked(True)
        self.spinnerStep = 1.0
        self.btnGroup.addButton(self.rBtn1)
        self.btnGroup.addButton(self.rBtn2)
        self.btnGroup.addButton(self.rBtn3)

        self.rBtn1.setToolTip("Set indicated spinboxes increment")
        self.rBtn2.setToolTip("Set indicated spinboxes increment")
        self.rBtn3.setToolTip("Set indicated spinboxes increment")

        self.btnGroup.buttonClicked.connect(self.stepBtnHandler)

        self.line = QFrame()
        self.line.setGeometry(QRect(130, 230, 361, 41))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        # Buttons:  OK, Cancel
        self.okButton = QPushButton('Ok')  # create OK button
        self.okButton.setToolTip("Close dialog & set values.")
        self.closeButton = QPushButton('Close')  # create Cancel buttons
        self.closeButton.setToolTip("Close dialog & do not set values")

        # Unset autoDefault on above buttons
        # so that hitting return will not exit the popup
        # (because we want to use return to set values typed into spinbox)
        #print("AUTODEFAULT:", okButton.autoDefault())
        #print("ISDEFAULT  :", okButton.isDefault())
        self.okButton.setAutoDefault(False)
        self.okButton.setDefault(False)
        self.closeButton.setAutoDefault(False)
        self.closeButton.setDefault(False)

        # Layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.closeButton)
        layout = QGridLayout()

        #----------------------------
        layout.addWidget(titleLbl, 0, 0, 1, 8)
        layout.addWidget(self.line, 1, 0, 1, 8)
        layout.addWidget(self.topSpinnerLbl, 2, 0, 1, 2)  # time/date spinbox1
        layout.addWidget(self.topSpinner, 2, 2, 1, 2)  # time/date spinbox1
        layout.addWidget(self.btmSpinnerLbl, 3, 0, 1, 2)  # time/date spinbox1
        layout.addWidget(self.btmSpinner, 3, 2, 1, 2)  # time/date spinbox1

        layout.addWidget(self.rBtnLbl, 4, 0, 1, 1)
        layout.addWidget(self.rBtn1, 4, 1, 1, 1)
        layout.addWidget(self.rBtn2, 4, 2, 1, 1)
        layout.addWidget(self.rBtn3, 4, 3, 1, 1)
        layout.addWidget(self.line, 5, 0, 1, 8)
        layout.addLayout(buttonLayout, 8, 0, 1, 3)
        self.setLayout(layout)

        # Wire Ok/Cancel buttons to handlers
        # These would also work using builtin slots, 'accept'  & 'reject'

        self.okButton.clicked.connect(self.ok)
        self.closeButton.clicked.connect(self.reject)

    #def setDatesTimes(s,min,max):
    #    print("---- setDatesTimes ----")
    #    print("min", min.toString())
    #    print("max", max.toString())
    #    s.p1Dte.setDateTimeRange(min, max)
    #    s.p2Dte.setDateTimeRange(min, max)
    #    print("Step Enabled:", s.p1Dte.stepEnabled())

    #...........................................................................
    def popup(self, qp):
        #s.setDictValues() # apply new values every time
        self.move(qp.x(), qp.y())
        self.show()

    def setLblStyle(self, lbl):
        fg = " QLabel {color:%s}" % Kst.LBLFGCOLOR
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'
        lbl.setStyleSheet(fg + bg + border)

    def setSpinners(self, top, btm):
        #print("setSpinners")
        self.scaleMaxv = top
        self.scaleMinv = btm
        self.topSpinner.setValue(self.scaleMaxv)
        self.btmSpinner.setValue(self.scaleMinv)

    #...........................................................................
    # get new alarm&enable values from dict
    # checkbox signals stateChanged when box checked/unchecked
    #...........................................................................
    def setDictValues(self):
        pass

    #...........................................................................
    # Ok button handler: get values to dict
    #...........................................................................
    def ok(self):
        #s.emit(SIGNAL("ChartPopupOK"))
        #s.pwdg.fixedScaleTop = s.scaleMaxv
        #s.pwdg.fixedScaleBtm = s.scaleMinv
        #s.pwdg.setYScale(s.scaleMinv, s.scaleMaxv)

        self.scaleMaxv = self.topSpinner.value()
        self.scaleMinv = self.btmSpinner.value()
        self.pwdg.setFixedScale(
                'SP1', self.scaleMaxv)  #set top scale same as spinner 1
        self.pwdg.setFixedScale(
                'SP2', self.scaleMinv)  #set top scale same as spinner 2
        self.accept()  # dismiss dialogue w. QDialog.accept()

    #...........................................................................
    #
    #...........................................................................
    def stepBtnHandler(self):
        id = self.btnGroup.checkedId()  # which radio button?
        #print("stepBtnHandler Id", id)
        # Hours button
        if id == -2:  # is 10
            self.spinnerStep = 10.0

        # Minutes button
        if id == -3:  # is 1
            self.spinnerStep = 1.0
        # Seconds button
        if id == -4:  # is 0.1
            self.spinnerStep = 0.1

        self.topSpinner.setSingleStep(self.spinnerStep)
        self.btmSpinner.setSingleStep(self.spinnerStep)
