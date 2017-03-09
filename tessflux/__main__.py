# ----------------------------------------------------------------------
# Copyright (c) 2014 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------


#--------------------
# System wide imports
# -------------------

from __future__ import division, absolute_import

import os
import sys

# ---------------
# Twisted imports
# ---------------

#--------------
# local imports
# -------------

from .config import cmdline

# ----------------
# Module constants
# ----------------

# -----------------------
# Module global variables
# -----------------------

options = cmdline()

if os.name == "posix":
    import tessflux.main_posix
else:
    print("ERROR: unsupported OS")
    sys.exit(1)
