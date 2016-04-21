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
import copy
import numpy
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist import
from pyconnectomist.exceptions import ConnectomistBadManufacturerNameError
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError
from pyconnectomist.preproc.qspace import data_import_and_qspace_sampling


class ConnectomistQspace(unittest.TestCase):
    """ Test the Connectomist 'DWI & Q-space' tab:
    'pyconnectomist.preproc.qspace.data_import_and_qspace_sampling'
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
            "dwi": "/my/path/mock_dwi.nii.gz",
            "bval": "/my/path/mock_dwi.bval",
            "bvec": "/my/path/mock_dwi.bvec",
            "outdir": "/my/path/mock_outdir",
            "subject_id": "Lola",
            "b0_magnitude": "/my/path/mock_b0_magnitude",
            "b0_phase": "/my/path/mock_b0_phase",
            "path_connectomist": "/my/path/mock_connectomist",
            "invertX": True,
            "invertY": False,
            "invertZ": False,
            "manufacturer": "Siemens",
            "subject_id": "Lola"
        }
        self.bvecs = numpy.array([[0, 0, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0]])
        self.bvals = numpy.array([0, 0, 1500, 1500])

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          data_import_and_qspace_sampling, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.qspace.ptk_nifti_to_gis")
    @mock.patch("os.path")
    @mock.patch("shutil.copyfile")
    @mock.patch("os.mkdir")
    def test_badmanufacturer_raise(self, mock_mkdir, mock_copyfile, mock_path,
                                   mock_conversion):
        """ A wrong manufacturer -> raise ConnectomistBadManufacturerNameError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True] * 5 + [False]
        mock_conversion.side_effect = lambda *x: x[-1]

        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["manufacturer"] = "WRONG"
        self.assertRaises(ConnectomistBadManufacturerNameError,
                          data_import_and_qspace_sampling, **wrong_kwargs)

    @mock.patch("pyconnectomist.preproc.qspace.read_bvals_bvecs")
    @mock.patch("pyconnectomist.preproc.qspace.ptk_nifti_to_gis")
    @mock.patch("os.path")
    @mock.patch("shutil.copyfile")
    @mock.patch("os.mkdir")
    def test_nbshell_raise(self, mock_mkdir, mock_copyfile, mock_path,
                           mock_conversion, mock_bvecs):
        """ A wrong qsapce sampling -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True] * 5 + [False]
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_bvecs.return_value = (self.bvals, self.bvecs, 2, 1)

        # Test execution
        self.assertRaises(ConnectomistError,
                          data_import_and_qspace_sampling, **self.kwargs)

    @mock.patch("numpy.savetxt")
    @mock.patch("pyconnectomist.preproc.qspace.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.qspace.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("pyconnectomist.preproc.qspace.read_bvals_bvecs")
    @mock.patch("pyconnectomist.preproc.qspace.ptk_nifti_to_gis")
    @mock.patch("os.path")
    @mock.patch("shutil.copyfile")
    @mock.patch("os.mkdir")
    def test_normal_execution(self, mock_mkdir, mock_copyfile, mock_path,
                              mock_conversion, mock_bvecs, mock_params,
                              mock_version, mock_savetxt):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isdir.return_value = False
        mock_path.isfile.side_effect = [True] * 8 + [False]
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_bvecs.return_value = (self.bvals, self.bvecs, 1, 2)
        mock_params.return_value = "/my/path/mock_parameters"

        # Test execution
        outdir = data_import_and_qspace_sampling(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(
            [mock.call(self.kwargs["outdir"])] == mock_mkdir.call_args_list)
        expected_copyfiles = [
            mock.call(self.kwargs["bval"],
                      self.kwargs["outdir"] + "/" + "dwi.bval"),
            mock.call(self.kwargs["bvec"],
                      self.kwargs["outdir"] + "/" + "dwi.bvec")]
        self.assertTrue(expected_copyfiles == mock_copyfile.call_args_list)
        expected_conversions = [
            mock.call(self.kwargs["dwi"],
                      self.kwargs["outdir"] + "/" + "dwi.ima"),
            mock.call(self.kwargs["b0_magnitude"],
                      self.kwargs["outdir"] + "/" + "b0_magnitude.ima"),
            mock.call(self.kwargs["b0_phase"],
                      self.kwargs["outdir"] + "/" + "b0_phase.ima")]
        self.assertTrue(expected_conversions == mock_conversion.call_args_list)
        self.assertTrue([
            mock.call(self.kwargs["outdir"] + "/" + "dwi.bval",
                      self.kwargs["outdir"] + "/" + "dwi.bvec")] ==
            mock_bvecs.call_args_list)
        self.assertTrue(len(mock_params.call_args_list) == 1)
        expected_saves = [
            mock.call(self.kwargs["outdir"] + "/" + "dwi.bval", self.bvals),
            mock.call(self.kwargs["outdir"] + "/" + "dwi.bvec", self.bvecs)]
        self.assertTrue(expected_saves, mock_savetxt.call_args_list)


if __name__ == "__main__":
    unittest.main()
