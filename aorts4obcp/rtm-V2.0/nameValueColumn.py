#===============================================================================
# File : nameValueColumn.py
#      : Contains class nameValueColumn
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import Configuration

from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QFormLayout, QSizePolicy, QLabel, QFrame)

import Constants as Kst
import ClickableLabel
import AlarmDialogue


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class nameValueColumn(QFormLayout):

    #..........................................................................
    def __init__(self, names, parent=None):

        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        super(nameValueColumn, self).__init__(parent)
        self.names = names
        self.nrows = 0

        self.cfgD = self.cfg.cfgD
        self.D = {}

        # create 3 alarm states : No-alarm, low-alarm, hi-alarm
        self.NoAlarmState, self.LowAlarmState, self.HighAlarmState = range(3)

        #.......................................................................
        row = 0
        for name in names:

            item = self.cfgD[name]
            nlbl = QLabel(item['label'])  # Tag   label

            # Create clickable label
            vlbl = ClickableLabel.ClickableLabel(parent)

            # set same tooltip for label and value widgets
            vlbl.setToolTip(item['desc'])
            nlbl.setToolTip(item['desc'])

            # Create set-alarms popup
            # Pass name and alarm parameters dictionary
            title = "%s  ALARMS" % name

            #  create AlarmDialogue instance
            self.alarmDlg = AlarmDialogue.AlarmDialog(title.upper(), item,
                                                      parent=vlbl)
            # Set AlarmDialogue as clickable label popup
            vlbl.setClickAction(self.alarmDlg.popup)

            # Create dictionary items for this label
            self.D[name] = {}
            self.D[name]['dict'] = self.cfgD[name]
            self.D[name]['nlbl'] = nlbl
            self.D[name]['vlbl'] = vlbl
            self.D[name]['val'] = None
            self.D[name]['row'] = row
            self.D[name]['alarm'] = 0
            self.D[name]['alarmState'] = self.NoAlarmState

            # states for some labels for better efficiency
            self.loopTransition = 0
            self.vmdriveTransition = 0
            self.setValueStyle(vlbl)
            self.addRow(nlbl, vlbl)
            row += 1

        self.setFromConfig()
        self.nrows = row
        self.setHorizontalSpacing(0)

    def clicked(s, event):
        print("CLICKED", event)

    #............................................................
    def setFromConfig(self):

        for name in self.names:
            item = self.cfgD[name]
            self.D[name]['label'] = item['label']
            self.D[name]['datandx'] = int(item['dataNdx'])
            self.D[name]['alarmHi'] = item['alarmHi']['value']
            self.D[name]['alarmLow'] = item['alarmLow']['value']

    #............................................................
    def setValueByTag(self, tag, value):
        self.D[tag]['val'] = value
        self.D[tag]['vlbl'].setText(str(value))

    #............................................................
    def setValueByRow(self, row, value):
        self.values[row] = value
        self.labels[row].setText(str(value))

    #............................................................
    def valuebyRow(self, row):
        return (self.values[row])

    #............................................................
    def valuebyTag(self, tag):
        self.values[tag]

    #............................................................
    # Other backgrounds : 'transparent',
    def setValueStyle(self, lbl):

        fg = " QLabel {color:%s}" % Kst.LBLFGCOLOR
        bg = " QLabel {background-color:%s}" % Kst.LBLBKGCOLOR
        border = " QLabel {border-color:%s}" % '#000000'
        lbl.setStyleSheet(fg + bg + border)

        lbl.setAlignment(Qt.AlignRight)
        lbl.setFont(QFont("Monospace"))
        lbl.setMinimumWidth(80)
        lbl.setMaximumWidth(80)
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        lbl.setTextFormat(Qt.RichText)
        lbl.setFrameStyle(QFrame.Box | QFrame.Sunken)
        lbl.setLineWidth(1)
        lbl.setMidLineWidth(0)

        # enum TextInteractionFlag NoTextInteraction, TextSelectableByMouse,
        #  TextSelectableByKeyboard, LinksAccessibleByMouse, ...,
        #  TextBrowserInteraction }
        #lbl.setTextInteractionFlags(Qt.NoTextInteraction)
        # Align: Qt. AlignLeft,AlignRight,AlignHCenter,AlignJustify
        #lbl.setGeometry(QRect(s.nameht, s.namewd, s.nameht, s.namewd))

    #............................................................
    def setLabelStyle(self, lbl, bgcolor, fgcolor):
        bg = " QLabel {background-color:%s}" % bgcolor
        fg = " QLabel {background-color:%s}" % fgcolor
        border = " QLabel {border-color:%s}" % 'black'
        lbl.setStyleSheet(fg + bg + border)

        lbl.setFrameStyle(QFrame.Box | QFrame.Sunken)
        lbl.setLineWidth(1)
        lbl.setMidLineWidth(0)

    #............................................................
    def setAlarmStyleHigh(self, lbl):
        self.setLabelStyle(lbl, Kst.DESATRED, '#000000')

    #............................................................
    def setAlarmStyleLow(self, lbl):
        self.setLabelStyle(lbl, Kst.ALARMYELLOW, '#000000')

    #............................................................
    def setAlarmStyleNone(self, lbl):
        self.setValueStyle(lbl)

    #............................................................
    def setHighAlarm(self, item):
        if not item['alarmState'] == self.HighAlarmState:
            self.setAlarmStyleHigh(item['vlbl'])
            item['alarmState'] = self.HighAlarmState

    #............................................................
    def setLowAlarm(self, item):
        if not item['alarmState'] == self.LowAlarmState:
            self.setAlarmStyleLow(item['vlbl'])
            item['alarmState'] = self.LowAlarmState

    #............................................................
    def clearAlarm(self, item):
        item['alarmState'] = self.NoAlarmState
        self.setAlarmStyleNone(item['vlbl'])

    #............................................................
    def checkAlarms(self, name, item, value):

        alarmHi = item['dict']['alarmHi']['value']
        alarmLow = item['dict']['alarmLow']['value']

        if self.cfg.debug > 5:
            print("Label Alarm", name, value, alarmLow, alarmHi)

        # Check alarms
        if item['dict']['alarmHi']['enable'] \
           and value > float(alarmHi):
            if item['alarmState'] != self.HighAlarmState:
                self.lg.warn("High alarm.  %s = %.5f > %.5f" %
                             (name, float(value), float(alarmHi)))
            self.setHighAlarm(item)

        elif item['dict']['alarmLow']['enable'] \
            and value < float(alarmLow):
            self.setLowAlarm(item)

        elif item['alarmState'] != self.NoAlarmState:
            self.clearAlarm(item)

    #............................................................
    def updateData(self, data):
        for name in self.D:
            item = self.D[name]

            value = data[Kst.GENDATASTART + item['datandx']]
            item['textvalue'] = value
            self.checkAlarms(name, item, value)

            if self.cfg.debug:
                print("%s:%s" % (item['label'], value))

            # kludges: display text in place of numeric values
            if name == 'loopStatus':
                if value == Kst.LOOPSTATUS_ON:
                    value = 'ON'
                elif value == Kst.LOOPSTATUS_OFF:
                    value = 'OFF'
                elif value == -1:
                    value = 'UNKNOWN'
                else:
                    value = '???'

                if self.loopTransition != value:
                    self.lg.info("LoopStatus: %s ==> %s", self.loopTransition,
                                 value)
                    self.loopTransition = value
                    if value == 'ON':
                        self.setLabelStyle(item['vlbl'], Kst.DESATGREEN,
                                           Kst.BLACK)
                    else:
                        self.setAlarmStyleNone(item['vlbl'])

            elif name == 'vmdrive':
                if value == Kst.VMDRIVE_ON:
                    value = 'ON'
                elif value == Kst.VMDRIVE_OFF:
                    value = 'OFF'
                elif value == -1:
                    value = 'UNKNOWN'
                else:
                    value = '???'

                if self.vmdriveTransition != value:
                    self.lg.info("Vmdrive: %s ==> %s", self.vmdriveTransition,
                                 value)
                    self.vmdriveTransition = value
                    if value == 'ON':
                        self.setLabelStyle(item['vlbl'], Kst.DESATGREEN,
                                           Kst.BLACK)
                    else:
                        self.setAlarmStyleNone(item['vlbl'])

            #s.setLabelStyle(item['vlbl'], Kst.BKGORANGE, Kst.Black)
            elif name == 'GsMode':
                if value == Kst.NGS_MATRIX:
                    value = 'NGS'
                    self.setLabelStyle(item['vlbl'], Kst.DESATBLUE, Kst.BLACK)
                elif value == Kst.LGS_MATRIX:
                    value = 'LGS'
                    self.setLabelStyle(item['vlbl'], Kst.DESATORANGE, Kst.BLACK)
                elif value == -1:
                    value = 'UNKNOWN'
                else:
                    value = '???'

            item['vlbl'].setText(str(value))

    #............................................................
    def configChangeHandler(self):
        print("change handler : nameValueColumn")
        self.setFromConfig()
