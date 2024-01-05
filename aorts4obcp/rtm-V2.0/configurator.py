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

import os

#import CmdlineOptions
import Configuration
import DictUtils as du
import Constants as Kst

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

    def __init__(self, configFile, logpath, logger, parent=None):

        self.cfg = Configuration.cfg  # create configuration instance
        self.cfg.lg = logger  # give logger to configuration
        self.cfg.logpath = logpath  # give logpath to configuration
        self.cfg.versionS = str(Kst.VERSION)  # version number

        # Get file-path info to configuraton
        (self.cfg.execdir, self.cfg.execname, self.cfg.execpath,
         self.cfg.execpfx, self.cfg.homedir, self.cfg.cwd) = util.setPaths()

        # Set path to config file which may or may not exist yet
        self.cfg.configpath = "%s/%s" % (Kst.SOURCEFOLDER, configFile)

        # where to find get mirror 'eyeball' polygons
        #s.cfg.polygonPath= "%s/%s"%(s.cfg.execdir, Kst.POLYGONFILE)
        self.cfg.polygonPath = "%s/%s" % (Kst.SOURCEFOLDER, Kst.POLYGONFILE)

        # Copy the configuration default dictionary
        #s.cfg.cfgD = deepcopy(defaultConfig.dfltConfigD)

        ## create shelved dictionary instance. Don't open/create file yet
        # s.cfg.shd  = shd.shelvedDict(s.cfg.configpath)
        ## Open or create configuration-dictionary file.
        # If no such file, open(create=FALSE)  returns False
        #configFileExists =  s.cfg.shd.open(create=False)

        # check for yaml config file
        configFileExists = os.path.exists(self.cfg.configpath)

        if not configFileExists:
            # No config file was found, so create one from default dict

            # tell user what we're doing
            self.cfg.lg.info("o Config file not found")
            self.cfg.lg.info("  Create default config-file: %s" %
                             self.cfg.configpath)

            # set config dictionary from default
            self.cfg.cfgD = deepcopy(defaultConfig.dfltConfigD)

            # yaml-ize the default configuration dictionary to a file
            with open(self.cfg.configpath, 'w') as fs:
                rtn = yaml.dump(defaultConfig.dfltConfigD, fs)

            # we no longer use the shelve dictionary module
            # s.cfg.shd.set(s.cfg.cfgD)
            # s.cfg.shd.close()           # close and write it

        #
        else:  # get dictionary from config file
            self.cfg.lg.info("o Configuration from file  : %s" %
                             self.cfg.configpath)

            # copy shelved dict values to _configDict
            #d = s.cfg.shd.D
            #for key in d.keys():
            #    s.cfg.cfgD[key] = d[key]

            fs = open(self.cfg.configpath, 'r')
            self.cfg.cfgD = deepcopy(yaml.load(fs))
            fs.close()

            #print("CONFIGPATH:", s.cfg.cfgD['gen']['configpath']['valu'])
        # set values from dict. Override cmdline opts
        self.cfg.setCfgFromDict()  # set config values from dict
        self.cfg.set_cmdline_overrides()  # override with cmdline opts
        self.cfg.setDictFromCfg()  # now set any changes

    #---------------------------------------------------------------------------
    def dict_prn(self, D):
        du.printDict(D)


#-------------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    configurer = Configurer()
    configurer.cfg.prn_cfg()
    cfg = configurer.cfg
