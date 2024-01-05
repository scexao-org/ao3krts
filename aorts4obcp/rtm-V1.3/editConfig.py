#!/usr/bin/python
#===============================================================================
# File : editConfig.py
# Notes:
#
#
#
#
#
#
#
#===============================================================================
from __future__ import absolute_import, print_function, division
from PyQt4.QtCore import (Qt, QSize, QRect, QString, SIGNAL, QObject)
from PyQt4.QtGui import (QWidget, QBrush, QColor, QPalette, QFrame,
                         QApplication, QMainWindow, QPushButton, QLabel, QFont,
                         QPalette, QHBoxLayout, QVBoxLayout, QLineEdit,
                         QDialogButtonBox, QDialog, QScrollArea, QToolBar,
                         QSizePolicy)
import sys, string
import Configuration
import DictUtils as du
import util
import nameValueColumn as nvc
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import Constants as Kst
from yaml import dump as yamlDump


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class editConfigWindowMwin(QMainWindow):

    def __init__(s, parent=None):

        super(editConfigWindowMwin, s).__init__(parent)
        s.cfg = Configuration.cfg
        s.lg = s.cfg.lg
        #s.setWindowFlags(Qt.WindowFlags(Qt.NonModal|Qt.WindowStaysOnTopHint) )
        s.setWindowModality(Qt.NonModal)
        s.toolbar = s.addToolBar(QString("Edit"))
        s.toolbar.addAction('Apply', s.applyDict)
        s.toolbar.addAction('Save', s.saveDict)
        s.toolbar.addAction('Quit', s.quit)

        s.panel = DictLabelsPanel(s.cfg.cfgD, s)
        s.scrollArea = QScrollArea(s)
        s.scrollArea.setWidget(s.panel)
        s.setCentralWidget(s.scrollArea)

    def setValues(s):
        D = s.cfg.cfgD
        for lbp in s.panel.lbpairs:
            lbp.setValue(str(D[lbp.pkey][lbp.key]['value']))

    #-..........................................................................
    #
    #...........................................................................
    def saveDict(s):
        if s.cfg.debug: print("<DictLabelsPanel.saveDict>")
        s.cfg.lg.info("Saving configuration to file: %s" % s.cfg.configpath)

        #du.writeDict(s.cfg.configpath,s.cfg.cfgD, logger=s.cfg.lg)
        #du.writeDict('dict.cfg', s.cfg.cfgD, logger=s.cfg.lg)

        # no longer use shelved-dictionaries
        #s.cfg.shd.set(s.cfg.cfgD)
        #s.cfg.shd.sync()

        s.cfg.saveConfigDict()

        #fs  = file(s.cfg.configpath, 'w')
        #rtn = yamlDump( s.cfg.cfgD, fs)
        #fs.close()

    #-..........................................................................
    #   'Apply' button handler
    #...........................................................................
    def applyDict(s):
        if s.cfg.debug: print("<DictLabelsPanel.applyDict>")
        for lbp in s.panel.lbpairs:
            lbp.setDictValue(lbp.valText)
        s.emit(SIGNAL('ConfigChanged'))

    #-..........................................................................
    def quit(s):
        s.close()
        #s.destroy()

    #-..........................................................................
    # called on edit-window close
    #...........................................................................
    def closeEvent(s, ev):
        #s.lg.info("Configuration edit close")
        pass


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DictLabelsPanel(QFrame):

    def __init__(s, D, parent=None, bgcolor=None, fgcolor=None, font=None,
                 fontSz=None):

        super(DictLabelsPanel, s).__init__(parent)

        s.D = D
        s.vbox = QVBoxLayout()
        s.vbox.setSpacing(0)
        s.lbpairs = []

        # alarms
        lbls = ('dmeye', 'crveye', 'apdeye', 'sheye', 'dmTiltX', 'dmTiltY',
                'dmDefocus', 'dmMax', 'dmMin', 'dmAvg', 'crvTiltY',
                'crvDefocus', 'crvMax', 'crvMin', 'crvAvg', 'shTiltX',
                'shTiltY', 'shDefocus', 'shMax', 'shRmag', 'shAvg',
                'loopStatus', 'dmgain', 'ttgain', 'psbgain', 'sttgain',
                'GsMode', 'dmgainHold', 'ttgainHold', 'psbgainHold',
                'sttgainHold', 'vmdrive', 'vmvolt', 'vmfreq', 'vmphase',
                'httgain', 'wttgain', 'lttgain', 'ldfgain', 'hdfgain',
                'adfgain')
        for lbl in lbls:
            s.appendLbp(lbl, 'alarmHi')
            s.appendLbp(lbl, 'alarmLow')

        s.appendLbp('gen', 'rtDataHost')
        s.appendLbp('gen', 'port')
        s.appendLbp('gen', 'debug')
        s.appendLbp('gen', 'framesPerEye')
        s.appendLbp('gen', 'framesPerLabel')
        s.appendLbp('gen', 'framesPerChart')
        s.appendLbp('gen', 'framesPerMountPlot')
        s.appendLbp('gen', 'framesPerSH')
        s.appendLbp('gen', 'framesPerSHArrow')
        s.appendLbp('gen', 'ScreenX')
        s.appendLbp('gen', 'ScreenY')
        s.appendLbp('gen', 'stripchartHours')
        #s.appendLbp('gen','connectCommand'    )
        s.setLayout(s.vbox)

    #-..........................................................................
    def appendLbp(s, pkey, key):
        lbp = DictLabelPair(s.D, pkey, key)
        s.lbpairs.append(lbp)  # append this label-pair to list
        s.vbox.addWidget(lbp)  # add label-pair widget to layout

    #-..........................................................................
    #
    #...........................................................................
    def returned(s):
        print("*** <DictLabelPair.returned>", s.lineEdit.text())

    #def sizeHint(s):
    #    return(QSize(200,400)) # wd,ht


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class labelPair(QWidget):

    def __init__(s, tagText=None, value=None, parent=None, bgcolor=None,
                 fgcolor=None, font=None):

        super(labelPair, s).__init__(parent)

        s.debug = 0
        if s.debug > 1:
            print("<editConfig.labelPair__init__>", tagText, value, parent)

        s.valText = str(value)
        s.tagText = tagText

        s.tagwd = 350
        s.taght = 20
        s.valwd = 125
        s.valht = 20

        if s.debug:
            print("........................................")
            print("labelPair.value    :", value)
            print("labelPair.valText  :", s.valText)

        s.lbltag = QLabel(tagText)
        s.lineEdit = QLineEdit(s)
        if s.valText is not None:
            if s.debug: print("valtext :", s.valText)
            s.lineEdit.setText(s.valText)
        else:
            s.lineEdit.setText(QString("***"))

        s.hbox = QHBoxLayout()
        s.hbox.setSpacing(20)
        s.hbox.addStrut(20)
        #s.hbox.setGeometry(QRect(0,0,0,350))
        s.hbox.addWidget(s.lineEdit)
        s.hbox.addWidget(s.lbltag)

        #s.lbltag.setMinimumSize(QSize(s.tagwd, s.taght))
        #s.lbltag.setMaximumSize(QSize(s.tagwd, s.taght))

        s.lbltag.setFixedSize(QSize(s.tagwd, s.taght))
        s.lineEdit.setFixedSize(QSize(s.valwd, s.valht))
        s.lbltag.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        s.lineEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        s.lbltag.setMargin(0)
        s.lbltag.setIndent(0)
        s.lineEdit.setAlignment(Qt.AlignRight)
        #s.lineEdit.setTextMargins(0,0,0,0)
        s.lineEdit.setStyleSheet("selection-background-color: %s" % "#000000")
        s.lineEdit.setStyleSheet("background-color: %s" % Kst.MWINBKGCOLOR)

        s.set_tagStyle()
        s.hbox.addWidget(s.lbltag)
        s.setLayout(s.hbox)

        #.......................................................................
        s.palette = QPalette()
        s.brush = QBrush(QColor(0, 255, 0))
        s.brush.setStyle(Qt.SolidPattern)
        s.palette.setBrush(QPalette.Active, QPalette.ButtonText, s.brush)
        s.palette.setBrush(QPalette.Active, QPalette.WindowText, s.brush)
        s.palette.setBrush(QPalette.Active, QPalette.Text, s.brush)

        s.connect(s.lineEdit, SIGNAL("selectionChanged()"), s.changedSelection)
        s.connect(s.lineEdit, SIGNAL("cursorPositionChanged(int,int)"),
                  s.cursorMoved)
        s.connect(s.lineEdit, SIGNAL("editingFinished()"), s.editFinished)
        s.connect(s.lineEdit, SIGNAL("textEdited()"), s.textEdited)
        s.connect(s.lineEdit, SIGNAL("textChanged()"), s.updateVal)
        s.connect(s.lineEdit, SIGNAL("returnPressed()"), s.returned)

    def setValue(s, value):
        if s.debug > 2: print("<labelPair.setValue>", value)
        s.lineEdit.setText(value)

    def editFinished(s):
        if s.debug > 2:
            print("<labelPair>.editFinished", s.lineEdit.text())
        text = s.lineEdit.text()

        # Replace textual 'None' with python type None
        if text == 'None':
            s.valText = None
        else:
            s.valText = text

    def changedSelection(s):
        if s.debug > 2:
            print("*** Changed selection ***", s.lineEdit.text())
        pass

    def returned(s):
        if s.debug > 2:
            print("*** returned ***", s.lineEdit.text())
        pass

    def updateVal(s):
        if s.debug > 2:
            print("*** updateVal ***", s.lineEdit.text())
        pass

    def textEdited(s):
        if s.debug > 2:
            print("*** text Edited ***", s.lineEdit.text())
        pass

    def cursorMoved(s, c1, c2):  # sig:editingFinished()
        if s.debug > 2:
            print("*** cursorMoved ***", c1, c2, s.lineEdit.text())
        pass

    #...........................................................................
    #
    #...........................................................................
    def setFont(s, lbl, font="Arabic Newspaper", size=10):
        s.font = QFont()
        s.qfont.setFamily(_fromUtf8(font))
        s.qfont.setPointSize(size)

    #...........................................................................
    #
    #...........................................................................
    def set_tagStyle(s):
        lbl = s.lbltag
        #lbl.setFrameShape(QFrame.Box)
        #lbl.setFrameShadow(QFrame.Sunken)
        #lbl.setMidLineWidth(1)

        lbl.setStyleSheet( \
          _fromUtf8("background-color: rgb(AOAOAO); color:rgb(0,0,0);"))

        lbl.setAutoFillBackground(False)
        lbl.setGeometry(QRect(s.taght, s.tagwd, s.taght, s.tagwd))
        lbl.setMidLineWidth(1)
        lbl.setLineWidth(1)

        font = "Arabic Newspaper"
        fontSize = 10
        qfont = QFont()
        qfont.setFamily(_fromUtf8(font))
        qfont.setPointSize(fontSize)
        lbl.setFont(qfont)

        #s.lblval.setTextInteractionFlags(Qt.NoTextInteraction)

    def set_valStyle(s):
        lbl = s.lblval
        lbl.setGeometry(QRect(s.taght, s.tagwd, s.taght, s.tagwd))

        font = "Arabic Newspaper"
        fontSize = 10
        qfont = QFont()
        qfont.setFamily(_fromUtf8(font))
        qfont.setPointSize(fontSize)

        lbl.setFont(qfont)

        lbl.setCursor(Qt.IBeamCursor)
        lbl.setFocusPolicy(Qt.ClickFocus)
        lbl.setAutoFillBackground(False)
        lbl.setStyleSheet("background-color: %s" % Kst.MWINBKGCOLOR)
        lbl.setFrameShape(QFrame.StyledPanel)  # Box, StyledPanel...
        lbl.setFrameShadow(QFrame.Sunken)  # Raised,Sunken
        lbl.setMidLineWidth(8)
        lbl.setLineWidth(8)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | \
                                         Qt.TextEditable)

        lbl.setAcceptDrops(True)


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DictLabelPair(labelPair):

    def __init__(s, D, pkey, key, parent=None, bgcolor=None, fgcolor=None,
                 font=None):

        s.cfg = Configuration.cfg
        if s.cfg.debug > 9: print("<DictLabelPair__init__>", pkey, key)
        super(DictLabelPair, s).__init__(D[pkey][key]['label'],
                                         D[pkey][key]['value'], parent)
        s.D = D
        s.pkey = pkey
        s.key = key

    #-..........................................................................
    def setDictValue(s, value):
        if s.cfg.debug:
            print("<DictLabelPair.setDictValue>:", s.pkey, s.key, value)

        if value == None or value == 'None':
            s.D[s.pkey][s.key]['value'] = None
        else:
            s.D[s.pkey][s.key]['value'] = util.stringValue(str(value))

    #-..........................................................................
    def editFinished(s):
        if s.cfg.debug: print("<DictLabelPair>editFinished", s.lineEdit.text())
        value = s.lineEdit.text()
        if s.cfg.debug: print("    value:", value)
        s.setDictValue(value)
        s.cfg.setCfgFromDict()  # Dict ---> Config dict


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    import Constants as Kst
    import Logger

    #import defaultConfig


    def raise_editConfigWindow(parent):
        top = editConfigWindowMwin(parent)
        #top.move(20,80)
        top.setGeometry(20, 80, 500, 900)
        top.show()

    def btn00Handler():
        raise_editConfigWindow(mwin)

    import Configurer
    import Constants as Kst
    app = QApplication(sys.argv)
    mwin = QMainWindow()
    mwin.setWindowTitle("Test Window")

    #lg=Logger.Logger(logpath=Kst.LOGPATH, nfiles=10,level='INFO').lg
    #configurer = Configurer.Configurer(  Kst.CONFIGFILE, lg )
    #btn00  = QPushButton(mwin)
    #mwin.connect( btn00, SIGNAL('clicked()'), btn00Handler)
    #mwin.show()

    logpath = "%s/%s" % (Kst.LOGDIR, Kst.LOGFILE)  # use constants default
    logger = Logger.Logger(logpath, nfiles=5, level='INFO', debug=0)
    logpath = logger.logpath  # logpath from logger
    lg = logger.lg  # 'lg' will be python logging system
    logger.setLevel('INFO')  # set console & file logging level
    logger.set_console_level('ERROR')  # don't write this to stdout again
    lg.info("\n\n")
    lg.info("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
            )
    lg.info("|||||||||||||||||||||||||||||| EditConfig START  ||||||||||||||||||||||||||||||"
            )
    lg.info("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
            )
    logger.set_console_level(logger.level)  #restore console logging level

    # preload edit popup window
    ecw = editConfigWindowMwin()
    #ecw.setWindowModality(Qt.NonModal)
    #ecw.setGeometry(20,80, 500,900)
    #ecw.setValues()
    #ecw.show()

    app.exec_()
