#------------------------------------------------------------------------------
from __future__ import absolute_import, print_function, division

import math
from PyQt4.QtGui import QX11Info


class Xinfo(QX11Info):

    def __init__(s):
        print("<Xinfo.__init__>")
        super(Xinfo, s).__init__()

    def list_info(s):
        print("defaul tColormap: ", s.defaultColormap())
        print("default Visual  : ", s.defaultVisual())
        print("Colormap handle : ", s.colormap())
        print("depth           : ", s.depth())
        print("screen          : ", s.screen())
        print("visual          : ", s.visual())  # sip.voidptr
        print("\n")
        print("------------- Application -------------")
        print("Cells           : ", s.appCells())
        print("Class           : ", s.appClass())
        print("Colormap handle : ", s.appColormap())
        print("Default Visual  : ", s.appDefaultVisual())
        print("Depth           : ", s.appDepth())
        print("DpiX            : ", s.appDpiX())
        print("DpiY            : ", s.appDpiX())
        print("Root Window     : ", s.appRootWindow())
        print("Screen          : ", s.appScreen())
        print("Time            : ", s.appTime())
        print("User Time       : ", s.appUserTime())
        print("Visual          : ", s.appVisual())
        print("Display         : ", s.display())
        print("Composition Mgr Running : ", s.isCompositingManagerRunning())

        #setAppDpiX (int screen, int dpi)
        #setAppDpiY (int screen, int dpi)
        #setAppTime (int time)
        #setAppUserTime (int time)

        #display = s.display()
        #visual  = s.Visual
