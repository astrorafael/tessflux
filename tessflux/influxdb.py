# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import datetime
import requests

from StringIO import StringIO

# ---------------
# Twisted imports
# ---------------

from twisted.logger               import Logger, LogLevel
from twisted.internet             import reactor, task
from twisted.internet.defer       import inlineCallbacks, returnValue
from twisted.internet.task        import deferLater
from twisted.web.client           import Agent, FileBodyProducer
from twisted.web.http_headers     import Headers
from twisted.internet.defer       import DeferredList
from twisted.application.service  import Service

from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred

#--------------
# local imports
# -------------

from .logger import setLogLevel
from .service.reloadable import Service

# ----------------
# Module constants
# ----------------

# InfluxDB Epoch (start of timestamps)
INFLUXDB_EPOCH = datetime.datetime(year=1970,month=1,day=1)

# InfluxDB database probe timeout in seconds
PROBE_TIMEOUT = 5

# Influx DB Write request Body Format
MONITORING_BODY="%(meas)s,name=%(name)s mag=%(mag)s,freq=%(freq)s,tsky=%(tsky)s,tamb=%(tamb)s,wdBm=%(wdBm)s %(tstamp)d"

# ----------------
# Global functions
# -----------------


# -----------------------
# Module global variables
# -----------------------

log = Logger(namespace='influxdb')


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            log.debug("{m}",m=display)
            self.remaining -= len(display)

    def connectionLost(self, reason):
        log.debug('Finished receiving body: {m}', m=reason.getErrorMessage())
        self.finished.callback(None)


class InfluxDBService(Service):

    # Service name
    NAME = 'InfluxDB Client Service'

    def __init__(self, options):
        self.options  = options
        self.agent    = Agent(reactor)
        setLogLevel(namespace='influxdb', levelStr=self.options['log_level'])
        setLogLevel(namespace='twisted.web.client._HTTP11ClientFactory', levelStr='warn')
        self.resetCounters()

    
    def startService(self):
        log.info("starting {name}", name=self.name)
        Service.startService(self)
        self.probe()

    
    def stopService(self):
        Service.stopService(self)


    #---------------------
    # Extended Service API
    # --------------------

    def reloadService(self, options):
        options = options['influxdb']
        setLogLevel(namespace='inet', levelStr=options['log_level'])
        log.info("new log level is {lvl}", lvl=options['log_level'])
        self.options = options

    

    # -------------
    # log stats API
    # -------------

    def resetCounters(self):
        '''Resets stat counters'''
        self.nrequests  = 0
        self.nrejected  = 0
        self.nresponses = 0
        self.nfailures  = 0


    def getCounters(self):
        return [ self.nrequests, self.nresponses, self.nrejected, self.nfailures ]


    def logCounters(self):
        '''log stat counters'''
        if not self.options['stats']:
            return
        # get stats
        result = self.getCounters()
        log.info("InfluxDB Stats [Requested, Ok, Reject, Fail] = {counters!s}", counters=result)

    # --------------
    # Helper methods
    # --------------


    def probe(self):
        '''Probe InfluxDB Database Server'''
        try:
            log.info("probing InfluxDB at {url}", url=self.options['url'])
            resp = requests.head(self.options['url'] + '/ping', timeout=PROBE_TIMEOUT)
        except Exception as e:
            log.error('{excp!r}', excp=e)
            raise
        else:
            if resp.status_code != 204:
                raise RuntimeError("InfluxDB not ready")
            log.info("found InfluxDB version {version}", version=resp.headers['X-Influxdb-Version'])
            reactor.callLater(0, self.loop)


    @inlineCallbacks
    def loop(self):
        '''
        Returns a deferred that when triggered returns True or False
        '''
        log.debug("called InfluxDB writter main loop ...")
        while True:
            try:
                row           = yield self.parent.queue.get()
                self.nrequests += 1
                row['tstamp'] -= INFLUXDB_EPOCH
                row['tstamp'] = (10**9)*row['tstamp'].total_seconds()
                row['dbname'] = self.options['dbname']
                row['meas']   = self.options['measurement']
                status_code   = yield self.write(row)
            except Exception as e:
                log.error('{excp!r}', excp=e)
                reactor.callLater(0, reactor.stop)


    def write(self, row):
        '''
        Writes a sample into InfluxDB with proper format.
        Returns a deferred with the respone object as callback argument
        '''
        datapoint = MONITORING_BODY % row
        log.info("{datapoint}", datapoint=datapoint)
        parameters = "/write?db=%(dbname)s\n" % row
        # From UNICODE to simple strimg
        datapoint = str(datapoint)
        body = FileBodyProducer(StringIO(datapoint))
        d = self.agent.request('POST',
                self.options['url'] + parameters,
                Headers(
                    {'User-Agent':  ['tessflux'], 
                    'Content-Type': ['application/x-www-form-urlencoded']
                    }),
                body)
        d.addCallbacks(self._okResponse, self._failResponse)
        return d
   
  
    def _failResponse(self, failure):
        log.debug("reported {message}", message=failure.getErrorMessage())
        self.nfailures += 1
        return failure

    def _okResponse(self, response):
        log.debug("from {response.request.absoluteURI} => {response.code}", response=response)
        if response.code == 204:
            self.nresponses += 1
        else:
            self.nrejected += 1
        finished = Deferred()
        response.deliverBody(BeginningPrinter(finished))
        return finished



    

__all__ = [
    "InfluxDBService"
]