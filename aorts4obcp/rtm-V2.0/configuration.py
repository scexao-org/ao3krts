#===============================================================================
# File: configuration.py
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

import cmdLineOptions as Clo

#import shelvedDict as shd
from yaml import dump as yamlDump


#-------------------------------------------------------------------------------
# CLASS configuration : Dynamic configuration values to be set from .cfg file
#                       or overridden fromcommandline.
#-------------------------------------------------------------------------------
class configuration(object):

    def __init__(self, parent=None):
        super(configuration, self).__init__()
        self.cfgD = None  # to be set by configurator
        self.logpath = None
        self.lg = None  # to be set by configurator
        self.configpath = None  # from constants
        self.libpath = None  # unused
        self.debug = None  # from cmdLine
        self.test = None  # from cmdline

    #---------------------------------------------------------------------------
    # Set program variables from configuration dictionary
    #---------------------------------------------------------------------------
    def setCfgFromDict(self):
        if self.debug:
            print("<configuration.setCfgFromDict>")
        #
        d = self.cfgD

        self.rtDataHost = d['gen']['rtDataHost']['value']
        self.rtDataPort = int(d['gen']['rtDataPort']['value'])

        self.ScreenX = int(d['gen']['ScreenX']['value'])
        self.ScreenY = int(d['gen']['ScreenY']['value'])
        self.framesPerEye = int(d['gen']['framesPerEye']['value'])
        self.framesPerLabel = int(d['gen']['framesPerLabel']['value'])
        self.framesPerChart = int(d['gen']['framesPerChart']['value'])
        self.framesPerMountPlot = int(d['gen']['framesPerMountPlot']['value'])
        self.framesPerSH = int(d['gen']['framesPerSH']['value'])
        self.framesPerSHArrow = int(d['gen']['framesPerSHArrow']['value'])
        self.framesPerDefocusUpdate = 5

        #s.dm_alarmHi    = s.setFloat(s.get_dictValue('dmeye','alarmHi'       ))
        #s.dm_alarmLow   = s.setFloat(s.get_dictValue('dmeye','alarmLow'      ))
        #s.crv_alarmHi   = s.setFloat(s.get_dictValue('crveye','alarmHi'      ))
        #s.crv_alarmLow  = s.setFloat(s.get_dictValue('crveye','alarmLow'     ))
        #s.apd_alarmHi   = s.setFloat(s.get_dictValue('apdeye','alarmHi'      ))
        #s.apd_alarmLow  = s.setFloat(s.get_dictValue('apdeye','alarmLow'     ))
        #s.sh_alarmHi    = s.setFloat(s.get_dictValue('sheye','alarmHi'       ))
        #s.sh_alarmLow   = s.setFloat(s.get_dictValue('sheye','alarmLow'      ))
        self.debug = int(d['gen']['debug']['value'])

        self.tags = self.tags_to_tuple(self.cfgD)

    #---------------------------------------------------------------------------
    # setDictFromCfg : called only from configurator.py
    # set commandline options in dictionary
    #---------------------------------------------------------------------------
    def setDictFromCfg(self):
        if self.debug:
            print("<configuration.setDictFromCfg>")
            print("-----------------------------------------------------------")
        dct = self.cfgD
        #dct['gen']['configpath']['value']      = s.logpath # !!! ???
        dct['gen']['debug']['value'] = int(self.debug)
        dct['gen']['verbose']['value'] = int(self.verbose)

    # yaml-ize the default configuration dictionary to a file
    def saveConfigDict(self):

        #s.Lskt.notify_connect.setEnabled(False)
        #s.Lskt.EvlSc.notify_read.setEnabled(False)
        #s.Lskt.EvlSc.notify_write.setEnabled(False)
        with open(self.configpath, 'w') as fs:
            rtn = yamlDump(self.cfgD, fs)

        # FileWrite stops action on connected data socket, re-enable
        print('s.Lskt.EvlSc', self.Lskt.EvlSc)
        if self.Lskt.EvlSc is not None:
            self.Lskt.EvlSc.notify_read.setEnabled(True)

        #s.Lskt.EvlSc.notify_write.setEnabled(True)
        #s.Lskt.notify_connect.setEnabled(True)

    #---------------------------------------------------------------------------
    def setFloat(self, value):
        if value is None:
            return (None)
        if value == 'None':
            return (None)
        return float(value)

    #---------------------------------------------------------------------------
    #  get_dictValue sectionKey, itemKey : return config item value
    #---------------------------------------------------------------------------
    def get_dictValue(self, sectionKey, itemKey):

        value = self.cfgD[sectionKey][itemKey]['value']
        if self.debug > 2:
            print("<configuration.get_dictValue>", sectionKey, itemKey, value)
        if value is None:
            return None
        return value

    #---------------------------------------------------------------------------
    #  debug is initially set by configurator from commandline opts
    #---------------------------------------------------------------------------
    def set_cmdline_overrides(self):

        if self.debug:
            print("<configuration.set_cmdline_overrides>")
        if Clo.debug is not None:
            self.debug = int(Clo.debug)
        else:
            self.debug = 0

        if Clo.test is not None:
            self.test = Clo.test
        else:
            self.test = 0

        if Clo.verbose is not None:
            self.verbose = int(Clo.verbose)
        else:
            self.verbose = int(0)

        if Clo.logpath is not None:
            self.logpath = Clo.logpath

        if Clo.libpath is not None:
            self.libpath = Clo.libpath

        if Clo.port is not None:
            self.port = int(Clo.port)

        if self.debug:
            Clo.prn_options()

    #---------------------------------------------------------------------------
    def prn_cfg(self):
        print("---------------------------------------------------------------")
        print("                   configuration                               ")
        print("---------------------------------------------------------------")
        print("%-12s: %s" % ("Logpath", self.logpath))
        #print("%-12s: %s"% ("Libpath" ,  s.libpath))
        print("%-12s: %s" % ("Port", self.port))
        print("%-12s: %s" % ("Debug", self.debug))
        print("%-12s: %s" % ("Verbose", self.verbose))
        print("%-12s: %s" % ("Test", self.test))
        print("---------------------------------------------------------------")
        if self.debug > 3:
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
    def get_row_column_data(self, row, column):
        if self.debug > 2:
            print("<configuration.get_row_column_data>", row, column)

        # Get section number for given row
        rowcount = 0
        for sectionNdx in range(self.nsections):
            nrows = len(self.dkeys[sectionNdx + 2])
            datumNdx = row - rowcount
            rowcount += nrows
            if row < rowcount:
                break
        datum = self.get_datum(sectionNdx, datumNdx)
        x = datum[column]
        return (x)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def get_datum(self, sectionNdx, datumNdx):
        # DM,CRV,GEN=range(3)
        if self.debug > 2: print("<configuration.get_value>")

        DICT, SECTION, LABEL, DATUM = list(range(4))

        labelNdx = sectionNdx + 2
        sectionKey = self.tags[SECTION][sectionNdx]
        datumKey = self.tags[labelNdx][datumNdx]

        label = self.cfgD[sectionKey][datumKey]['label']
        typ = self.cfgD[sectionKey][datumKey]['type']
        value = self.cfgD[sectionKey][datumKey]['value']
        desc = self.cfgD[sectionKey][datumKey]['desc']

        if self.debug > 2:
            print("    sectionNdx:%d datumNdx:%d" % (sectionNdx, datumNdx))
            print("    sectionKey:%s datumKey:%s" % (sectionKey, datumKey))
            print("    Label:", label)
            print("    typ  :", typ)
            print("    Value:", value)

        return ((label, value, desc, typ))

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def tags_to_tuple(self, D):
        if self.debug:
            print("<configuration.tags_to_tuple>")

        dicts = {'D0': D}
        topkeys = ('D0', )
        dkeys = copy.copy(topkeys)
        keylist = [topkeys]
        ndicts = len(keylist)
        for i in range(ndicts):
            try:
                k = list(dicts[topkeys[i]].keys())
            except Exception as exc:
                print("<configuration.tags_to_tuple> Exception:", exc)
                continue
            keylist.append(tuple(k))

        dkeys = copy.copy(keylist)
        self.nsections = len(k)  # n toplevel dicts
        dictKey = dkeys[0][0]

        for j in range(self.nsections):
            #dict   #section    #var-keys
            try:
                x = list(dicts[dictKey][dkeys[1][j]].keys())
            except Exception as exc:
                print("<Configuraton.tags_to_tuple>", exc)
                continue
            keylist.append(tuple(x))

        dkeys = tuple(keylist)

        #s.nsections = len(dkeys[1])
        self.nrows = 0
        for sectionNdx in range(self.nsections):
            self.nrows += len(dkeys[sectionNdx + 2])
        self.dkeys = dkeys
        return (dkeys)


cfg = configuration()
lg = cfg.lg
