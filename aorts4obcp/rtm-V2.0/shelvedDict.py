#!/usr/bin/python
#===============================================================================
# File:
#
#===============================================================================
from __future__ import absolute_import, print_function, division

import shelve
import pprint

import os


#-------------------------------------------------------------------------------
# class shelvedDict
#-------------------------------------------------------------------------------
class ShelvedDict(object):

    def __init__(self, fpath):
        super(ShelvedDict, self).__init__()
        self.fpath = fpath
        self.D = None

    #...........................................................................
    # Open stored dictionary. s.D = dictionary
    # On exception s.D = None
    # If new is False, return False on no such file
    #...........................................................................
    def open(self, create=False):
        if not create:
            if not os.path.exists(self.fpath):
                #print("Dictionary file:%s does not exist."%s.fpath)
                self.D = None
                return (False)

        # open old file or create new
        try:
            self.D = shelve.open(self.fpath, writeback=False)
        except Exception as exc:
            print("Read dictionary error. Problem opening dictionary file:%s:%s"
                  % (self.fpath, exc))
            self.D = None
            return False

        return True

    #...........................................................................
    def sync(self):
        print("SYNC DICT")
        try:
            self.D.sync()
        except Exception as exc:
            print("Sync dictionary error. Exception synchronising dictionary file:%s:%s"
                  % (self.fpath, exc))

    #...........................................................................
    def close(self):
        try:
            self.D.close()
        except Exception as exc:
            print("Close dictionary error. Exception closing dictionary file:%s:%s"
                  % (self.fpath, exc))
        self.isOpen = False

    #...........................................................................
    # Shelve new dictionary
    def set(self, newDict):

        # open or create stored-dict. s.D = dictionary or None
        self.open(create=True)
        if self.D is None:
            print("<set new dict> Could not open file:%s" % self.fpath)
            return False

        #print("len pre clear:", len(s.D))
        self.D.clear()
        #print("len post clear :", len(s.D))
        for key in newDict.keys():
            self.D[key] = newDict[key]

        #print("len post set :", len(s.D))
        self.D.sync()
        return True

    #...........................................................................
    def printD(self):
        #print("Dict:", pprint.pprint(s.D))
        #pprint.pprint(s.D, indent=4, width=20, depth=1)

        print("Dict:")
        pprint.pprint(self.D)

    #...........................................................................
#    def setNewDict2( dct ):
#        d = shelve.open( s.fpath, writeback=True)
#        d.clear()
#        d['key1'] = 1
#        d['key2'] = 'two'

    def stats(self):
        print("file:", self.fpath)
        if self.D is None:
            print("D is none")
        else:
            print("D Len:", len(self.D))

    def writeDict(self, fpath, theDict, top="# Dictionary data\n", logger=None):
        self.D.sync()

    def readDict(self, fpath):
        self.open(create=False)


#-------------------------------------------------------------------------------
# Main: for test
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    print(" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("{             Test shelvedDict.py                                }")
    print(" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    d = {'one': 1, 'two': 2}

    import defaultConfig
    import sys
    DICTNAME = 'rtmConfig.db'

    print("........................................................")
    shd = ShelvedDict(DICTNAME)
    shd.open(new=False)
    shd.printD()

    print("........................................................")

    shd.set(d)  #shd.set( defaultConfig.dfltConfigD )
    shd.printD()
    sys.exit()

    print("........................................................")
    shd.sync()
    shd.close()
    shd.open()

    sys.exit()
    print("........................................................")
    shd.open()
    shd.stats()
    shd.printD()
    print("........................................................")
    shd.D['three'] = 3
    shd.printD()

    print("........................................................")
    #shd.close()
    #shd.open()
    #shd.printD()
