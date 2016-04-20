###############################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Common wrappers from Connectomist package.
"""

# System import
import os
import time
import pprint
import subprocess

# Clindmri import
from . import DEFAULT_CONNECTOMIST_PATH
from .exceptions import ConnectomistError
from .exceptions import ConnectomistConfigurationError
from .exceptions import ConnectomistRuntimeError


class ConnectomistWrapper(object):
    """ Parent class for the wrapping of Connectomist functions.
    """
    def __init__(self, path_connectomist=DEFAULT_CONNECTOMIST_PATH):
        """ Initialize the ConnectomistWrapper class by setting properly the
        environment and checking that the Connectomist software is installed.

        Parameters
        ----------
        path_connectomist: str (optional)
            path to the Connectomist executable.

        Raises
        ------
        ConnectomistConfigurationError: If Connectomist is not configured.
        """
        # Class parameters
        self.path_connectomist = path_connectomist
        self.environment = os.environ

        # Check Connectomist has been configured so the command can be found
        cmd = "%s --help" % (self.path_connectomist)
        process = subprocess.Popen(
            cmd, shell=True,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.stdout, self.stderr = process.communicate()
        self.exitcode = process.returncode
        if self.exitcode != 0:
            raise ConnectomistConfigurationError(self.path_connectomist)

    def __call__(self, algorithm, parameter_file, outdir):
        """ Run the Connectomist 'algorithm' (tab in UI).

        Parameters
        ----------
        algorithm: str
            name of Connectomist's tab in ui.
        paramter_file: str
            path to the parameter file for the tab in ui: executable python
            file to set the connectomist tab input parameters.
        outdir: str
            path to directory where the algorithm outputs.

        Raises
        ------
        ConnectomistError: If Connectomist call failed.
        """
        # Command to be run.
        cmd = "%s -p %s -f %s" % (self.path_connectomist, algorithm,
                                  parameter_file)

        # Run the command.
        process = subprocess.Popen(
            cmd,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.stdout, self.stderr = process.communicate()
        self.exitcode = process.returncode
        if self.exitcode != 0:
            error_message = ["STDOUT", "----", self.stdout, "STDERR", "----",
                             self.stderr]
            error_message = "\n".join(error_message)
            raise ConnectomistRuntimeError(algorithm, cmd, error_message)

    @classmethod
    def create_parameter_file(cls, algorithm, parameters_dict, outdir):
        """ Writes the '.py' file Connectomist uses when working in command
        line.

        Parameters
        ----------
        algorithm: str
            name of Connectomist's tab.
        parameters_dict: dict
            parameter values for the tab.
        outdir: str
            path to directory where to write the parameter file.
            If not existing the directory is created.

        Returns
        -------
        parameter_file: str
            path to the created parameter file for the tab in ui: executable
            python file to set the connectomist tab input parameters.
        """
        # If not existing create outdir
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        # Write the parameter file
        parameter_file = os.path.join(outdir, "%s.py" % algorithm)
        with open(parameter_file, "w") as f:
            f.write("algorithmName = '%s'\n" % algorithm)
            # Pretty text to write, without the first "{"
            pretty_dict = pprint.pformat(parameters_dict)[1:]
            f.write("parameterValues = {\n " + pretty_dict)

        return parameter_file


class PtkWrapper(object):
    """ Parent class for the wrapping of Connectomist Ptk functions.
    """
    def __init__(self, cmd):
        """ Initialize the PtkWrapper class

        Parameters
        ----------
        cmd: list of str (mandatory)
            the Morphologist command to execute.
        """
        # Class parameter
        self.cmd = cmd
        self.environment = os.environ

        # Check Connectomist Ptk has been configured so the command can b
        # found
        process = subprocess.Popen(
            ["which", self.cmd[0]],
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.stdout, self.stderr = process.communicate()
        self.exitcode = process.returncode
        if self.exitcode != 0:
            raise ConnectomistConfigurationError(self.cmd[0])

    def __call__(self):
        """ Run the Connectomist Ptk command.
        """
        # Execute the command
        process = subprocess.Popen(
            self.cmd,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.stdout, self.stderr = process.communicate()
        self.exitcode = process.returncode
        if self.exitcode != 0:
            error_message = ["STDOUT", "----", self.stdout, "STDERR", "----",
                             self.stderr]
            error_message = "\n".join(error_message)
            raise ConnectomistRuntimeError(algorithm, cmd, error_message)
