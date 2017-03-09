# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

# ---------------
# Twisted imports
# ---------------

from twisted.internet import task, reactor

#--------------
# local imports
# -------------

from tessflux.service.reloadable import Service, MultiService, Application
from tessflux.logger import sysLogInfo,  startLogging
from tessflux.config import VERSION_STRING, cmdline, loadCfgFile


from tessflux.tessflux  import TESSFluxDBService
from tessflux.mqttsubs  import MQTTService
from tessflux.influxdb  import InfluxDBService  


# Read the command line arguments and config file options
cmdline_opts = cmdline()
config_file = cmdline_opts.config
if config_file:
   options  = loadCfgFile(config_file)
else:
   options = None


# Start the logging subsystem
log_file = options['tessflux']['log_file']
startLogging(console=cmdline_opts.console, filepath=log_file)

# ------------------------------------------------
# Assemble application from its service components
# ------------------------------------------------

application = Application("TESSFLUX")

tessfluxService  = TESSFluxDBService(options['tessflux'], config_file)
tessfluxService.setName(TESSFluxDBService.NAME)
tessfluxService.setServiceParent(application)

mqttService = MQTTService(options['mqtt'])
mqttService.setName(MQTTService.NAME)
mqttService.setServiceParent(tessfluxService)

influxdbService = InfluxDBService(options['influxdb'])
influxdbService.setName(InfluxDBService.NAME)
influxdbService.setServiceParent(tessfluxService)


# --------------------------------------------------------
# Store direct links to subservices in our manager service
# --------------------------------------------------------


__all__ = [ "application" ]