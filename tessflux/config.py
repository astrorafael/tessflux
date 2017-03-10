# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


#--------------------
# System wide imports
# -------------------
from __future__ import division, absolute_import

import sys
import os
import os.path
import argparse
import errno

# Only Python 2
import ConfigParser

# ---------------
# Twisted imports
# ---------------

from twisted.logger import LogLevel

#--------------
# local imports
# -------------

from tessflux.utils import chop
from tessflux       import __version__

# ----------------
# Module constants
# ----------------


VERSION_STRING = "tessflux/{0}/Python {1}.{2}".format(__version__, sys.version_info.major, sys.version_info.minor)

# Default config file path
CONFIG_FILE="/etc/tessflux/config"


# -----------------------
# Module global variables
# -----------------------


# ------------------------
# Module Utility Functions
# ------------------------

def cmdline():
    '''
    Create and parse the command line for the tessflux package.
    Minimal options are passed in the command line.
    The rest goes into the config file.
    '''
    parser = argparse.ArgumentParser(prog='ema')
    parser.add_argument('--version',            action='version', version='{0}'.format(VERSION_STRING))
    parser.add_argument('-k' , '--console',     action='store_true', help='log to console')
    parser.add_argument('-i' , '--interactive', action='store_true', help='run in foreground (Windows only)')
    parser.add_argument('-c' , '--config', type=str,  action='store', metavar='<config file>', help='detailed configuration file')
    parser.add_argument('-s' , '--startup', type=str, action='store', metavar='<auto|manual>', help='Windows service starup mode')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(' install', type=str, nargs='?', help='install Windows service')
    group.add_argument(' start',   type=str, nargs='?', help='start Windows service')
    group.add_argument(' stop',    type=str, nargs='?', help='start Windows service')
    group.add_argument(' remove',  type=str, nargs='?', help='remove Windows service')
    return parser.parse_args()


def loadCfgFile(path):
    '''
    Load options from configuration file whose path is given
    Returns a dictionary
    '''

    if path is None or not (os.path.exists(path)):
        raise IOError(errno.ENOENT,"No such file or directory", path)

    options = {}
    parser  = ConfigParser.RawConfigParser()
    # str is for case sensitive options
    #parser.optionxform = str
    parser.read(path)

    options['tessflux'] = {}
    options['tessflux']['log_file']   = parser.get("global","log_file")
    options['tessflux']['log_level']  = parser.get("global","log_level")
   
    options['influxdb'] = {}
    options['influxdb']['url']        = parser.get("influxdb","url")
    options['influxdb']['dbname']     = parser.get("influxdb","dbname")
    options['influxdb']['measurement'] = parser.get("influxdb","measurement")
    options['influxdb']['batch']      = parser.getint("influxdb","batch")
    options['influxdb']['log_level']  = parser.get("influxdb","log_level")
    options['influxdb']['stats']      = parser.getboolean("influxdb","stats")

    options['mqtt'] = {}
    options['mqtt']['log_level']      = parser.get("mqtt","log_level")
    options['mqtt']['validation']     = parser.getboolean("mqtt","validation")
    options['mqtt']['stats']          = parser.getboolean("mqtt","stats")
    options['mqtt']['broker']         = parser.get("mqtt","broker")
    options['mqtt']['username']       = parser.get("mqtt","username")
    options['mqtt']['password']       = parser.get("mqtt","password")
    options['mqtt']['keepalive']      = parser.getint("mqtt","keepalive")
    options['mqtt']['whitelist']      = chop(parser.get("mqtt","whitelist"),',')
    options['mqtt']['blacklist']      = chop(parser.get("mqtt","blacklist"),',')
    options['mqtt']['topics']         = chop(parser.get("mqtt","topics"),',')
   
    return options


__all__ = ["VERSION_STRING", "loadCfgFile", "cmdline"]
