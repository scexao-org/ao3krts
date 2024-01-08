#===============================================================================
# File : MirrorWidet_loader.py
#      : Get polygon data from file to QPolygon list
#===============================================================================
from __future__ import absolute_import
from __future__ import print_function
#from __future__ import division
import sys
from PyQt4.QtGui import (QPolygon)
import Configuration


#----------------------------------------------------------------------
# MirrorWidget_loader
#----------------------------------------------------------------------
class MirrorWidget_loader(object):

    def __init__(s, pfactor=0):
        s.cfg = Configuration.cfg
        if s.cfg.debug: print("< MirrorWidget_loader__init__ >")
        s.polygons = []
        s.pFactor = pfactor  # adjust polygon points by adding this value
        polygonFp = open(s.cfg.polygonPath, 'r')
        s.load_polygons(polygonFp)

    #--------------------------------------------------

    #
    #--------------------------------------------------
    def load_polygons(s, file_ptr):
        if s.cfg.debug: print("< MirrorWidget_loader.load_polygons >")
        polygon_points = []
        for line in file_ptr:
            plist = s.getInt(line)  # returns list of pgon-points
            s.polygons.append(QPolygon(plist))

        #s.findMinMax()

    #--------------------------------------------------
    # return line (from polygon file) as a list of integers
    # with each element alterred by pFactor
    #--------------------------------------------------
    def getInt(s, line):
        value = ''
        ret_val = []
        for a in line:
            if ((a == " ") | (a == "\n") | (a == "\t")):
                if (value != ''):
                    ret_val.append((int(value) + s.pFactor))
                value = ''
            else:
                value = value + a
        return ret_val

    def prnPolygons(s):
        print("....................................")
        print("       Polygon Vertices")
        print("....................................")
        for plist in s.polygons:
            for p in plist:
                print(p.x(), p.y())
            print("....................................")

#--------------------------------------------------

    def findMinMax(s):
        s.max_x = s.max_y = 0
        s.min_x = s.min_y = 9999999

        for plst in s.polygons:
            for p in plst:
                x = p.x()
                y = p.y()

            if y < s.min_x:
                s.min_x = x
            if x < s.min_y:
                s.min_y = y
            if x > s.max_x:
                s.max_x = x
            if y > s.max_y:
                s.max_y = y

        print("max X:", s.max_x, "min X:", s.min_x)
        print("max Y:", s.max_y, "min Y:", s.min_y)

    #--------------------------------------------------
    # Unused: numpy.loadtxt requires same number of points in each row
    #--------------------------------------------------
    #def npLoad_polygons(s, file_ptr):
    #    import numpy as np
    #    x = np.loadtxt(s.cfg.polygonPath)
    #    for v in x:
    #        s.polygons.append(QPolygon(list(v)))
    #    s.prnPolygons()
