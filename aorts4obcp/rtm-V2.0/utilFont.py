#===============================================================================
# File : utilFont.py
#
# Notes:
#
#===============================================================================
#
# QFont.StyleHint
# Style hints are used by the font matching algorithm to find
# an appropriate default family if a selected font family is not available.
# hint = QFont.StyleHint
#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qfont.html#StyleHint-enum

# ('pixelSize :', 11)
# ('pointSize :', 9)
# ('fixedPitch:', True)
# ('Bold      :', False)

from PyQt4.QtGui import QFont


# see QFont.QFontInfo
#     QFont.StyleHint
def print_StyleHint(styleHint):
    if styleHint == QFont.AnyStyle:
        print("StyleHint=AnyStyle")
        print("""
                 Leaves the font matching algorithm to choose the family.
                 This is the default.
              """)


# info = QFontInfo
def printFontInfo(info):

    info = QFont.QFontInfo()
    print("---------- FontInfo ----------")
    print("Family    :", info.family())
    print("exactMatch:", info.exactMatch())
    print("pixelSize :", info.pixelSize())
    print("pointSize :", info.pointSize())
    print("fixedPitch:", info.fixedPitch())
    print("weight    :", info.weight())
    print("Bold      :", info.bold())
    print("italic    :", info.italic())
    print("rawMode   :", info.rawMode())
    print("style     :", info.style())

    print("--------- FontMetrics---------")
    #QFontMetrics metrics
    #metrics = font.QFontMetrics(font)


#('Family    :', PyQt4.QtCore.QString(u'DejaVu Sans Mono'))
#('exactMatch:', False)
#('pixelSize :', 11)
#('pointSize :', 9)
#('fixedPitch:', True)
#('Bold      :', False)
#('italic    :', False)
#('rawMode   :', False)
#('style     :', 0)
#('styleHint :', 5)
#
#
#
#
#
#
