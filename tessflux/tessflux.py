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
import datetime
import random
import os
from collections import deque

# ---------------
# Twisted imports
# ---------------

from twisted          import __version__ as __twisted_version__
from twisted.logger   import Logger, LogLevel
from twisted.internet import task, reactor, defer
from twisted.internet.defer   import inlineCallbacks
from twisted.internet.threads import deferToThread

#--------------
# local imports
# -------------

from tessflux        import __version__
from tessflux.config import VERSION_STRING, loadCfgFile
from tessflux.logger import setLogLevel

from tessflux.service.reloadable import MultiService

from tessflux.influxdb import InfluxDBService
from tessflux.mqttsubs import MQTTService

from tessflux.defer    import DeferredQueue

# ----------------
# Module constants
# ----------------


# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='tessflux')

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------    
# -----------------------------------------------------------------------------    

class TESSFluxDBService(MultiService):

    # Service name
    NAME = 'MQTT To InfluxDB converter'

    # Stats period task in seconds
    T_STAT = 3600
   
    def __init__(self, options, cfgFilePath):
        MultiService.__init__(self)
        setLogLevel(namespace='tessflux', levelStr=options['log_level'])
        self.cfgFilePath = cfgFilePath
        self.options     = options
        self.queue       = DeferredQueue(backlog=1)
        self.statsTask   = task.LoopingCall(self.logCounters)
       

    @inlineCallbacks
    def reloadService(self, options):
        '''
        Reload application parameters
        '''
        log.warn("{tessflux} config being reloaded", tessflux=VERSION_STRING)
        try:
            options  = yield deferToThread(loadCfgFile, self.cfgFilePath)
        except Exception as e:
            log.error("Error trying to reload: {excp!s}", excp=e)
        else:
            self.options                  = options['tessflux']
            MultiService.reloadService(self, options)
           
    def startService(self):
        '''
        Starts database service and see if we can continue.
        '''
        log.info('starting {name} {version} using Twisted {tw_version}', 
            name=self.name,
            version=__version__, 
            tw_version=__twisted_version__)
       
        self.influxdbService  = self.getServiceNamed(InfluxDBService.NAME)
        self.mqttService      = self.getServiceNamed(MQTTService.NAME)
        self.statsTask.start(self.T_STAT, now=False) # call every T seconds
        try:
            self.influxdbService.startService()
        except Exception as e:
            log.failure("{excp!s}", excp=e)
            log.critical("Problems initializing {name}. Exiting gracefully", name=InfluxDBService.NAME)
            reactor.callLater(0, reactor.stop)
        else:
            self.mqttService.startService()

    # -------------
    # log stats API
    # -------------

    def resetCounters(self):
        '''Resets stat counters'''
        self.mqttService.resetCounters()
        self.influxdbService.resetCounters()


    def logCounters(self):
        '''log stat counters'''
        self.mqttService.logCounters()
        self.influxdbService.logCounters()
        self.resetCounters()


__all__ = [ "TESSFluxDBService" ]