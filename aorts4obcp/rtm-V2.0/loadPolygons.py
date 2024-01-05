#===============================================================================
# File : MirrorWidet_loader.py
#      : Get polygon data from file to QPolygon list
#===============================================================================
from __future__ import absolute_import, print_function

from PyQt4.QtGui import QPolygon
import Configuration


#----------------------------------------------------------------------
# MirrorWidget_loader
#----------------------------------------------------------------------
class MirrorWidget_loader(object):

    def __init__(self, pfactor=0):
        self.cfg = Configuration.cfg
        if self.cfg.debug: print("< MirrorWidget_loader__init__ >")
        self.polygons = []
        self.pFactor = pfactor  # adjust polygon points by adding this value
        polygonFp = open(self.cfg.polygonPath, 'r')
        self.load_polygons(polygonFp)

    #--------------------------------------------------

    #
    #--------------------------------------------------
    def load_polygons(self, file_ptr):
        if self.cfg.debug: print("< MirrorWidget_loader.load_polygons >")
        polygon_points = []
        for line in file_ptr:
            plist = self.getInt(line)  # returns list of pgon-points
            self.polygons.append(QPolygon(plist))

        #s.findMinMax()

    #--------------------------------------------------
    # return line (from polygon file) as a list of integers
    # with each element alterred by pFactor
    #--------------------------------------------------
    def getInt(self, line):
        value = ''
        ret_val = []
        for a in line:
            if ((a == " ") | (a == "\n") | (a == "\t")):
                if (value != ''):
                    ret_val.append((int(value) + self.pFactor))
                value = ''
            else:
                value = value + a
        return ret_val

    def prnPolygons(self):
        print("....................................")
        print("       Polygon Vertices")
        print("....................................")
        for plist in self.polygons:
            for p in plist:
                print(p.x(), p.y())
            print("....................................")


#--------------------------------------------------

    def findMinMax(self):
        self.max_x = self.max_y = 0
        self.min_x = self.min_y = 9999999

        for plst in self.polygons:
            for p in plst:
                x = p.x()
                y = p.y()

            if y < self.min_x:
                self.min_x = x
            if x < self.min_y:
                self.min_y = y
            if x > self.max_x:
                self.max_x = x
            if y > self.max_y:
                self.max_y = y

        print("max X:", self.max_x, "min X:", self.min_x)
        print("max Y:", self.max_y, "min Y:", self.min_y)
