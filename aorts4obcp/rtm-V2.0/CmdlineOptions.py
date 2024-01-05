#===============================================================================
# File: CmdlineOptions.py : generic command-line arguments parser
#
#
#===============================================================================
from __future__ import (absolute_import, print_function, division)
import optparse


#-------------------------------------------------------------------------------
def prn_options():
    print("...................................................................")
    print("                   Commandline Options")
    print("...................................................................")

    print("Debug  :", debug)
    print("Verbose:", verbose)
    print("Libpath:", libpath)
    print("Logpath:", logpath)
    print("Host   :", host)
    print("Port   :", port)
    print("Test   :", test)
    print("Opts   :", opts)
    print("Args   :", args)  #list of positional args left after parsing opts
    print("...................................................................")


#-------------------------------------------------------------------------------
def optToInt(opt):
    if opt is not None:
        return (int(opt))
    return None


# Command Line Parser
usage = "Try: --help"
_cmdlp = optparse.OptionParser(usage=usage)

#------------------------------------------------------------------------------

# define options

_cmdlp.add_option("--logpath", action="store", dest="logpath",
                  help="Set logfile path")

_cmdlp.add_option("--libpath", action="store", dest="libpath",
                  help="Set library path")

_cmdlp.add_option("--debug", action="store", dest="debug",
                  help="Set debug level 1-10")

_cmdlp.add_option("--verbose", action="store", dest="verbose",
                  help="Set verbosity level 1-10")

_cmdlp.add_option("--test", action="store", dest="test", help="set test number")

#_cmdlp.add_option("--fake"   , action="store_true", dest="fake"   ,
#               help="Generate fake data")

_cmdlp.add_option("-V", action="store_true", dest="version",
                  help='Print version number and quit')

_cmdlp.add_option("--version", action="store_true", dest="version",
                  help='Print version number and quit')

_cmdlp.add_option("--host", action="store", dest="host",
                  help="set host.          Exp: '--host 'localhost' ")

_cmdlp.add_option("--port", action="store", dest="port",
                  help="set RTS data port. Exp: '--port NUMBER' ")

_cmdlp.add_option("--tests", action="store_true", dest="tests",
                  help="test help.  Exp: '--tests' ")

# set defaults
_cmdlp.set_defaults(
        debug=None,
        verbose=None,
        fake=None,
        version=None,
        test=None,
        port=None,
        logpath=None,
        libpath=None,
        host=None,
)

# opts : dictionary of option,value pairs
# args : list of positional args left over after parsing opts
(opts, args) = _cmdlp.parse_args()

#-------------------------------------------------------------------------------
#debug   = opts.debug
#verbose = opts.verbose
#test    = opts.test
#fake    = opts.fake

version = opts.version
logpath = opts.logpath
libpath = opts.libpath
host = opts.host

debug = optToInt(opts.debug)
verbose = optToInt(opts.verbose)
test = optToInt(opts.test)
tests = optToInt(opts.tests)
fake = optToInt(opts.fake)
port = optToInt(opts.port)
