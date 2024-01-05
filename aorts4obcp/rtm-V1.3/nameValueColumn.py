#===============================================================================
# File : nameValueColumn.py
#      : Contains class nameValueColumn
#
# Notes:
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import Configuration

from PyQt4.QtCore import (Qt, QSize, SIGNAL)
#from PyQt4.QtGui import (QColor,QWidget,QFrame,QLabel,\
#                         QGridLayout,QVBoxLayout,QHBoxLayout,\
#                         QSizePolicy,QSplitter,\
#                         QMenuBar,QMenu,QAction,QStyleOption,QFont,\
#                         QSpacerItem, QFormLayout)

from PyQt4.QtGui import (QFormLayout, QSizePolicy, QLabel, QFont, QFrame)
from PyQt4.QtCore import QString
import util
import Constants as Kst
import ClickableLabel
import AlarmDialogue


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
class nameValueColumn(QFormLayout):

    #..........................................................................
    def __init__(s, names, parent=None):

        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        super(nameValueColumn, s).__init__(parent)
        s.names = names
        s.nrows = 0

        s.cfgD = s.cfg.cfgD
        s.D = {}

        # create 3 alarm states : No-alarm, low-alarm, hi-alarm
        s.NoAlarmState, s.LowAlarmState, s.HighAlarmState = range(3)

        #.......................................................................
        row = 0
        for name in names:

            item = s.cfgD[name]
            nlbl = QLabel(item['label'])  # Tag   label

            # Create clickable label
            vlbl = ClickableLabel.ClickableLabel(parent)

            # set same tooltip for label and value widgets
            vlbl.setToolTip(QString(item['desc']))
            nlbl.setToolTip(QString(item['desc']))

            # Create set-alarms popup
            # Pass name and alarm parameters dictionary
            title = "%s  ALARMS" % name

            #  create AlarmDialogue instance
            s.alarmDlg = AlarmDialogue.AlarmDialog(title.upper(), item,
                                                   parent=vlbl)
            # Set AlarmDialogue as clickable label popup
            vlbl.setClickAction(s.alarmDlg.popup)

            # Create dictionary items for this label
            s.D[name] = {}
            s.D[name]['dict'] = s.cfgD[name]
            s.D[name]['nlbl'] = nlbl
            s.D[name]['vlbl'] = vlbl
            s.D[name]['val'] = None
            s.D[name]['row'] = row
            s.D[name]['alarm'] = 0
            s.D[name]['alarmState'] = s.NoAlarmState

            # states for some labels for better efficiency
            s.loopTransition = 0
            s.vmdriveTransition = 0
            s.setValueStyle(vlbl)
            s.addRow(nlbl, vlbl)
            row += 1

        s.setFromConfig()
        s.nrows = row
        s.setHorizontalSpacing(0)

    def clicked(s, event):
        print("CLICKED", event)

    #............................................................
    def setFromConfig(s):

        for name in s.names:
            item = s.cfgD[name]
            s.D[name]['label'] = item['label']
            s.D[name]['datandx'] = int(item['dataNdx'])
            s.D[name]['alarmHi'] = item['alarmHi']['value']
            s.D[name]['alarmLow'] = item['alarmLow']['value']

    #............................................................
    #def setAlarmLevel(s, value):
    #    if value == 'None' or value is None:
    #        return None
    #    else:
    #        return float(value)
    #............................................................
    def setValueByTag(s, tag, value):
        s.D[tag]['val'] = value
        s.D[tag]['vlbl'].setText(str(value))

    #............................................................
    def setValueByRow(s, row, value):
        s.values[row] = value
        s.labels[row].setText(str(value))

    #............................................................
    def valuebyRow(s, row):
        return (s.values[row])

    #............................................................
    def valuebyTag(s, tag):
        s.values['tag']

    #............................................................
    # Other backgrounds : 'transparent',
    def setValueStyle(s, lbl):

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
    def setLabelStyle(s, lbl, bgcolor, fgcolor):
        bg = " QLabel {background-color:%s}" % bgcolor
        fg = " QLabel {background-color:%s}" % fgcolor
        border = " QLabel {border-color:%s}" % 'black'
        lbl.setStyleSheet(fg + bg + border)

        lbl.setFrameStyle(QFrame.Box | QFrame.Sunken)
        lbl.setLineWidth(1)
        lbl.setMidLineWidth(0)

    #............................................................
    def setAlarmStyleHigh(s, lbl):
        s.setLabelStyle(lbl, Kst.DESATRED, '#000000')

    #............................................................
    def setAlarmStyleLow(s, lbl):
        s.setLabelStyle(lbl, Kst.ALARMYELLOW, '#000000')

    #............................................................
    def setAlarmStyleNone(s, lbl):
        s.setValueStyle(lbl)

    #............................................................
    def setHighAlarm(s, item):
        if not item['alarmState'] == s.HighAlarmState:
            s.setAlarmStyleHigh(item['vlbl'])
            item['alarmState'] = s.HighAlarmState

    #............................................................
    def setLowAlarm(s, item):
        if not item['alarmState'] == s.LowAlarmState:
            s.setAlarmStyleLow(item['vlbl'])
            item['alarmState'] = s.LowAlarmState

    #............................................................
    def clearAlarm(s, item):
        item['alarmState'] = s.NoAlarmState
        s.setAlarmStyleNone(item['vlbl'])

    #............................................................
    def checkAlarms(s, name, item, value):

        alarmHi = item['dict']['alarmHi']['value']
        alarmLow = item['dict']['alarmLow']['value']

        if s.cfg.debug > 5:
            print("Label Alarm", name, value, alarmLow, alarmHi)

        # Check alarms
        if item['dict']['alarmHi']['enable'] \
           and value > float(alarmHi):
            if item['alarmState'] != s.HighAlarmState:
                s.lg.warn("High alarm.  %s = %.5f > %.5f" %
                          (name, float(value), float(alarmHi)))
            s.setHighAlarm(item)

        elif item['dict']['alarmLow']['enable'] \
            and value < float(alarmLow):
            s.setLowAlarm(item)

        elif item['alarmState'] != s.NoAlarmState:
            s.clearAlarm(item)

    #............................................................
    def updateData(s, data):
        for name in s.D:
            item = s.D[name]

            value = data[Kst.GENDATASTART + item['datandx']]
            item['textvalue'] = value
            s.checkAlarms(name, item, value)

            if s.cfg.debug:
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

                if s.loopTransition != value:
                    s.lg.info("LoopStatus: %s ==> %s", s.loopTransition, value)
                    s.loopTransition = value
                    if value == 'ON':
                        s.setLabelStyle(item['vlbl'], Kst.DESATGREEN, Kst.BLACK)
                    else:
                        s.setAlarmStyleNone(item['vlbl'])

            elif name == 'vmdrive':
                if value == Kst.VMDRIVE_ON:
                    value = 'ON'
                elif value == Kst.VMDRIVE_OFF:
                    value = 'OFF'
                elif value == -1:
                    value = 'UNKNOWN'
                else:
                    value = '???'

                if s.vmdriveTransition != value:
                    s.lg.info("Vmdrive: %s ==> %s", s.vmdriveTransition, value)
                    s.vmdriveTransition = value
                    if value == 'ON':
                        s.setLabelStyle(item['vlbl'], Kst.DESATGREEN, Kst.BLACK)
                    else:
                        s.setAlarmStyleNone(item['vlbl'])

            #s.setLabelStyle(item['vlbl'], Kst.BKGORANGE, Kst.Black)
            elif name == 'GsMode':
                if value == Kst.NGS_MATRIX:
                    value = 'NGS'
                    s.setLabelStyle(item['vlbl'], Kst.DESATBLUE, Kst.BLACK)
                elif value == Kst.LGS_MATRIX:
                    value = 'LGS'
                    s.setLabelStyle(item['vlbl'], Kst.DESATORANGE, Kst.BLACK)
                elif value == -1:
                    value = 'UNKNOWN'
                else:
                    value = '???'

            item['vlbl'].setText(str(value))

    #............................................................
    def configChangeHandler(s):
        print("change handler : nameValueColumn")
        s.setFromConfig()
