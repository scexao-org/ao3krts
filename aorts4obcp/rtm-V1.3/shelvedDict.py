#!/usr/bin/python
#===============================================================================
# File:
#
#===============================================================================
from __future__ import absolute_import, print_function, division

import shelve
import pprint
import DictUtils
import os


#-------------------------------------------------------------------------------
# class shelvedDict
#-------------------------------------------------------------------------------
class shelvedDict(object):

    def __init__(s, fpath):
        super(shelvedDict, s).__init__()
        s.fpath = fpath
        s.D = None

    #...........................................................................
    # Open stored dictionary. s.D = dictionary
    # On exception s.D = None
    # If new is False, return False on no such file
    #...........................................................................
    def open(s, create=False):
        if not create:
            if not os.path.exists(s.fpath):
                #print("Dictionary file:%s does not exist."%s.fpath)
                s.D = None
                return (False)

        # open old file or create new
        try:
            s.D = shelve.open(s.fpath, writeback=False)
        except Exception as exc:
            print("Read dictionary error. Problem opening dictionary file:%s:%s"
                  % (s.fpath, exc))
            s.D = None
            return False

        return True

    #...........................................................................
    def sync(s):
        print("SYNC DICT")
        try:
            s.D.sync()
        except Exception as exc:
            print("Sync dictionary error. Exception synchronising dictionary file:%s:%s"
                  % (s.fpath, exc))

    #...........................................................................
    def close(s):
        try:
            s.D.close()
        except Exception as exc:
            print("Close dictionary error. Exception closing dictionary file:%s:%s"
                  % (s.fpath, exc))
        s.isOpen = False

    #...........................................................................
    # Shelve new dictionary
    def set(s, newDict):

        # open or create stored-dict. s.D = dictionary or None
        s.open(create=True)
        if s.D is None:
            print("<set new dict> Could not open file:%s" % s.fpath)
            return False

        #print("len pre clear:", len(s.D))
        s.D.clear()
        #print("len post clear :", len(s.D))
        for key in newDict.keys():
            s.D[key] = newDict[key]

        #print("len post set :", len(s.D))
        s.D.sync()
        return True

    #...........................................................................
    def printD(s):
        #print("Dict:", pprint.pprint(s.D))
        #pprint.pprint(s.D, indent=4, width=20, depth=1)

        print("Dict:")
        pprint.pprint(s.D)

    #...........................................................................
#    def setNewDict2( dct ):
#        d = shelve.open( s.fpath, writeback=True)
#        d.clear()
#        d['key1'] = 1
#        d['key2'] = 'two'

    def stats(s):
        print("file:", s.fpath)
        if s.D is None:
            print("D is none")
        else:
            print("D Len:", len(s.D))

    def writeDict(s, fpath, theDict, top="# Dictionary data\n", logger=None):
        s.D.sync()

    def readDict(fpath):
        s.open(create=False)


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
    shd = shelvedDict(DICTNAME)
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
