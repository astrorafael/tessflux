# TESSFLUX

MQTT to InfluxDB TESS data converter.

| Table of Contents                                                          |
|:---------------------------------------------------------------------------|
| [Description](README.md#Description)                                       |
| [Installation](README.md#Installation)                                     |
| [Start/Stop/Reload/Pause]((README.md#StartStopReloadPause)                 |
| [Configuration](README.md#Configuration)                                   |

## <a name="Description"> Description

**ema** is a software package that talks to the EMA Weather Station through a serial port or TCP port. Since EMA hardware is rather smart, the server has really very little processing to do, so it can run happily on a Raspberry Pi. 

Main features:

1. Publishes current and historic data to an MQTT broker.

2. If voltage threshold is reached it triggers a custom alarm script. Supplied script sends an SMS using the gammu-python package

3. If the roof relay changes state (from open to close and viceversa), it triggers a custom script.

4. Maintains EMA RTC in sync with the host computer RTC.

5. Manages active/inactive auxiliar relay time windows. Shuts down
host computer if needed. A Respberry Pi with **internal RTC is strongly recommended**.


## <a name="Instalation"> Instalation

Only for Linux.

**Warning** You need Debian package libffi-dev to install Pip 'service-identity' requirement

  `sudo pip install ema`

  or from GitHub:

    git clone https://github.com/astrorafael/ema.git
    cd ema
    sudo python setup.py install


All executables and custom scripts are copied to `/usr/local/bin`

Type `ema -k` to start the service on foreground with console output

An available startup service script for debian-based systems is provided. 
Type `sudo service ema start` to start it
Type `sudo update-rc.d emad defaults` to install it at boot time

### <a name="EMA Server Configuation"> EMA Server Configuation ###

By default, file `/etc/ema.d/config` provides the configuration options needed.
This file is self explanatory. 

In both cases, you need to create a new `config` or `config.ini` file from the examples.

Some parameters are defined as *reloadable*. Type `sudo service ema reload` for the new configuration to apply without stopping the service.

### <a name="Logging"> Logging ###

Log file is placed under `/var/log/ema.log` (Linux) or `C:\ema\log\ema.log` (Windows). 
Default log level is `info`. It generates very litte logging at this level.
On Linux, the log is rotated through the /etc/logrotate.d/ema policy. On Windows, there is no such policy.

