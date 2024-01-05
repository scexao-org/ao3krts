#===============================================================================
# File: Configuration.py
#
# Notes:
#  o Set logging level:
#    cfg.lg.setLevel('level-name') where level-name is one of
#        'CRIT'
#        'ERROR',
#        'WARN',
#        'INFO',
#        'DEBUG',
#    Example: cfg.lg.setLevel('WARN') : Enable levels WARN and all above it.
#                                       i.e. WARN,ERROR,CRIT
#
#===============================================================================

STR, BOOL, INT, FLT = list(range(4))  # data types

import copy
from PyQt4.QtGui import (QColor, QFont)
import Constants as Kst
import Logger
import CmdlineOptions as Clo
import DictUtils as du
#import shelvedDict as shd
from yaml import dump as yamlDump


#-------------------------------------------------------------------------------
# CLASS Configuration : Dynamic configuration values to be set from .cfg file
#                       or overridden fromcommandline.
#-------------------------------------------------------------------------------
class Configuration(object):

    def __init__(s, parent=None):
        super(Configuration, s).__init__()
        s.cfgD = None  # to be set by Configurer
        s.logpath = None
        s.lg = None  # to be set by Configurer
        s.configpath = None  # from Constants
        s.libpath = None  # unused
        s.debug = None  # from cmdLine
        s.test = None  # from cmdline

    #---------------------------------------------------------------------------
    # Set program variables from configuration dictionary
    #---------------------------------------------------------------------------
    def setCfgFromDict(s):
        if s.debug:
            print("<Configuration.setCfgFromDict>")
        #
        d = s.cfgD

        s.port = int(d['gen']['port']['value'])
        s.ScreenX = int(d['gen']['ScreenX']['value'])
        s.ScreenY = int(d['gen']['ScreenY']['value'])
        s.framesPerEye = int(d['gen']['framesPerEye']['value'])
        s.framesPerLabel = int(d['gen']['framesPerLabel']['value'])
        s.framesPerChart = int(d['gen']['framesPerChart']['value'])
        s.framesPerMountPlot = int(d['gen']['framesPerMountPlot']['value'])
        s.framesPerSH = int(d['gen']['framesPerSH']['value'])
        s.framesPerSHArrow = int(d['gen']['framesPerSHArrow']['value'])
        s.framesPerDefocusUpdate = 5

        #s.dm_alarmHi    = s.setFloat(s.get_dictValue('dmeye','alarmHi'       ))
        #s.dm_alarmLow   = s.setFloat(s.get_dictValue('dmeye','alarmLow'      ))
        #s.crv_alarmHi   = s.setFloat(s.get_dictValue('crveye','alarmHi'      ))
        #s.crv_alarmLow  = s.setFloat(s.get_dictValue('crveye','alarmLow'     ))
        #s.apd_alarmHi   = s.setFloat(s.get_dictValue('apdeye','alarmHi'      ))
        #s.apd_alarmLow  = s.setFloat(s.get_dictValue('apdeye','alarmLow'     ))
        #s.sh_alarmHi    = s.setFloat(s.get_dictValue('sheye','alarmHi'       ))
        #s.sh_alarmLow   = s.setFloat(s.get_dictValue('sheye','alarmLow'      ))
        s.debug = int(s.get_dictValue('gen', 'debug'))

        s.tags = s.tags_to_tuple(s.cfgD)

    #---------------------------------------------------------------------------
    # setDictFromCfg : called only from Configurer.py
    # set commandline options in dictionary
    #---------------------------------------------------------------------------
    def setDictFromCfg(s):
        if s.debug:
            print("<Configuration.setDictFromCfg>")
            print("-----------------------------------------------------------")
        dct = s.cfgD
        #dct['gen']['configpath']['value']      = s.logpath # !!! ???
        dct['gen']['debug']['value'] = int(s.debug)
        dct['gen']['verbose']['value'] = int(s.verbose)
        dct['gen']['port']['value'] = int(s.port)

    # yaml-ize the default configuration dictionary to a file
    def saveConfigDict(s):

        #s.Lskt.notify_connect.setEnabled(False)
        #s.Lskt.EvlSc.notify_read.setEnabled(False)
        #s.Lskt.EvlSc.notify_write.setEnabled(False)
        fs = file(s.configpath, 'w')
        rtn = yamlDump(s.cfgD, fs)
        fs.close()

        # FileWrite stops action on connected data socket, re-enable
        print('s.Lskt.EvlSc', s.Lskt.EvlSc)
        if s.Lskt.EvlSc is not None:
            s.Lskt.EvlSc.notify_read.setEnabled(True)

        #s.Lskt.EvlSc.notify_write.setEnabled(True)
        #s.Lskt.notify_connect.setEnabled(True)

    #---------------------------------------------------------------------------
    def setFloat(s, value):
        if value is None:
            return (None)
        if value == 'None':
            return (None)
        return float(value)

    #---------------------------------------------------------------------------
    #  get_dictValue sectionKey, itemKey : return config item value
    #---------------------------------------------------------------------------
    def get_dictValue(s, sectionKey, itemKey):

        value = s.cfgD[sectionKey][itemKey]['value']
        if s.debug > 2:
            print("<Configuration.get_dictValue>", sectionKey, itemKey, value)
        if value is None:
            return None
        return value

    #---------------------------------------------------------------------------
    #  debug is initially set by Configurer from commandline opts
    #---------------------------------------------------------------------------
    def set_cmdline_overrides(s):

        if s.debug:
            print("<Configuration.set_cmdline_overrides>")
        if Clo.debug is not None:
            s.debug = int(Clo.debug)
        else:
            s.debug = 0

        if Clo.test is not None:
            s.test = Clo.test
        else:
            s.test = 0

        if Clo.verbose is not None:
            s.verbose = int(Clo.verbose)
        else:
            s.verbose = int(0)

        if Clo.logpath is not None:
            s.logpath = Clo.logpath

        if Clo.libpath is not None:
            s.libpath = Clo.libpath

        if Clo.port is not None:
            s.port = int(Clo.port)

        if s.debug:
            Clo.prn_options()

    #---------------------------------------------------------------------------
    def prn_cfg(s):
        print("---------------------------------------------------------------")
        print("                   Configuration                               ")
        print("---------------------------------------------------------------")
        print("%-12s: %s" % ("Logpath", s.logpath))
        #print("%-12s: %s"% ("Libpath" ,  s.libpath))
        print("%-12s: %s" % ("Port", s.port))
        print("%-12s: %s" % ("Debug", s.debug))
        print("%-12s: %s" % ("Verbose", s.verbose))
        print("%-12s: %s" % ("Test", s.test))
        print("---------------------------------------------------------------")
        if s.debug > 3:
            print("")
            print("-----------------------------------------------------------")
            print("              Config Dictionary")
            print("-----------------------------------------------------------")
            #du.printDict(s.cfgD)
            print("-----------------------------------------------------------")
        print("")

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def get_row_column_data(s, row, column):
        if s.debug > 2:
            print("<Configuration.get_row_column_data>", row, column)

        # Get section number for given row
        rowcount = 0
        for sectionNdx in range(s.nsections):
            nrows = len(s.dkeys[sectionNdx + 2])
            datumNdx = row - rowcount
            rowcount += nrows
            if row < rowcount:
                break
        datum = s.get_datum(sectionNdx, datumNdx)
        x = datum[column]
        return (x)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def get_datum(s, sectionNdx, datumNdx):
        # DM,CRV,GEN=range(3)
        if s.debug > 2: print("<Configuration.get_value>")

        DICT, SECTION, LABEL, DATUM = list(range(4))

        labelNdx = sectionNdx + 2
        sectionKey = s.tags[SECTION][sectionNdx]
        datumKey = s.tags[labelNdx][datumNdx]

        label = s.cfgD[sectionKey][datumKey]['label']
        typ = s.cfgD[sectionKey][datumKey]['type']
        value = s.cfgD[sectionKey][datumKey]['value']
        desc = s.cfgD[sectionKey][datumKey]['desc']

        if s.debug > 2:
            print("    sectionNdx:%d datumNdx:%d" % (sectionNdx, datumNdx))
            print("    sectionKey:%s datumKey:%s" % (sectionKey, datumKey))
            print("    Label:", label)
            print("    typ  :", typ)
            print("    Value:", value)

        return ((label, value, desc, typ))

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def tags_to_tuple(s, D):
        if s.debug:
            print("<Configuration.tags_to_tuple>")

        dicts = {'D0': D}
        topkeys = ('D0', )
        dkeys = copy.copy(topkeys)
        keylist = [topkeys]
        ndicts = len(keylist)
        for i in range(ndicts):
            try:
                k = list(dicts[topkeys[i]].keys())
            except Exception as exc:
                print("<Configuration.tags_to_tuple> Exception:", exc)
                continue
            keylist.append(tuple(k))

        dkeys = copy.copy(keylist)
        s.nsections = len(k)  # n toplevel dicts
        dictKey = dkeys[0][0]

        for j in range(s.nsections):
            #dict   #section    #var-keys
            try:
                x = list(dicts[dictKey][dkeys[1][j]].keys())
            except Exception as exc:
                print("<Configuraton.tags_to_tuple>", exc)
                continue
            keylist.append(tuple(x))

        dkeys = tuple(keylist)

        #s.nsections = len(dkeys[1])
        s.nrows = 0
        for sectionNdx in range(s.nsections):
            s.nrows += len(dkeys[sectionNdx + 2])
        s.dkeys = dkeys
        return (dkeys)


cfg = Configuration()
lg = cfg.lg
