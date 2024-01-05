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
from PyQt5.QtCore import (Qt, QSize, QRect)
from PyQt5.QtGui import (QBrush, QColor, QPalette, QFont)
from PyQt5.QtWidgets import (QWidget, QFrame, QApplication, QMainWindow, QLabel,
                             QHBoxLayout, QVBoxLayout, QLineEdit, QScrollArea,
                             QSizePolicy)

import sys
import Configuration

import util

_fromUtf8 = lambda s: s

import Constants as Kst

from yaml import dump as yamlDump


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class editConfigWindowMwin(QMainWindow):

    def __init__(self, parent=None):

        super(editConfigWindowMwin, self).__init__(parent)
        self.cfg = Configuration.cfg
        self.lg = self.cfg.lg
        #s.setWindowFlags(Qt.WindowFlags(Qt.NonModal|Qt.WindowStaysOnTopHint) )
        self.setWindowModality(Qt.NonModal)
        self.toolbar = self.addToolBar("Edit")
        self.toolbar.addAction('Apply', self.applyDict)
        self.toolbar.addAction('Save', self.saveDict)
        self.toolbar.addAction('Quit', self.quit)

        self.panel = DictLabelsPanel(self.cfg.cfgD, self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.panel)
        self.setCentralWidget(self.scrollArea)

    def setValues(self):
        D = self.cfg.cfgD
        for lbp in self.panel.lbpairs:
            lbp.setValue(str(D[lbp.pkey][lbp.key]['value']))

    #-..........................................................................
    #
    #...........................................................................
    def saveDict(self):
        if self.cfg.debug: print("<DictLabelsPanel.saveDict>")
        self.cfg.lg.info("Saving configuration to file: %s" %
                         self.cfg.configpath)

        #du.writeDict(s.cfg.configpath,s.cfg.cfgD, logger=s.cfg.lg)
        #du.writeDict('dict.cfg', s.cfg.cfgD, logger=s.cfg.lg)

        # no longer use shelved-dictionaries
        #s.cfg.shd.set(s.cfg.cfgD)
        #s.cfg.shd.sync()

        self.cfg.saveConfigDict()

        #fs  = file(s.cfg.configpath, 'w')
        #rtn = yamlDump( s.cfg.cfgD, fs)
        #fs.close()

    #-..........................................................................
    #   'Apply' button handler
    #...........................................................................
    def applyDict(self):
        if self.cfg.debug: print("<DictLabelsPanel.applyDict>")
        for lbp in self.panel.lbpairs:
            lbp.setDictValue(lbp.valText)
        self.emit(SIGNAL('ConfigChanged'))

    #-..........................................................................
    def quit(self):
        self.close()
        #s.destroy()

    #-..........................................................................
    # called on edit-window close
    #...........................................................................
    def closeEvent(self, ev):
        #s.lg.info("Configuration edit close")
        pass


#^------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class DictLabelsPanel(QFrame):

    def __init__(self, D, parent=None, bgcolor=None, fgcolor=None, font=None,
                 fontSz=None):

        super(DictLabelsPanel, self).__init__(parent)

        self.D = D
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(0)
        self.lbpairs = []

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
            self.appendLbp(lbl, 'alarmHi')
            self.appendLbp(lbl, 'alarmLow')

        self.appendLbp('gen', 'rtDataHost')
        self.appendLbp('gen', 'rtDataPort')
        self.appendLbp('gen', 'debug')
        self.appendLbp('gen', 'framesPerEye')
        self.appendLbp('gen', 'framesPerLabel')
        self.appendLbp('gen', 'framesPerChart')
        self.appendLbp('gen', 'framesPerMountPlot')
        self.appendLbp('gen', 'framesPerSH')
        self.appendLbp('gen', 'framesPerSHArrow')
        self.appendLbp('gen', 'ScreenX')
        self.appendLbp('gen', 'ScreenY')
        self.appendLbp('gen', 'stripchartHours')
        #s.appendLbp('gen','connectCommand'    )
        self.setLayout(self.vbox)

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
class LabelPair(QWidget):

    def __init__(self, tagText=None, value=None, parent=None, bgcolor=None,
                 fgcolor=None, font=None):

        super(LabelPair, self).__init__(parent)

        self.debug = 0
        if self.debug > 1:
            print("<editConfig.labelPair__init__>", tagText, value, parent)

        self.valText = str(value)
        self.tagText = tagText

        self.tagwd = 350
        self.taght = 20
        self.valwd = 125
        self.valht = 20

        if self.debug:
            print("........................................")
            print("labelPair.value    :", value)
            print("labelPair.valText  :", self.valText)

        self.lbltag = QLabel(tagText)
        self.lineEdit = QLineEdit(self)
        if self.valText is not None:
            if self.debug: print("valtext :", self.valText)
            self.lineEdit.setText(self.valText)
        else:
            self.lineEdit.setText(QString("***"))

        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(20)
        self.hbox.addStrut(20)
        #s.hbox.setGeometry(QRect(0,0,0,350))
        self.hbox.addWidget(self.lineEdit)
        self.hbox.addWidget(self.lbltag)

        #s.lbltag.setMinimumSize(QSize(s.tagwd, s.taght))
        #s.lbltag.setMaximumSize(QSize(s.tagwd, s.taght))

        self.lbltag.setFixedSize(QSize(self.tagwd, self.taght))
        self.lineEdit.setFixedSize(QSize(self.valwd, self.valht))
        self.lbltag.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lineEdit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbltag.setMargin(0)
        self.lbltag.setIndent(0)
        self.lineEdit.setAlignment(Qt.AlignRight)
        #s.lineEdit.setTextMargins(0,0,0,0)
        self.lineEdit.setStyleSheet("selection-background-color: %s" %
                                    "#000000")
        self.lineEdit.setStyleSheet("background-color: %s" % Kst.MWINBKGCOLOR)

        self.set_tagStyle()
        self.hbox.addWidget(self.lbltag)
        self.setLayout(self.hbox)

        #.......................................................................
        self.palette = QPalette()
        self.brush = QBrush(QColor(0, 255, 0))
        self.brush.setStyle(Qt.SolidPattern)
        self.palette.setBrush(QPalette.Active, QPalette.ButtonText, self.brush)
        self.palette.setBrush(QPalette.Active, QPalette.WindowText, self.brush)
        self.palette.setBrush(QPalette.Active, QPalette.Text, self.brush)

        self.connect(self.lineEdit, SIGNAL("selectionChanged()"),
                     self.changedSelection)
        self.connect(self.lineEdit, SIGNAL("cursorPositionChanged(int,int)"),
                     self.cursorMoved)
        self.connect(self.lineEdit, SIGNAL("editingFinished()"),
                     self.editFinished)
        self.connect(self.lineEdit, SIGNAL("textEdited()"), self.textEdited)
        self.connect(self.lineEdit, SIGNAL("textChanged()"), self.updateVal)
        self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.returned)

    def setValue(self, value):
        if self.debug > 2: print("<labelPair.setValue>", value)
        self.lineEdit.setText(value)

    def editFinished(self):
        if self.debug > 2:
            print("<labelPair>.editFinished", self.lineEdit.text())
        text = self.lineEdit.text()

        # Replace textual 'None' with python type None
        if text == 'None':
            self.valText = None
        else:
            self.valText = text

    def changedSelection(self):
        if self.debug > 2:
            print("*** Changed selection ***", self.lineEdit.text())
        pass

    def returned(self):
        if self.debug > 2:
            print("*** returned ***", self.lineEdit.text())
        pass

    def updateVal(self):
        if self.debug > 2:
            print("*** updateVal ***", self.lineEdit.text())
        pass

    def textEdited(self):
        if self.debug > 2:
            print("*** text Edited ***", self.lineEdit.text())
        pass

    def cursorMoved(self, c1, c2):  # sig:editingFinished()
        if self.debug > 2:
            print("*** cursorMoved ***", c1, c2, self.lineEdit.text())
        pass

    #...........................................................................
    #
    #...........................................................................
    def setFont(self, lbl, font="Arabic Newspaper", size=10):
        self.font = QFont()
        self.qfont.setFamily(_fromUtf8(font))
        self.qfont.setPointSize(size)

    #...........................................................................
    #
    #...........................................................................
    def set_tagStyle(self):
        lbl = self.lbltag
        #lbl.setFrameShape(QFrame.Box)
        #lbl.setFrameShadow(QFrame.Sunken)
        #lbl.setMidLineWidth(1)

        lbl.setStyleSheet( \
          _fromUtf8("background-color: rgb(AOAOAO); color:rgb(0,0,0);"))

        lbl.setAutoFillBackground(False)
        lbl.setGeometry(QRect(self.taght, self.tagwd, self.taght, self.tagwd))
        lbl.setMidLineWidth(1)
        lbl.setLineWidth(1)

        font = "Arabic Newspaper"
        fontSize = 10
        qfont = QFont()
        qfont.setFamily(_fromUtf8(font))
        qfont.setPointSize(fontSize)
        lbl.setFont(qfont)

        #s.lblval.setTextInteractionFlags(Qt.NoTextInteraction)

    def set_valStyle(self):
        lbl = self.lblval
        lbl.setGeometry(QRect(self.taght, self.tagwd, self.taght, self.tagwd))

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
class DictLabelPair(LabelPair):

    def __init__(self, D, pkey, key, parent=None, bgcolor=None, fgcolor=None,
                 font=None):

        self.cfg = Configuration.cfg
        if self.cfg.debug > 9: print("<DictLabelPair__init__>", pkey, key)
        super(DictLabelPair, self).__init__(D[pkey][key]['label'],
                                            D[pkey][key]['value'], parent)
        self.D = D
        self.pkey = pkey
        self.key = key

    #-..........................................................................
    def setDictValue(self, value):
        if self.cfg.debug:
            print("<DictLabelPair.setDictValue>:", self.pkey, self.key, value)

        if value == None or value == 'None':
            self.D[self.pkey][self.key]['value'] = None
        else:
            self.D[self.pkey][self.key]['value'] = util.stringValue(str(value))

    #-..........................................................................
    def editFinished(self):
        if self.cfg.debug:
            print("<DictLabelPair>editFinished", self.lineEdit.text())
        value = self.lineEdit.text()
        if self.cfg.debug: print("    value:", value)
        self.setDictValue(value)
        self.cfg.setCfgFromDict()  # Dict ---> Config dict


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
