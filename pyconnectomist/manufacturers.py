##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
The module defines the MANUFACTURERS dict that maps the names used by the
package API to the IDs used by the Connectomist software.
"""

# Note: we use simplified manufacturer names to simplify usage.
# e.g. we use "GE" where Connectomist uses "GE HealthCare",
# but a DICOM header would use "GE Medical Systems"
MANUFACTURERS = {
    "Bruker":  0,
    "GE":      1,
    "Philips": 2,
    "Siemens": 3
}
