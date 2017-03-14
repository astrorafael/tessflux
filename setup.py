import os
import os.path

from setuptools import setup, Extension
import versioneer

# Default description in markdown
long_description = open('README.md').read()
 
# Converts from makrdown to rst using pandoc
# and its python binding.
# Docunetation is uploaded in PyPi when registering
# by issuing `python setup.py register`

try:
    import subprocess
    import pandoc
 
    process = subprocess.Popen(
        ['which pandoc'],
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )
 
    pandoc_path = process.communicate()[0]
    pandoc_path = pandoc_path.strip('\n')
 
    pandoc.core.PANDOC_PATH = pandoc_path
 
    doc = pandoc.Document()
    doc.markdown = long_description
 
    long_description = doc.rst
 
except:
    pass
   

  
classifiers = [
    'Environment :: No Input/Output (Daemon)',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Topic :: Communications',
    'Topic :: Internet',
    'Development Status :: 4 - Beta',
]


if os.name == "posix":

    import shlex

    # Some fixes before setup
    if not os.path.exists("/etc/tessflux"):
      print("creating directory /etc/tessflux")
      args = shlex.split( "mkdir /etc/tessflux")
      subprocess.call(args)

    setup(name             = 'tessflux',
          version          = versioneer.get_version(),
          cmdclass         = versioneer.get_cmdclass(),
          author           = 'Rafael Gonzalez',
          author_email     = 'astrorafael@yahoo.es',
          description      = 'MQTT to InfluxDB adapter for the STARS4ALL project',
          long_description = long_description,
          license          = 'MIT',
          keywords         = 'TESS Astronomy Python STARS4ALL',
          url              = 'http://github.com/astrorafael/tessflux/',
          classifiers      = classifiers,
          packages         = ["tessflux",  "tessflux.service", "tessflux.test", ],
          install_requires = ['twisted == 16.6.0','twisted-mqtt', 'requests'],
          data_files       = [ 
              ('/etc/init.d' ,     ['files/etc/init.d/tessflux']),
              ('/etc/systemd/system',  ['files/etc/systemd/system/tessflux.service']),
              ('/etc/tessflux',    ['files/etc/tessflux/config.example','files/etc/tessflux/influxdb.example']),
              ('/etc/logrotate.d', ['files/etc/logrotate.d/tessflux']),
              ('/usr/local/bin',   ['files/usr/local/bin/tessflux']),
            ],
        )

    args = shlex.split( "systemctl daemon-reload")
    subprocess.call(args)

else:
  pass
