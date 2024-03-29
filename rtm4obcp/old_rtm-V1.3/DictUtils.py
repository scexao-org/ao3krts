#!/usr/bin/python
#===============================================================================
# File:
#
#===============================================================================
from __future__ import absolute_import, print_function, division
import json
import pprint
import string
import sys


#---------------------------------------------------------------------------
#Converting a JSON object to a QVariant requires just three lines of code:
#
#1 // create a JSonDriver instance
#2 QJson::Parser parser;
#3 bool ok;
# // json is a QString containing the data to convert
# QVariant result = parser.parse (json, &ok);
#
#It's also possible to convert QVariant instances to JSON objects:
# // create a Serializer instance
# QJson::Serializer serializer;
# const QByteArray serialized = serializer.serialize( json_object );
#
#
#---------------------------------------------------------------------------
def prettify_dict(Dict):

    str = json.dumps(Dict, indent=4)

    # json doesn't get everything right for python
    str = string.replace(str, 'true', 'True')
    str = string.replace(str, 'false', 'False')
    return str


#---------------------------------------------------------------------------
#
# Notes:
# o The following works but indentation is crummy:
# pp = pprint.PrettyPrinter()
# pprint.pprint(theDict,stream=f)
#
# o The following doesn't work: json messes with upper/lower case eg.True=>true
# f.write(json.dumps(theDict,indent=4))
# json.dumps(theDict,indent=4)
#---------------------------------------------------------------------------


def writeDict(fpath, theDict, top="# Dictionary data\n", logger=None):

    try:
        f = open(fpath, 'w')  # open filepath
    except Exception as exc:
        if logger:
            logger.info(
                    "Write dictionary error. Exception opening dictionary file:%s"
                    % exc)
        else:
            print("Write dictionary error. Exception opening dictionary file:%s"
                  % exc)
        return

    if top is None:
        top = "#===============================================================================\n"

    # write top banner
    try:
        f.write(top)
    except Exception as exc:

        if logger is not None:
            logger.error("Dictionary write failed: %s" % exc)
        else:
            print("Dictionary write failed:", exc)
        return

    f.write(prettify_dict(theDict))  # write the file
    f.close()  # close file


#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def readDict(fpath):
    theDict = None
    f = open(fpath, 'r')
    try:
        theDict = eval(f.read())
    except Exception as exc:
        print("<DictUtils.readDict> Problem reading file:[%s]" % (fpath), exc)
        print("Goodbye...")
        sys.exit()
    f.close()
    return (theDict)


#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def printDict(Dict):

    print(prettify_dict(Dict))

    # Ok but crummy indentation
    #   for k, v in theDict.items():
    #       print(".............................")
    #       print("[%s]" % k)
    #       for k,v in theDict[k].items():
    #           print("%-16s %s %s" % (k,":",v))


#-------------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------------
if __name__ == "__main__":

    print(" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("{                                                                 }")
    print(" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    _default_cfg = {
            'gen': {
                    'libpath': {
                            'label': 'Library path',
                            'value': '../lib',
                            'desc': "Additional library filepath",
                            'type': 'STR'
                    },
                    'port': {
                            'label':
                                    'Port',
                            'value':
                                    12345,
                            'desc':
                                    'Port for AO RTS to send Deformable Mirror data',
                            'type':
                                    'INT'
                    },
                    'debug': {
                            'label': 'Debug',
                            'value': 0,
                            'desc': 'Debug level [0-10]',
                            'type': 'INT'
                    },
            },  # gen end
            'dm': {
                    'alarm_hi': {
                            'label': 'DM high-alarm',
                            'value': 0,
                            'desc': 'DM high-alarm threshold',
                            'type': 'INT'
                    },
                    'alarm_lo': {
                            'label': 'DM low-alarm',
                            'value': 0,
                            'desc': 'DM low-alarm threshold',
                            'type': 'INT'
                    },
            },
    }

    Dict = _default_cfg
    print("------------------------------------------------------------")

    print("This is the dictionary:")
    printDict(Dict)

    print("write dict")
    writeDict("dict.out", Dict)

    print("------------------------------------------------------------")
    print("read back written dict")
    inputDict = readDict("dict.out")
    printDict(inputDict)
