#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# pyConnectomist current version
version_major = 1
version_minor = 0
version_micro = 0

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(version_major, version_minor, version_micro)

# Define default Connectomist path for the package
DEFAULT_CONNECTOMIST_PATH = ("/i2bm/local/Ubuntu-14.04-x86_64/ptk/bin/"
                             "connectomist")

# Define Connectomist PTK supported version
PTK_RELEASE = "5.0"

# Expected by setup.py: the status of the project
CLASSIFIERS = ["Development Status :: 5 - Production/Stable",
               "Environment :: Console",
               "Environment :: X11 Applications :: Qt",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering",
               "Topic :: Utilities"]

# Project descriptions
description = """
[pyConnectomist]
This package provides common scripts:

* pyconnectomist_preproc: preprocess a diffusion sequence.
* pyconnectomist_tractography: compute a determinist tractography and detect
  bundles using an atlas.
* pyconnectomist_dtifit: estimate a DTI model from the preprocessed diffusion
  data.
"""
long_description = """
======================
pyConnectomist
======================

Python wrappers for Connectomist: wrap the Connectomist software and simplify
scripting calls. Each preprocessing, tractography and labeling step (i.e. one
Connectomist tab) can be run through the use of a dedicated function of the
package.
"""

# Main setup parameters
NAME = "pyConnectomist"
ORGANISATION = "CEA"
MAINTAINER = "Antoine Grigis"
MAINTAINER_EMAIL = "antoine.grigis@cea.fr"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "https://github.com/neurospin/pyconnectomist"
DOWNLOAD_URL = "https://github.com/neurospin/pyconnectomist"
LICENSE = "CeCILL-B"
CLASSIFIERS = CLASSIFIERS
AUTHOR = "pyConnectomist developers"
AUTHOR_EMAIL = "antoine.grigis@cea.fr"
PLATFORMS = "OS Independent"
ISRELEASE = True
VERSION = __version__
PROVIDES = ["pyconnectomist"]
REQUIRES = [
    "numpy>=1.6.1",
    "nibabel>=1.1.0"
]
EXTRA_REQUIRES = {}
