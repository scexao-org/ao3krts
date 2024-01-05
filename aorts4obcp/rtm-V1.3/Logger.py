#!/usr/bin/python -Qnew
#^==============================================================================
# File: Logger.py
#
#
# http://docs.python.org/library/logging.html
#===============================================================================
from __future__ import absolute_import, print_function, division
import sys, os
import logging, logging.handlers  # the python standard logging modules
import util


#-------------------------------------------------------------------------------
# class Logger:
#  logpath     :
#  nmbytes     : number of megabytes per logfile
#  nfiles      : number of logfiles
#-------------------------------------------------------------------------------
# Notes:
# o  Create a logger
#    lg = Logger.Logger().lg
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
    def __init__(s, logpath=None, nmbytes=1, nfiles=1, debug=False,
                 level='DEBUG', nolog=False):

        # logging-levels dictionary for key:s.level
        s.levels = {
                'CRITICAL': logging.CRITICAL,
                'ERROR': logging.ERROR,
                'WARNING': logging.WARNING,
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'NOTSET': logging.NOTSET
        }

        s.nmbytes = nmbytes
        s.nfiles = nfiles
        s.maxfsize = nmbytes * 0x100000  # number of megabytes X  1048576
        s.debug = debug  # class debug, not logging debug
        s.level = level  # logging level
        s.file_level = level  # file    level
        s.console_level = level  # console level

        s.logname = None

        # Get some path info
        (s.execdir, s.execname, s.execpath, s.execpfx, s.homedir,
         s.cwd) = util.setPaths()
        if s.debug:
            print("-------------------------------------------------------")
            print("EXECDIR :", s.execdir)
            print("EXECNAME:", s.execname)
            print("EXECPATH:", s.execpath)
            print("EXECPFX :", s.execpfx)
            print("HOMEDIR :", s.homedir)
            print("CWD     :", s.cwd)

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
                logdir = s.cwd
                logpath = logdir + '/' + logname

            # directory exists
            else:

                # If directory is not writeable, directory = cwd
                if not os.access(logdir, os.W_OK):
                    print("LOG DIRECTORY NOT WRITEABLE:'%s'" % logdir)
                    print("LOG TO DIRECTORY           :'%s'" % s.cwd)

                    logdir = s.cwd  #
                    logpath = logdir + '/' + logname

                # if directory is writeable & file exists but is not writeable:
                #
                if os.path.exists(logpath) \
                and not os.access(logpath, os.W_OK ):
                    print("LOGFILE IS NOT WRITEABLE   :'%s'" % logpath)
                    logname = 'xyz.log'
                    logpath = logdir + '/' + logname
                    print("LOGGING TO                 :'%s'" % logpath)

            s.logpath = logpath
            s.logdir = logdir
            s.logname = logname

        # No logpath was given
        else:
            s.logpath = None
            s.logdir = None
            s.logname = None

        #......................................................................
        # if s.logpath is None (possibly due to above)
        # use process-invocation-rootname + .log
        if s.logpath is None:

            # if given logpath was bad, use the name portion of the bad path
            if s.logname is not None:
                s.logpath = s.cwd + '/' + s.logname + '.log'

            # else use the executable's prefix eg: 'foo' from 'foo.py'
            else:
                s.logpath = s.cwd + '/' + s.execpfx + '.log'

            print("BAD LOGPATH. USING         :'%s'" % s.logpath)
            s.logname = os.path.basename(s.logpath)  #set filename from logpath
            s.logdir = os.path.dirname(s.logpath)

        if s.debug:
            print("<Logger>")
            print("LOGNAME :", s.logname)
            print("LOGDIR  :", s.logdir)
            print("LOGPATH :", s.logpath)

        #......................................................................
        # get python logger instance
        try:
            s.lg = logging.getLogger(s.logpath)
        except Exception, e:
            print("*** Error,Logger: Logger creation exception:", e)

            sys.exit(-1)

        # get files handler
        try:
            s.file_handler = logging.handlers.RotatingFileHandler(
                    s.logpath, maxBytes=s.maxfsize, backupCount=s.nfiles)
        except Exception, e:
            print("*** Error, Logger: File-handler creation exception:", e)
            #s.set_null_logger()
            #raise(); return()  # raise same exception to caller
            #return
            return

        # get console formatter
        s.console_formatter = logging.Formatter("%(message)s")

        # get files formatter
        s.file_formatter = logging.Formatter(
                "%(asctime)s : %(levelname)s : %(message)s")

        # get console handler
        try:
            s.console_handler = logging.StreamHandler()
        except Exception, e:
            print("***Error, Logger: Console-handler creation exception:", e)
            raise ()
            return ()  # raise same exception to caller

        # set console formatter
        s.console_handler.setFormatter(s.console_formatter)

        # set files formatter
        s.file_handler.setFormatter(s.file_formatter)

        # add handlers to logger
        s.lg.addHandler(s.file_handler)
        s.lg.addHandler(s.console_handler)

        # add the handler to the root logger
        #logging.getLogger(s.logpath).addHandler(s.console_handler)
        s.lg.addHandler(s.console_handler)

        # set console & files log-level
        s.setLevel(s.level)  # set console & file log-levels

        # std debug output
        if s.debug:
            print("Level                   :", s.level)
            print("Console level           :", s.console_level)
            print("File    level           :", s.file_level)
            print("Logpath                 :", logpath)
            print("N Files                 :", s.nfiles)
            print("Max file size, megabytes:", s.nmbytes)
            print("Maximum file size       :", s.maxfsize)
            print("log directory           :", s.logdir)
            print("Logpath                 :", s.logpath)
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
    def setLevel(s, level):
        if s.debug: print("<Logger>setLevel              :", level)
        s.lg.setLevel(s.levels[level])
        s.set_file_level(level)
        s.set_console_level(level)

    #---------------------------------------------------------------------------
    def set_console_level(s, level):
        if s.debug: print("<Logger>set_console_Level     :", level)
        s.console_level = level
        s.console_handler.setLevel(s.levels[level])
        #s.lg.setLevel   ( s.levels[level] )

    #---------------------------------------------------------------------------
    def set_file_level(s, level):
        if s.debug: print("<Logger>set_file_Level        :", level)
        s.file_level = level
        s.file_handler.setLevel(s.levels[level])

    #---------------------------------------------------------------------------
    def stop(s):
        logging.shutdown()

    def foo(s):
        print("***** FOO ******")

    # *** Under Development ***
    # good idea... Under development
    # if nolog, logger is null (for best performance) ... but see
    # logging in python book for best solution
    def set_null_logger(s):
        s.lg = None
        print("<Logger> set_null_logger. Fatal. Exiting...")
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
            lg = Logger('./logs/test.log', debug=True)
        except:
            sys.exit()
        print("..................................................")

        try:
            lg = Logger('./nosuchdirectory/test.log', debug=True)
        except:
            print("Caught no such directory errror: Good")
        else:
            print("** BAD ** Did not catch no such directory errror: ")

        try:
            lg = Logger(debug=True)
        except:
            sys.exit()
        print("..................................................")

    try:
        logger = Logger(debug=True)
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
        #  creates a log message similar to Logger.error(). The difference is
        #  that Logger.exception() dumps a stack trace along with it. Call
        #  this method only from an exception handler.
        #
        #

        # lg.log() takes a log level as an explicit argument. This is a little
        # more verbose for logging messages than using the log level
        # convenience methods listed above, but this is how to log at custom
        # log levels.
        #
        # lg.log()

    #logging.disable(logging.DEBUG)     # can't turn debug on again

#    lg.info("\n")
#    lg.setLevel( (logging.DEBUG + 10) ) # disable all logging <= DEBUG

#    lg.debug("debug message")
#    lg.info ("debug off")
#    lg.warn ("warn message")
#    lg.error("error message")
#    lg.critical("critical message")
#-------------------------------------
#    open(logpath, "w").write(procParms + "\n")
#    close(logpath)
#-------------------------------------
#    create console output handler and set level to debug
#    ch = logging.StreamHandler()
#    ch.setLevel(logging.DEBUG)
#    ch.setFormatter(formatter)     # add formatter to ch
#    lg.addHandler(ch) # add ch to logger
#-------------------------------------
#  write pid, etc
#  lg.info(set_parms()+'\n')
