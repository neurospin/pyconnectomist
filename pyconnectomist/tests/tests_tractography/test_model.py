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
from pyconnectomist.tractography.model import dwi_local_modeling
from pyconnectomist.tractography.model import export_scalars_to_nifti
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError


class ConnectomistDWIModel(unittest.TestCase):
    """ Test the Connectomist 'Local modeling' tab:
    'pyconnectomist.tractography.model.dwi_local_modeling'
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
            "registered_dwi_dir": "/my/path/mock_regitereddwidir",
            "eddy_motion_dir": "/my/path/mock_eddydir",
            "rough_mask_dir": "/my/path/mock_maskdir",
            "subject_id": "Lola",
            "model": "aqbi",
            "order": 4,
            "aqbi_laplacebeltrami_sharpefactor": 0.0,
            "regularization_lccurvefactor": 0.006,
            "dti_estimator": "linear",
            "constrained_sd": False,
            "sd_kernel_type": "symmetric_tensor",
            "sd_kernel_lower_fa": 0.65,
            "sd_kernel_upper_fa": 0.85,
            "sd_kernel_voxel_count": 300,
            "rgbscale": 1.0,
            "path_connectomist": "/my/path/mock_connectomist"
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("os.path")
    def test_badfileerror_raise(self, mock_path):
        """ A bad input file -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [False, True, True, True, True]

        # Test execution
        self.assertRaises(ConnectomistBadFileError, dwi_local_modeling,
                          **self.kwargs)

    @mock.patch("os.path")
    def test_modelerror_raise(self, mock_path):
        """ A bad model -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, True, True, True]

        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["model"] = "WRONG"
        self.assertRaises(ConnectomistError, dwi_local_modeling,
                          **wrong_kwargs)

    @mock.patch("os.path")
    def test_estimatorerror_raise(self, mock_path):
        """ A bad estimator -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, True, True, True]

        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["dti_estimator"] = "WRONG"
        self.assertRaises(ConnectomistError, dwi_local_modeling,
                          **wrong_kwargs)

    @mock.patch("os.path")
    def test_constrainedsderror_raise(self, mock_path):
        """ A bad constrained_sd value -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, True, True, True]

        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["constrained_sd"] = "WRONG"
        self.assertRaises(ConnectomistError, dwi_local_modeling,
                          **wrong_kwargs)

    @mock.patch("os.path")
    def test_kernelerror_raise(self, mock_path):
        """ A bad kernel -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, True, True, True]

        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["sd_kernel_type"] = "WRONG"
        self.assertRaises(ConnectomistError, dwi_local_modeling,
                          **wrong_kwargs)

    @mock.patch("pyconnectomist.tractography.model.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.tractography.model.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_params, mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_path.isfile.side_effect = [True, True, True, True, True]

        # Test execution
        outdir = dwi_local_modeling(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertEqual(len(mock_params.call_args_list), 1)
        self.assertEqual(len(self.mock_popen.call_args_list), 2)
        self.assertEqual([
            mock.call(self.kwargs["eddy_motion_dir"],
                      "dw_wo_eddy_current_and_motion.ima"),
            mock.call(self.kwargs["rough_mask_dir"], "mask.ima"),
            mock.call(self.kwargs["registered_dwi_dir"], "t1.ima"),
            mock.call(self.kwargs["eddy_motion_dir"],
                      "t2_wo_eddy_current_and_motion.ima"),
            mock.call(self.kwargs["registered_dwi_dir"], "dw_to_t1.trm")],
            mock_path.join.call_args_list)
        self.assertEqual([
            mock.call(os.path.join(self.kwargs["eddy_motion_dir"],
                      "dw_wo_eddy_current_and_motion.ima")),
            mock.call(os.path.join(self.kwargs["rough_mask_dir"],
                      "mask.ima")),
            mock.call(os.path.join(self.kwargs["registered_dwi_dir"],
                      "t1.ima")),
            mock.call(os.path.join(self.kwargs["eddy_motion_dir"],
                      "t2_wo_eddy_current_and_motion.ima")),
            mock.call(os.path.join(self.kwargs["registered_dwi_dir"],
                      "dw_to_t1.trm"))],
            mock_path.isfile.call_args_list)


class ConnectomistModelExport(unittest.TestCase):
    """ Test the Connectomist 'Local modeling' tab Nifti export:
    'pyconnectomist.tractography.model.export_scalars_to_nifti'
    """
    def setUp(self):
        """ Define Function parameters.
        """
        self.kwargs = {
            "model_dir": "/my/path/mock_modeldir",
            "model": "qba",
            "outdir": "/my/path/mock_outdir",
            "gfafilename": "gfa",
            "mdfilename": "md"
        }

    @mock.patch("pyconnectomist.tractography.model.os.mkdir")
    def test_badfileerror_execution(self, mock_mkdir):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          export_scalars_to_nifti, **self.kwargs)

    @mock.patch("pyconnectomist.tractography.model.ptk_gis_to_nifti")
    @mock.patch("pyconnectomist.tractography.model.os.path.isdir")
    @mock.patch("pyconnectomist.tractography.model.os.path.isfile")
    @mock.patch("pyconnectomist.tractography.model.os.mkdir")
    def test_normal_execution(self, mock_mkdir, mock_isfile, mock_isdir,
                              mock_conversion):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_isfile.side_effect = [True, True]
        mock_isdir.side_effect = [False]
        mock_conversion.side_effect = lambda *x: x[-1]

        # Test execution
        outfiles = export_scalars_to_nifti(**self.kwargs)
        expected_outfiles = (
            os.path.join(self.kwargs["outdir"],
                         self.kwargs["gfafilename"] + ".nii.gz"),
            os.path.join(self.kwargs["outdir"],
                         self.kwargs["mdfilename"] + ".nii.gz"))
        expected_files = [
            os.path.join(
                self.kwargs["model_dir"],
                "{0}_gfa.ima".format(self.kwargs["model"])),
            os.path.join(
                self.kwargs["model_dir"],
                "{0}_mean_diffusivity.ima".format(self.kwargs["model"]))]
        self.assertEqual(expected_outfiles, outfiles)
        self.assertEqual([mock.call(self.kwargs["outdir"])],
                         mock_isdir.call_args_list)
        self.assertEqual([mock.call(self.kwargs["outdir"])],
                         mock_mkdir.call_args_list)
        self.assertEqual([mock.call(elem) for elem in expected_files],
                         mock_isfile.call_args_list)
        self.assertEqual([mock.call(expected_files[0], expected_outfiles[0]),
                          mock.call(expected_files[1], expected_outfiles[1])],
                         mock_conversion.call_args_list)


if __name__ == "__main__":
    unittest.main()
