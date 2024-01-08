#!/usr/bin/python -Qnew
#^==============================================================================
# File: logger.py
#
#
# http://docs.python.org/library/logging.html
#===============================================================================
from __future__ import absolute_import, print_function, division
import sys, os
import logging, logging.handlers  # the python standard logging modules
import util


#-------------------------------------------------------------------------------
# class logger:
#  logpath     :
#  nmbytes     : number of megabytes per logfile
#  nfiles      : number of logfiles
#-------------------------------------------------------------------------------
# Notes:
# o  Create a logger
#    lg = logger.Logger().lg
#
#
# o  Set logging level
#    lg.setLevel('level-name') where level-name is one of
#        'CRITICAL'
#        'ERROR',
#        'WARN',
#        'INFO',
#        'DEBUG',
#    Example: cfg.lg.setLevel('WARN') : Enable levels WARN and all above it.
#
# o Logfiles
#   The most current file is always LOG_FILENAME, and each time it reaches
#   the size limit it is renamed with the suffix .1. Each of the existing
#   backup files is renamed to increment the suffix (.1 becomes .2, etc.)
#   and the .maxnumber file is erased.
#                                       i.e. WARN,ERROR,CRIT
##-------------------------------------------------------------------------------
class Logger(object):

    #...........................................................................
    def __init__(self, logpath=None, nmbytes=1, nfiles=1, debug=0,
                 level='DEBUG', nolog=False):

        # logging-levels dictionary for key:s.level
        self.levels = {
                'CRITICAL': logging.CRITICAL,
                'ERROR': logging.ERROR,
                'WARNING': logging.WARNING,
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'NOTSET': logging.NOTSET
        }

        self.nmbytes = nmbytes
        self.nfiles = nfiles
        self.maxfsize = nmbytes * 0x100000  # number of megabytes X  1048576
        self.debug = debug  # class debug, not logging debug
        self.level = level  # logging level
        self.file_level = level  # file    level
        self.console_level = level  # console level

        self.logname = None

        # Get some path info
        (self.execdir, self.execname, self.execpath, self.execpfx, self.homedir,
         self.cwd) = util.setPaths()
        if self.debug:
            print("-------------------------------------------------------")
            print("EXECDIR :", self.execdir)
            print("EXECNAME:", self.execname)
            print("EXECPATH:", self.execpath)
            print("EXECPFX :", self.execpfx)
            print("HOMEDIR :", self.homedir)
            print("CWD     :", self.cwd)

        # If logpath was given...
        if logpath is not None:
            logpath = os.path.realpath(logpath)  # realpath, not symlink, etc...
            logdir = os.path.dirname(logpath)  # set log directory
            logname = os.path.basename(logpath)  # set log-filename from logpath
            print("LOGPATH:", logpath)
            print("LOGDIR :", logdir)
            print("LOGNAME:", logname)

            # If no such directory, directory = cwd
            if not os.path.exists(logdir):
                print("NO SUCH LOGFILE DIRECTORY  :'%s'" % logdir)
                logdir = self.cwd
                logpath = logdir + '/' + logname

            # directory exists
            else:

                # If directory is not writeable, directory = cwd
                if not os.access(logdir, os.W_OK):
                    print("LOG DIRECTORY NOT WRITEABLE:'%s'" % logdir)
                    print("LOG TO DIRECTORY           :'%s'" % self.cwd)

                    logdir = self.cwd  #
                    logpath = logdir + '/' + logname

                # if directory is writeable & file exists but is not writeable:
                #
                if os.path.exists(logpath) \
                and not os.access(logpath, os.W_OK ):
                    print("LOGFILE IS NOT WRITEABLE   :'%s'" % logpath)
                    logname = 'xyz.log'
                    logpath = logdir + '/' + logname
                    print("LOGGING TO                 :'%s'" % logpath)

            self.logpath = logpath
            self.logdir = logdir
            self.logname = logname

        # No logpath was given
        else:
            self.logpath = None
            self.logdir = None
            self.logname = None

        #......................................................................
        # if s.logpath is None (possibly due to above)
        # use process-invocation-rootname + .log
        if self.logpath is None:

            # if given logpath was bad, use the name portion of the bad path
            if self.logname is not None:
                self.logpath = self.cwd + '/' + self.logname + '.log'

            # else use the executable's prefix eg: 'foo' from 'foo.py'
            else:
                self.logpath = self.cwd + '/' + self.execpfx + '.log'

            print("BAD LOGPATH. USING         :'%s'" % self.logpath)
            self.logname = os.path.basename(
                    self.logpath)  #set filename from logpath
            self.logdir = os.path.dirname(self.logpath)

        if self.debug:
            print("<logger>")
            print("LOGNAME :", self.logname)
            print("LOGDIR  :", self.logdir)
            print("LOGPATH :", self.logpath)

        #......................................................................
        # get python logger instance
        try:
            self.lg = logging.getLogger(self.logpath)
        except Exception as e:
            print("*** Error,logger: Logger creation exception:", e)

            sys.exit(-1)

        # get files handler
        try:
            self.file_handler = logging.handlers.RotatingFileHandler(
                    self.logpath, maxBytes=self.maxfsize,
                    backupCount=self.nfiles)
        except Exception as e:
            print("*** Error, logger: File-handler creation exception:", e)
            #s.set_null_logger()
            #raise(); return()  # raise same exception to caller
            #return
            return

        # get console formatter
        self.console_formatter = logging.Formatter("%(message)s")

        # get files formatter
        self.file_formatter = logging.Formatter(
                "%(asctime)s : %(levelname)s : %(message)s")

        # get console handler
        try:
            self.console_handler = logging.StreamHandler()
        except Exception as e:
            print("***Error, logger: Console-handler creation exception:", e)
            raise ()
            return ()  # raise same exception to caller

        # set console formatter
        self.console_handler.setFormatter(self.console_formatter)

        # set files formatter
        self.file_handler.setFormatter(self.file_formatter)

        # add handlers to logger
        self.lg.addHandler(self.file_handler)
        self.lg.addHandler(self.console_handler)

        # add the handler to the root logger
        #logging.getlogger(s.logpath).addHandler(s.console_handler)
        self.lg.addHandler(self.console_handler)

        # set console & files log-level
        self.setLevel(self.level)  # set console & file log-levels

        # std debug output
        if self.debug:
            print("Level                   :", self.level)
            print("Console level           :", self.console_level)
            print("File    level           :", self.file_level)
            print("Logpath                 :", logpath)
            print("N Files                 :", self.nfiles)
            print("Max file size, megabytes:", self.nmbytes)
            print("Maximum file size       :", self.maxfsize)
            print("log directory           :", self.logdir)
            print("Logpath                 :", self.logpath)
            #print("log directory exists    :", s.logdir_exists       )
            #print("path exists             :", s.fullpath_exists     )
            print("...........................................................")

    #---------------------------------------------------------------------------
    # Set logging Level
    #
    # logging levels
    # CRITICAL  50
    # ERROR     40
    # WARNING   30
    # INFO      20
    # DEBUG     10
    # NOTSET     0
    #---------------------------------------------------------------------------
    def setLevel(self, level):
        if self.debug: print("<logger>setLevel              :", level)
        self.lg.setLevel(self.levels[level])
        self.set_file_level(level)
        self.set_console_level(level)

    #---------------------------------------------------------------------------
    def set_console_level(self, level):
        if self.debug: print("<logger>set_console_Level     :", level)
        self.console_level = level
        self.console_handler.setLevel(self.levels[level])
        #s.lg.setLevel   ( s.levels[level] )

    #---------------------------------------------------------------------------
    def set_file_level(self, level):
        if self.debug: print("<logger>set_file_Level        :", level)
        self.file_level = level
        self.file_handler.setLevel(self.levels[level])

    #---------------------------------------------------------------------------
    def stop(self):
        logging.shutdown()

    def foo(self):
        print("***** FOO ******")

    # *** Under Development ***
    # good idea... Under development
    # if nolog, logger is null (for best performance) ... but see
    # logging in python book for best solution
    def set_null_logger(self):
        self.lg = None
        print("<logger> set_null_logger. Fatal. Exiting...")
        sys.exit()

    # Return the full directory path of the executable regardles of how
    # invoked.
    # Ie. regardless of relative paths, symbolic links, ets
    # Note: this is a copy of (current)<util.py>.setExecDirectory()
    #def setExecDirectory(s):
    #    return(os.path.dirname(os.path.realpath(sys.argv[0])))


#
# Main for module Test
#
if __name__ == "__main__":

    print("************************************************************")
    print("************************************************************")

    def test1():
        try:
            lg = logger('./logs/test.log', debug=True)
        except:
            sys.exit()
        print("..................................................")

        try:
            lg = logger('./nosuchdirectory/test.log', debug=True)
        except:
            print("Caught no such directory errror: Good")
        else:
            print("** BAD ** Did not catch no such directory errror: ")

        try:
            lg = logger(debug=True)
        except:
            sys.exit()
        print("..................................................")

    try:
        logger = logger(debug=True)
    except:
        print("*** Goodbye ***")
        sys.exit()

    lg = logger.lg
    logger.setLevel('DEBUG')  # enable all logging >= DEBUG
    for i in range(2):
        lg.info(".................... %d .........................." % i)
        lg.critical("critical message")
        lg.error("error    message")
        lg.warn("warning  message")
        lg.info("info     message")
        lg.debug("debug    message")

        print("-----------------------------------")

        logger.setLevel('INFO')  # enable all logging >= DEBUG
        # lg.exception
        #  creates a log message similar to logger.error(). The difference is
        #  that logger.exception() dumps a stack trace along with it. Call
        #  this method only from an exception handler.
        #
        #

        # lg.log() takes a log level as an explicit argument. This is a little
        # more verbose for logging messages than using the log level
        # convenience methods listed above, but this is how to log at custom
        # log levels.
        #
        # lg.log()
