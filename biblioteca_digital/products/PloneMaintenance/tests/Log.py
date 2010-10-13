# -*- coding: utf-8 -*-
## PloneMaintenance
## Run cheduled scripts for routine work in a Plone site, like packing the ZODB
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# ****************************
# ****** LOG FACILITIES ******
# ****************************
"""
One can override the following variables :

LOG_LEVEL : The log level, from 0 to 5.
A Log level n implies all logs from 0 to n.
LOG_LEVEL MUST BE OVERRIDEN !!!!!


LOG_NONE = 0            => No log output
LOG_CRITICAL = 1        => Critical problems (data consistency, module integrity, ...)
LOG_ERROR = 2           => Error (runtime exceptions, ...)
LOG_WARNING = 3         => Warning (non-blocking exceptions, ...)
LOG_NOTICE = 4          => Notices (Special conditions, ...)
LOG_DEBUG = 5           => Debug (Debugging information)


LOG_PROCESSOR : A dictionnary holding, for each key, the data processor.
A data processor is a function that takes only one parameter : the data to print.
Default : logFile for all keys.
"""


LOG_LEVEL = -1

LOG_NONE = 0
LOG_CRITICAL = 1
LOG_ERROR = 2
LOG_WARNING = 3
LOG_NOTICE = 4
LOG_DEBUG = 5

from sys import stdout, stderr, exc_info
import time
import thread
import threading
import traceback
import os
import pprint

LOG_STACK_DEPTH = [-2]

def Log(level, *args):
    """
    Log(level, *args) => Pretty-prints data on the console with additional information.
    """
    if LOG_LEVEL and level <= LOG_LEVEL:
        if not level in LOG_PROCESSOR.keys():
            raise ValueError, "Invalid log level :", level

        stack = ""
        stackItems = traceback.extract_stack()
        for depth in LOG_STACK_DEPTH:
            stackItem = stackItems[depth]
            stack = "%s%s:%s:" % (stack, os.path.basename(stackItem[0]), stackItem[1],)
##        return "%s(%s)"%( os.path.basename(stackItem[0]), stackItem[1] )
##        pr = "%s %s %010.02f %08d/%02d > " % (LOG_LABEL[level], time.ctime(time.time()), time.clock(), thread.get_ident(), threading.activeCount())
        pr = "%8s %s%s: " % (
            LOG_LABEL[level],
            stack,
            time.ctime(time.time()),
##            thread.get_ident(),
##            threading.activeCount()
            )
        for data in args:
            try:
                if "\n" in data:
                    data = data
                else:
                    data = pprint.pformat(data)
            except:
                data = pprint.pformat(data)
            pr = pr + data + " "

        LOG_PROCESSOR[level](level, LOG_LABEL[level], pr, stackItems)


def FormatStack(stack):
    """
    FormatStack(stack) => string
    
    Return a 'loggable' version of the stack trace
    """
    ret = ""
    for s in stack:
        ret = ret + "%s:%s:%s: %s\n" % (os.path.basename(s[0]), s[1], s[2], s[3])
    return ret


##def LogException():
##    """
##    LogException () => None

##    Print an exception information on the console
##    """
##    Log(LOG_NOTICE, "EXCEPTION >>>")
##    traceback.print_exc(file = LOG_OUTPUT)
##    Log(LOG_NOTICE, "<<< EXCEPTION")


LOG_OUTPUT = stderr
def logFile(level, label, data, stack):
    """
    logFile : writes data to the LOG_OUTPUT file.
    """
    LOG_OUTPUT.write(data+'\n')
    LOG_OUTPUT.flush()


import zLOG

zLogLevelConverter = {
    LOG_NONE: zLOG.TRACE,
    LOG_CRITICAL: zLOG.PANIC,
    LOG_ERROR: zLOG.ERROR,
    LOG_WARNING: zLOG.PROBLEM,
    LOG_NOTICE: zLOG.INFO,
    LOG_DEBUG: zLOG.DEBUG,
    }

def logZLog(level, label, data, stack):
    """
    logZLog : writes data though Zope's logging facility
    """
    zLOG.LOG("IngeniWeb", zLogLevelConverter[level], "", data + "\n", )

    

LOG_PROCESSOR = {
    LOG_NONE: logZLog,
    LOG_CRITICAL: logZLog,
    LOG_ERROR: logZLog,
    LOG_WARNING: logZLog,
    LOG_NOTICE: logZLog,
    LOG_DEBUG: logFile,
    }
    

LOG_LABEL = {
    LOG_NONE: "",
    LOG_CRITICAL: "CRITICAL",
    LOG_ERROR:    "ERROR   ",
    LOG_WARNING:  "WARNING ",
    LOG_NOTICE:   "NOTICE  ",
    LOG_DEBUG:    "DEBUG   ",
    }
    
