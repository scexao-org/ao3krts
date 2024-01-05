#!/usr/bin/python
#===============================================================================
# File: Configurer.py
#     : Read configuration file. Load cfg values in dynamic Configuration
#
#
#http://stackoverflow.com/questions/3409856/accessing-dictionaries-vs-accessing-shelves
# This code doesn't work as expected with a shelf, but works with a dictionary:
#s["foo"] = MyClass()
#s["foo"].X = 8
#p = s["foo"] # store a reference to the object
#p.X = 9 # update the reference
#s.sync() # flushes the cache
#p.X = 0
#print "value in memory: %d" % p.X # prints 0
#print "value in shelf: %d" % s["foo"].X # prints 9
#
# Also see: Configuration.py
#===============================================================================

import sys, os, string

#import CmdlineOptions
import Configuration
import DictUtils as du
import Constants as Kst
import shelvedDict as shd
from copy import deepcopy
import defaultConfig
import util
import yaml


#-------------------------------------------------------------------------------
# Configurer
#-------------------------------------------------------------------------------
class Configurer(object):
    """Load configuration dictionary from default module or file
       Set configuration values.
    """

    def __init__(s, configFile, logpath, logger, parent=None):

        s.cfg = Configuration.cfg  # create configuration instance
        s.cfg.lg = logger  # give logger to configuration
        s.cfg.logpath = logpath  # give logpath to configuration
        s.cfg.versionS = str(Kst.VERSION)  # version number

        # Get file-path info to configuraton
        (s.cfg.execdir, s.cfg.execname, s.cfg.execpath, s.cfg.execpfx,
         s.cfg.homedir, s.cfg.cwd) = util.setPaths()

        # Set path to config file which may or may not exist yet
        s.cfg.configpath = "%s/%s" % ("/home/ao/ao188/src/rtm/rtm-V1.3",
                                      configFile)

        # where to find get mirror 'eyeball' polygons
        #s.cfg.polygonPath= "%s/%s"%(s.cfg.execdir, Kst.POLYGONFILE)
        s.cfg.polygonPath = "%s/%s" % ("/home/ao/ao188/src/rtm/rtm-V1.3",
                                       Kst.POLYGONFILE)

        # Copy the configuration default dictionary
        #s.cfg.cfgD = deepcopy(defaultConfig.dfltConfigD)

        ## create shelved dictionary instance. Don't open/create file yet
        # s.cfg.shd  = shd.shelvedDict(s.cfg.configpath)
        ## Open or create configuration-dictionary file.
        # If no such file, open(create=FALSE)  returns False
        #configFileExists =  s.cfg.shd.open(create=False)

        # check for yaml config file
        configFileExists = os.path.exists(s.cfg.configpath)

        if not configFileExists:
            # No config file was found, so create one from default dict

            # tell user what we're doing
            s.cfg.lg.info("o Config file not found")
            s.cfg.lg.info("  Create default config-file: %s" % s.cfg.configpath)

            # set config dictionary from default
            s.cfg.cfgD = deepcopy(defaultConfig.dfltConfigD)

            # yaml-ize the default configuration dictionary to a file
            fs = file(s.cfg.configpath, 'w')
            rtn = yaml.dump(defaultConfig.dfltConfigD, fs)
            fs.close()

            # we no longer use the shelve dictionary module
            # s.cfg.shd.set(s.cfg.cfgD)
            # s.cfg.shd.close()           # close and write it

        #
        else:  # get dictionary from config file
            s.cfg.lg.info("o Configuration from file  : %s" % s.cfg.configpath)

            # copy shelved dict values to _configDict
            #d = s.cfg.shd.D
            #for key in d.keys():
            #    s.cfg.cfgD[key] = d[key]

            fs = open(s.cfg.configpath, 'r')
            s.cfg.cfgD = deepcopy(yaml.load(fs))
            fs.close()

            #print("CONFIGPATH:", s.cfg.cfgD['gen']['configpath']['valu'])
        # set values from dict. Override cmdline opts
        s.cfg.setCfgFromDict()  # set config values from dict
        s.cfg.set_cmdline_overrides()  # override with cmdline opts
        s.cfg.setDictFromCfg()  # now set any changes

    #---------------------------------------------------------------------------
    def dict_prn(s, D):
        du.printDict(D)


#   #--------------------------------------------------------------------------
#   # Read config dictionary.
#   #---------------------------------------------------------------------------
#    def read_dict(s,fpath):
#        try: f = open(fpath,'r')
#        except Exception as exc:
#            cfg.lg.error("Couldn't open config file %s: %s" % (fpath, exc))
#            return None
#
#
#        try: theDict = eval(f.read())
#        except Exception as exc:
#            print("Problem reading file:%s" % (fpath), exc)
#            f.close()
#            return None
#
#        f.close()
#        return(theDict)

#-------------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    configurer = Configurer()
    configurer.cfg.prn_cfg()
    cfg = configurer.cfg

#def getApplicationFont():
#    return QFont(Config.fontfamily,
#                 Config.pointsize,
#                 Config.weight,
#                 Config.italic,
#                 Config.encoding )

#def setApplicationFont(qfont):
#     Config.fontfamily = qfont.family()
#     Config.pointsize = qfont.pointSize()
#     Config.weight = qfont.weight()
#     Config.italic = qfont.italic()
#     Config.encoding = qfont.encoding()

#.....................................................
#cfg_items = cfg.items('cfg') )  # get sections items as a list of tuples (including comments)
#print(cfg_items)

## Set as menu item: X11 Info
#Xinfo = X11.Xinfo()
#Xinfo.list_info()
