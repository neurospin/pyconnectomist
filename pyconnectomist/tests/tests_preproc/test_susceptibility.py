##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Mocking Popen directly - need to construct a Mock to return, and adjust its
communicate() return_value.
The benefit of this approach is in not needing to do the strip/split on your
fake return string.
"""

# System import
import unittest
import sys
import os
import copy
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist import
from pyconnectomist.preproc.susceptibility import susceptibility_correction
from pyconnectomist.exceptions import ConnectomistBadManufacturerNameError
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistMissingParametersError


class ConnectomistMask(unittest.TestCase):
    """ Test the Connectomist 'Susceptibility' tab:
    'pyconnectomist.preproc.susceptibility.susceptibility_correction'
    """
    def setUp(self):
        """ Run before each test - the mock_popen will be available and in the
        right state in every test<something> function.
        """
        # Mocking popen
        self.popen_patcher = patch("pyconnectomist.wrappers.subprocess.Popen")
        self.mock_popen = self.popen_patcher.start()
        mock_process = mock.Mock()
        attrs = {
            "communicate.return_value": ("mock_OK", "mock_NONE"),
            "returncode": 0
        }
        mock_process.configure_mock(**attrs)
        self.mock_popen.return_value = mock_process
        self.kwargs = {
            "outdir": "/my/path/mock_outdir",
            "raw_dwi_dir": "/my/path/mock_rawdwidir",
            "rough_mask_dir": "/my/path/mock_rawmaskdir",
            "outliers_dir": "/my/path/mock_outliersdir",
            "subject_id": "Lola",
            "delta_TE": 5,
            "partial_fourier_factor": 1,
            "parallel_acceleration_factor": 2,
            "negative_sign": False,
            "echo_spacing": None,
            "EPI_factor": None,
            "b0_field": 3.0,
            "water_fat_shift": 4.68
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("pyconnectomist.preproc.susceptibility.exec_file")
    @mock.patch("os.path")
    def test_manufacturermiss_raise(self, mock_path, mock_exec):
        """ No manufacturer -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_exec.return_value = {
            "acquisitionParameters": {}
        }

        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          susceptibility_correction, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.susceptibility.exec_file")
    @mock.patch("os.path")
    def test_manufacturer_raise(self, mock_path, mock_exec):
        """ No manufacturer -> raise ConnectomistBadManufacturerNameError.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_exec.return_value = {
            "acquisitionParameters": {
                "manufacturer": "WRONG"
            }
        }

        # Test execution
        self.assertRaises(ConnectomistBadManufacturerNameError,
                          susceptibility_correction, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.susceptibility.exec_file")
    @mock.patch("os.path")
    def test_params_raise(self, mock_path, mock_exec):
        """ Wrong parameters -> raise ConnectomistMissingParametersError.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_exec.return_value = {
            "acquisitionParameters": {
                "manufacturer": "Siemens"
            }
        }

        # Test execution
        self.assertRaises(ConnectomistMissingParametersError,
                          susceptibility_correction, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.susceptibility.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.susceptibility.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("pyconnectomist.preproc.susceptibility.exec_file")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_exec, mock_params,
                              mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_exec.return_value = {
            "acquisitionParameters": {
                "manufacturer": "Siemens"
            }
        }
        kwargs = copy.copy(self.kwargs)
        kwargs["echo_spacing"] = 1

        # Test execution
        outdir = susceptibility_correction(**kwargs)
        expected_files = (
            "b0_magnitude.ima", "b0_phase.ima", "acquisition_parameters.py")
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(len(mock_params.call_args_list) == 1)
        self.assertEqual([
            mock.call(kwargs["raw_dwi_dir"], elem) for elem in expected_files],
            mock_path.join.call_args_list)
        self.assertEqual([
            mock.call(os.path.join(kwargs["raw_dwi_dir"], expected_files[2]))],
            mock_exec.call_args_list)


if __name__ == "__main__":
    unittest.main()
