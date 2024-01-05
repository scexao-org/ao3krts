#===============================================================================
# File :
#
#
#
# Notes:
#
#===============================================================================
from __future__ import absolute_import, print_function, division

import os, sys

import zmq

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QSizePolicy
from PyQt5.QtGui import QFont

import Constants as Kst


#
def set_valueLabel_style(lbls):
    fg = " QLabel {color:black}"
    bg = " QLabel {background-color:%s}" % Kst.LBLBKGCOLOR
    #bg     = " QLabel {background-color:transparent}"
    border = " QLabel {border-color:%s}" % '#000000'
    for lbl in lbls:
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt

        lbl.setFrameStyle(QFrame.Box | QFrame.Sunken)

        lbl.setLineWidth(1)
        lbl.setMidLineWidth(0.2)
        lbl.setTextFormat(Qt.RichText)
        lbl.setStyleSheet(fg + bg + border)

        #lbl.setFont(s.cfg.dflt_valuesFont)
        lbl.setFont(QFont("Monospace"))
        lbl.setMinimumWidth(80)

        # Align: Qt. AlignLeft,AlignRight,AlignHCenter,AlignJustify
        lbl.setAlignment(Qt.AlignCenter)


# change name ==> labels_labelStyle(lblsList,)
# 'selection-background-color'
def set_staticLabel_style(lbls):
    fg = " QLabel {color:black}"
    #bg     = " QLabel {background-color:%s}" % Kst.LBLBKGCOLOR
    bg = " QLabel {background-color:transparent}"
    border = " QLabel {border-color:%s}" % '#000000'
    #font = cfg.cfg.dflt_labelsFont
    font = QFont("Monospace")
    for lbl in lbls:
        #font = lbl.setFont(QFont("Monospace"))
        lbl.setFont(font)
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  #hrz,vrt
        lbl.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        lbl.setTextFormat(Qt.RichText)

        lbl.setStyleSheet(fg + bg + border)

        lbl.setMaximumHeight(16)

        # Font

        #font().setBold(False)
        #font().setPixelSize()
        #font().setPointSize(4)
        #font().setWeight(0)


def set_label_background(lbls, rgbstring):
    #font = cfg.QFont("Times", pointSize=10, weight=QFont.Bold, italic=False)
    fg = " QLabel {color:black}"
    bg = " QLabel {background-color:%s}" % rgbstring
    border = " QLabel {border-color:%s}" % '#000000'
    for lbl in lbls:
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  #hrz,vrt
        lbl.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        lbl.setTextFormat(Qt.RichText)
        #lbl.setStyleSheet( fg+bg )
        lbl.setStyleSheet(fg + bg + border)
        lbl.setStyleSheet(bg)
        lbl.setMaximumHeight(16)

        #lbl.setFont(font)
        #lbl.setFont(QFont("Monospace"));

        #lbl.setFrameStyle(QFrame.StyledPanel | QFrame.Raised);
        #lbl.setFrameStyle(QFrame.Panel | QFrame.Raised);
        #lbl.setFrameStyle(QFrame.Box | QFrame.Raised);


#^------------------------------------------------------------------------------
# return value based on string type
#
#  given  return
#  -----+-------
#  None   None
# 'None'  None
# 'none'  None
# '1234'  int(1234
# '123.4  float(123.4)
# 'xyz.a' 'xyz.a'
# '1.2.3' '1.2.3'
#
#-------------------------------------------------------------------------------
def stringValue(s):

    #NONE
    if s is None:
        pass

    # INT
    elif s.isdigit():
        s = int(s)

    # STRING or NONE if 'None' or 'none'
    elif s.isalpha():  # is string
        if s == 'None' or s == 'none':
            s = None

    # STRING
    elif s.isalnum():
        pass

    # FLOAT if one decimal point and all numeric else STRING
    # eg: '12.3.4' returns '12.3.4'
    elif '.' in s:
        try:
            s = float(s)

            # catch more than one decimal-point : eg: 123.45.67
            # catch decimal and alpahnumerics   : eg: abc.def
        except:
            pass  # print("String '%-10s' : STRING GARBLED FLOAT" % s )
        else:
            pass  # print("String '%-10s' : STRING FLOAT" % s )
    else:
        print("String '%-10s' : NOT DIGIT" % s)

    return (s)


#def string_is_number(s):
#    try:
#        float(s)
#        return True
#    except ValueError:
#        return False


# Return the full directory path of the executable regardles of how
# invoked.
# Ie. regardless of relative paths, symbolic links, ets
def setExecDirectory():
    import sys, os
    return (os.path.dirname(os.path.realpath(sys.argv[0])))


#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def setPaths():

    debug = False

    execdir = setExecDirectory()  # full executable dir path

    # real executable name, not symbolic link
    execpath = os.path.realpath(sys.argv[0])
    #execname = os.path.basename(os.path.realpath(sys.argv[0]))
    execname = os.path.basename(execpath)
    lst = execname.split('.')  # get list of strings split by '.'
    execpfx = lst[0]  # use the first one as execfile prefix
    homedir = os.getenv("HOME")
    cwd = os.getcwd()

    if debug:
        print("<util> setPaths")
        print("ARGV0   :", sys.argv[0])
        print("EXECDIR :", execdir)
        print("EXECNAME:", execname)
        print("EXECPFX :", execpfx)
        print("HOMEDIR :", homedir)
        print("CWD     :", cwd)

    return (execdir, execname, execpath, execpfx, homedir, cwd)
