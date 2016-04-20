##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Definition of the package exceptions.
"""

# Clindmri import
from .manufacturers import MANUFACTURERS


class ConnectomistError(Exception):
    """ Base exception type for the package.
    """
    def __init__(self, message):
        super(ConnectomistError, self).__init__(message)


class ConnectomistConfigurationError(ConnectomistError):
    """ Error thrown when call to the Connectomist software failed.
    """
    def __init__(self, command_name):
        message = "Connectomist command '{0}' not found.".format(command_name)
        super(ConnectomistConfigurationError, self).__init__(message)


class ConnectomistRuntimeError(ConnectomistError):
    """ Error thrown when call to the Connectomist software failed.
    """
    def __init__(self, algorithm_name, parameters, error=None):
        message = (
            "Connectomist call for '{0}' failed, with parameters: '{1}'. "
            "Error:: {2}.".format(algorithm_name, parameters, error))
        super(ConnectomistRuntimeError, self).__init__(message)


class ConnectomistBadManufacturerNameError(ConnectomistError):
    """ Error thrown when an incorrect manufacturer name is detected.
    """
    def __init__(self, manufacturer):
        message = ("Incorrect manufacturer name: '{0}', should be in "
                   "{1}.".format(manufacturer, set(MANUFACTURERS)))
        super(ConnectomistBadManufacturerNameError, self).__init__(message)


class ConnectomistMissingParametersError(ConnectomistError):
    """ Error thrown when needed parameters were not all given.
    """
    def __init__(self, algorithm_name, missing_parameters):
        message = "Missing parameters for '{0}': {1}.".format(
            algorithm_name, missing_parameters)
        super(ConnectomistMissingParametersError, self).__init__(message)


class ConnectomistBadFileError(ConnectomistError):
    """ Error thrown when a file is missing or corrupted.
    """
    def __init__(self, file_path):
        message = "Missing or corrupted file: '{0}'.".format(file_path)
        super(ConnectomistBadFileError, self).__init__(message)
