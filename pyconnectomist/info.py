#! /usr/bin/env python
##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# pyConnectomist current version
version_major = 2
version_minor = 0
version_micro = 0

# Expected by setup.py: string of form "X.Y.Z"
__version__ = "{0}.{1}.{2}".format(version_major, version_minor, version_micro)

# Define default Connectomist path for the package
DEFAULT_CONNECTOMIST_PATH = ("/volatile/PTK-6.0-Ubuntu-14.04LTS-x86_64/bin/"
                             "connectomist")

# Define Connectomist PTK supported version
PTK_RELEASE = "6.0"

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
Using Connectomist in Python.
"""
SUMMARY = """
.. container:: summary-carousel

    pyConnectomist is a Python module that can be used to play with the
    diffusion MRI data using Connectist. This package offers:

    * pyconnectomist_preproc: preprocess a diffusion sequence.
    * pyconnectomist_tractography: compute a determinist tractography and
      detect bundles using an atlas.
    * pyconnectomist_dtifit: estimate a DTI model from the preprocessed
      diffusion data.
"""
long_description = (
    "pyConnectomist \n\n"
    "Python wrappers for Connectomist: wrap the Connectomist software "
    "and simplify scripting calls. Each preprocessing, tractography and "
    "labeling step (i.e. one Connectomist tab) can be run through the use "
    "of a dedicated function of the package.\n\n"
    "pyConnectomist, developed by the NeuroSpin software platform, is "
    "a wrapping of the Connectomist software developped by the `UNIRS "
    "team <http://i2bm.cea.fr/drf/i2bm/Pages/NeuroSpin/UNIRS/"
    "Presentation.aspx>`. It is meant to be run as part of a research "
    "collaboration or a charged service. For more information about its "
    "terms of use, please contact Cyril Poupon and Vincent Frouin.\n")

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
    "nibabel>=1.1.0",
    "reportlab>=3.0"
]
EXTRA_REQUIRES = {
    "standalone": {
        "pyconnectome>=1.0.0"
    }
}
SCRIPTS = [
    "pyconnectomist/scripts/pyconnectomist_preproc",
    "pyconnectomist/scripts/pyconnectomist_tractography",
    "pyconnectomist/scripts/pyconnectomist_dtifit"
]
