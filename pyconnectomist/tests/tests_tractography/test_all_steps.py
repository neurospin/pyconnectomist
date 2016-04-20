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
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist module
from pyconnectomist.tractography.all_steps import complete_tractography
from pyconnectomist.tractography.all_steps import STEPS
from pyconnectomist.exceptions import ConnectomistError


class ConnectomistTractography(unittest.TestCase):
    """ Test the Connectomist runs all tractography tabs function:
    'pyconnectomist.tractography.all_steps.complete_tractography'
    """
    def setUp(self):
        """ Define function parameters.
        """
        self.kwargs = {
            "outdir": "/my/path/mock_outdir",
            "dwi_preproc_dir": "/my/path/mock_preprocdir",
            "morphologist_dir": "/my/path/mock_morphologist",
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
            "add_cerebelum": False,
            "add_commissures": True,
            "tracking_type": "streamline_regularize_deterministic",
            "bundlemap": "vtkbundlemap",
            "min_fiber_length": 5.,
            "max_fiber_length": 300.,
            "aperture_angle": 30.,
            "forward_step": 0.2,
            "voxel_sampler_point_count": 1,
            "gibbs_temperature": 1.,
            "storing_increment": 10,
            "output_orientation_count": 500,
            "path_connectomist": "/my/path/mock_connectomist"
        }

    @mock.patch("glob.glob")
    @mock.patch("os.path")
    def test_badregistrationdir_raise(self, mock_path, mock_glob):
        """ A wrong registration dir -> raise ConnectomistError.
        """
        # Set the mocked functions returned values
        registration_dir = "/my/path/mock_registrationdir"
        mock_glob.return_value = [registration_dir]
        mock_path.isdir.side_effect = [True, False]

        # Test execution
        self.assertRaises(ConnectomistError, complete_tractography,
                          **self.kwargs)

    @mock.patch("pyconnectomist.tractography.all_steps.dwi_local_modeling")
    @mock.patch("pyconnectomist.tractography.all_steps.tractography_mask")
    @mock.patch("pyconnectomist.tractography.all_steps.tractography")
    @mock.patch("glob.glob")
    @mock.patch("os.path")
    @mock.patch("os.mkdir")
    def test_normal_execution(self, mock_mkdir, mock_path, mock_glob,
                              mock_tract, mock_mask, mock_model):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        registration_dir = "/my/path/mock_registrationdir"
        mock_glob.return_value = [registration_dir]
        mock_path.isdir.side_effect = [False, True]
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]

        # Test execution
        output_files = complete_tractography(**self.kwargs)
        self.assertEqual([
            mock.call(self.kwargs["outdir"]), mock.call(registration_dir)],
            mock_path.isdir.call_args_list)
        self.assertEqual([
            mock.call(self.kwargs["outdir"])],
            mock_mkdir.call_args_list)
        self.assertEqual([
            mock.call(self.kwargs["dwi_preproc_dir"], "*Anatomy_Talairach"),
            mock.call(self.kwargs["outdir"],
                      STEPS[0].format(self.kwargs["model"])),
            mock.call(self.kwargs["outdir"], STEPS[1]),
            mock.call(self.kwargs["outdir"],
                      STEPS[2].format(self.kwargs["tracking_type"]))],
            mock_path.join.call_args_list)
        self.assertEqual([
            mock.call(os.path.join(self.kwargs["dwi_preproc_dir"],
                      "*Anatomy_Talairach"))],
            mock_glob.call_args_list)
        self.assertEqual(len(mock_tract.call_args_list), 1)
        self.assertEqual(len(mock_mask.call_args_list), 1)
        self.assertEqual(len(mock_model.call_args_list), 1)


if __name__ == "__main__":
    unittest.main()
