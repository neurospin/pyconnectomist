##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Package to wrap the Connectomist software and simplify scripting calls.
In the root location of the module are implemented:

    * the Connectomist's dedicated exceptions.
    * the Connectomist's wrappers.
    * the supported manufacturers.
"""

from .info import __version__
from .info import DEFAULT_CONNECTOMIST_PATH
