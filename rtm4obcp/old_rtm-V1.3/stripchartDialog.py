#===============================================================================
# File : stripchartDialog.py
#
# Notes:
# http://qt-project.org/doc/qt-4.8/qdatetime.html
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import Configuration
from PyQt4.QtCore import (Qt, SIGNAL, SLOT, QString, QRect)
from PyQt4.QtGui import (QLabel, QDialog, QSpinBox, QDoubleSpinBox, QPushButton,
                         QGridLayout, QHBoxLayout, QCheckBox, QFrame, QWidget,
                         QDateEdit, QDateTimeEdit, QButtonGroup, QRadioButton,
                         QFrame)
import Constants as Kst
from PyQt4 import Qwt5


#-------------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------------
class stripchartDialog(QDialog):

    def __init__(s, titleStr, pDct, parent=None):

        super(stripchartDialog, s).__init__(parent,
                                            Qt.Dialog | Qt.FramelessWindowHint)
        s.pwdg = parent
        s.pDct = pDct  # stripchart parameters dictionary
        s.id = s.pDct['Id']
        s.scaleMaxv = s.pDct['fixedScaleMax']['value']
        s.scaleMinv = s.pDct['fixedScaleMin']['value']
        s.spinnerStep = 1.0
        #s.scaleWheelMin = s.pDct['scaleWheelMin']['value']
        #s.scaleWheelMax = s.pDct['scaleWheelMax']['value']

        # set popup bkg color
        s.setStyleSheet("QDialog{ background-color: %s }" %
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
        s.topSpinnerLbl = QLabel('Upper Fixed Scale:')
        s.topSpinner = QDoubleSpinBox()
        s.topSpinner.setToolTip(QString("Set top fixed Y-axis value"))
        s.topSpinner.setRange(-100000, 10000)
        s.topSpinner.setValue(s.scaleMaxv)
        s.topSpinner.setDecimals(1)
        s.topSpinner.setSingleStep(1.0)
        s.topSpinner.Xid = 'SP1'  # our tag: spinner-1

        s.btmSpinnerLbl = QLabel('Lower Fixed Scale:')

        s.btmSpinner = QDoubleSpinBox()
        s.topSpinner.setToolTip(QString("Set bottom fixed Y-axis value"))
        s.btmSpinner.setDecimals(1)
        s.btmSpinner.setSingleStep(1.0)
        s.btmSpinner.setRange(-100000, 10000)
        s.btmSpinner.setValue(s.scaleMinv)
        s.btmSpinner.Xid = 'SP2'  # our tag: spinner-2

        s.connect(s.topSpinner, SIGNAL('valueChanged(double)'),
                  s.pwdg.fixedScaleHandler)

        s.connect(s.btmSpinner, SIGNAL('valueChanged(double)'),
                  s.pwdg.fixedScaleHandler)

        # 3 radio buttons
        s.rBtnLbl = QLabel('Step:')
        s.btnGroup = QButtonGroup()
        s.btnGroup.setExclusive(True)
        s.rBtn1 = QRadioButton("10")
        s.rBtn2 = QRadioButton(" 1")
        s.rBtn3 = QRadioButton("0.1")
        s.rBtn2.setChecked(True)
        s.spinnerStep = 1.0
        s.btnGroup.addButton(s.rBtn1)
        s.btnGroup.addButton(s.rBtn2)
        s.btnGroup.addButton(s.rBtn3)

        s.rBtn1.setToolTip(QString("Set indicated spinboxes increment"))
        s.rBtn2.setToolTip(QString("Set indicated spinboxes increment"))
        s.rBtn3.setToolTip(QString("Set indicated spinboxes increment"))

        s.connect(s.btnGroup, SIGNAL('buttonClicked(int)'), s.stepBtnHandler)

        s.line = QFrame()
        s.line.setGeometry(QRect(130, 230, 361, 41))
        s.line.setFrameShape(QFrame.HLine)
        s.line.setFrameShadow(QFrame.Sunken)

        # Buttons:  OK, Cancel
        s.okButton = QPushButton('Ok')  # create OK button
        s.okButton.setToolTip(QString("Close dialog & set values."))
        s.closeButton = QPushButton('Close')  # create Cancel buttons
        s.closeButton.setToolTip(QString("Close dialog & do not set values"))

        # Unset autoDefault on above buttons
        # so that hitting return will not exit the popup
        # (because we want to use return to set values typed into spinbox)
        #print("AUTODEFAULT:", okButton.autoDefault())
        #print("ISDEFAULT  :", okButton.isDefault())
        s.okButton.setAutoDefault(False)
        s.okButton.setDefault(False)
        s.closeButton.setAutoDefault(False)
        s.closeButton.setDefault(False)

        # Layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(s.okButton)
        buttonLayout.addWidget(s.closeButton)
        layout = QGridLayout()

        #----------------------------
        layout.addWidget(titleLbl, 0, 0, 1, 8)
        layout.addWidget(s.line, 1, 0, 1, 8)
        layout.addWidget(s.topSpinnerLbl, 2, 0, 1, 2)  # time/date spinbox1
        layout.addWidget(s.topSpinner, 2, 2, 1, 2)  # time/date spinbox1
        layout.addWidget(s.btmSpinnerLbl, 3, 0, 1, 2)  # time/date spinbox1
        layout.addWidget(s.btmSpinner, 3, 2, 1, 2)  # time/date spinbox1

        layout.addWidget(s.rBtnLbl, 4, 0, 1, 1)
        layout.addWidget(s.rBtn1, 4, 1, 1, 1)
        layout.addWidget(s.rBtn2, 4, 2, 1, 1)
        layout.addWidget(s.rBtn3, 4, 3, 1, 1)
        layout.addWidget(s.line, 5, 0, 1, 8)
        layout.addLayout(buttonLayout, 8, 0, 1, 3)
        s.setLayout(layout)

        # Wire Ok/Cancel buttons to handlers
        # These would also work using builtin slots, 'accept'  & 'reject'

        s.connect(s.okButton, SIGNAL('clicked()'), s.ok)
        s.connect(s.closeButton, SIGNAL('clicked()'), s, SLOT("reject()"))

    #def setDatesTimes(s,min,max):
    #    print("---- setDatesTimes ----")
    #    print("min", min.toString())
    #    print("max", max.toString())
    #    s.p1Dte.setDateTimeRange(min, max)
    #    s.p2Dte.setDateTimeRange(min, max)
    #    print("Step Enabled:", s.p1Dte.stepEnabled())

    #...........................................................................
    def popup(s, qp):
        #s.setDictValues() # apply new values every time
        s.move(qp.x(), qp.y())
        s.show()

    def setLblStyle(s, lbl):
        fg = " QLabel {color:%s}" % Kst.LBLFGCOLOR
        bg = " QLabel {background-color:%s}" % Kst.SETALARMPOPUPBKG
        border = " QLabel {border-color:%s}" % '#000000'
        lbl.setStyleSheet(fg + bg + border)

    def setSpinners(s, top, btm):
        #print("setSpinners")
        s.scaleMaxv = top
        s.scaleMinv = btm
        s.topSpinner.setValue(s.scaleMaxv)
        s.btmSpinner.setValue(s.scaleMinv)

    #...........................................................................
    # get new alarm&enable values from dict
    # checkbox signals stateChanged when box checked/unchecked
    #...........................................................................
    def setDictValues(s):
        pass

    #...........................................................................
    # Ok button handler: get values to dict
    #...........................................................................
    def ok(s):
        #s.emit(SIGNAL("ChartPopupOK"))
        #s.pwdg.fixedScaleTop = s.scaleMaxv
        #s.pwdg.fixedScaleBtm = s.scaleMinv
        #s.pwdg.setYScale(s.scaleMinv, s.scaleMaxv)

        s.scaleMaxv = s.topSpinner.value()
        s.scaleMinv = s.btmSpinner.value()
        s.pwdg.setFixedScale('SP1',
                             s.scaleMaxv)  #set top scale same as spinner 1
        s.pwdg.setFixedScale('SP2',
                             s.scaleMinv)  #set top scale same as spinner 2
        s.accept()  # dismiss dialogue w. QDialog.accept()

    #...........................................................................
    #
    #...........................................................................
    def stepBtnHandler(s):
        id = s.btnGroup.checkedId()  # which radio button?
        #print("stepBtnHandler Id", id)
        # Hours button
        if id == -2:  # is 10
            s.spinnerStep = 10.0

        # Minutes button
        if id == -3:  # is 1
            s.spinnerStep = 1.0
        # Seconds button
        if id == -4:  # is 0.1
            s.spinnerStep = 0.1

        s.topSpinner.setSingleStep(s.spinnerStep)
        s.btmSpinner.setSingleStep(s.spinnerStep)

    #...........................................................................
    #
    #...........................................................................
    #def btnHandler_plotTime(s):
    #    id = s.btnGroup.checkedId() # which radio button?
    #    # Hours button
    #    if id == -2: # is one Hour
    #        nHours = 4
    #        t1 = s.pwdg.tSeconds - (3 * 3600)
    #        if t1 < 0 :
    #            t1 = 0
    #        t2 = t1 + nHours * 3600
    #        s.pwdg.setPlot(Kst.HOURS, t1,t2 )
    #
    #    # Minutes button
    #    if id == -3: # Minutes
    #        nMinutes = 5
    #        t1 = s.pwdg.tSeconds - (nMinutes * 60)
    #        if t1 < 0 :
    #            t1 = 0
    #        t2 = t1 + (nMinutes * 60) + 60
    #        s.pwdg.setPlot(Kst.MINUTES, t1,t2 )
    #
    #
    #    # Seconds button
    #    if id == -4:
    #        nSeconds = 30
    #        t1 = s.pwdg.tSeconds - nSeconds
    #        if t1 < 0 :
    #            t1 = 0
    #        t2 = t1 + nSeconds + 10
    #        s.pwdg.setPlot(Kst.SECONDS, t1,t2 )

    #QCheckBox("Enable") # create checkbox
    ## date/time Spinboxes
    #s.p1Dte = QDateTimeEdit()
    #s.p2Dte = QDateTimeEdit()
    #s.p1Dte.setDisplayFormat(QString('yyyy/MM/dd  hh:mm:ss'))
    #s.p2Dte.setDisplayFormat(QString('yyyy MM dd  hh:mm:ss'))
    ##s.p1Dte.setEnabled(True)
    ##s.p1Dte.setFocusPolicy(Qt.StrongFocus)
    ##s.p2Dte.setFocusPolicy(Qt.StrongFocus)

    #s.topSpinner = Qwt5.QwtCounter()
    #s.topSpinner.setGeometry(QRect(60, 120, 171, 51))
    #s.topSpinner.setRange(-1000.0, 1000.0)
    #s.topSpinner.setStep(0.1)
    #s.topSpinner.setNumButtons(3)
    #s.topSpinner.setStepButton1(100)
    #s.topSpinner.setStepButton2(10)
    #s.topSpinner.setStepButton3(1)

    #s.btmSpinner = Qwt5.QwtCounter()
    #s.btmSpinner.setGeometry(QRect(60, 120, 171, 51))
    #s.btmSpinner.setRange(-1000.0, 1000.0)
    #s.btmSpinner.setStep(0.1)
    #s.btmSpinner.setNumButtons(3)
    #s.btmSpinner.setStepButton1(100)
    #s.btmSpinner.setStepButton2(10)
    #s.btmSpinner.setStepButton3(1)
