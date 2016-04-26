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
from pyconnectomist.tractography.tractography import tractography
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError


class ConnectomistTractography(unittest.TestCase):
    """ Test the Connectomist 'Tractography' tab:
    'pyconnectomist.tractography.tractography.tractography'
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
            "subject_id": "Lola",
            "mask_dir": "/my/path/mock_maskdir",
            "model": "aqbi",
            "model_dir": "/my/path/mock_modeldir",
            "registration_dir": "/my/path/mock_registrationdir",
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_bundlemaperror_raise(self):
        """ A bad bundlemap -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["bundlemap"] = "WRONG"
        self.assertRaises(ConnectomistError, tractography,
                          **wrong_kwargs)

    def test_trackingtypeerror_raise(self):
        """ A bad tracking type -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["tracking_type"] = "WRONG"
        self.assertRaises(ConnectomistError, tractography,
                          **wrong_kwargs)

    @mock.patch("os.path")
    def test_badfileerror_raise(self, mock_path):
        """ A bad input file -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [False, True, True, True, True, True,
                                        True]

        # Test execution
        self.assertRaises(ConnectomistBadFileError, tractography,
                          **self.kwargs)

    @mock.patch("pyconnectomist.tractography.tractography.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.tractography.tractography.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_params, mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_path.isfile.side_effect = [True, True, True, True, True, True,
                                        True]

        # Test execution
        outdir = tractography(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertEqual(len(mock_params.call_args_list), 1)
        self.assertEqual(len(self.mock_popen.call_args_list), 2)
        self.assertEqual([
            mock.call(self.kwargs["mask_dir"], "tractography_mask.ima"),
            mock.call(self.kwargs["model_dir"],
                      "{0}_odf_site_map.sitemap".format(self.kwargs["model"])),
            mock.call(self.kwargs["model_dir"],
                      "{0}_odf_texture_map.texturemap".format(
                          self.kwargs["model"])),
            mock.call(self.kwargs["model_dir"],
                      "{0}_rgb.ima".format(self.kwargs["model"])),
            mock.call(self.kwargs["registration_dir"], "t1.ima"),
            mock.call(self.kwargs["registration_dir"], "dw_to_t1.trm"),
            mock.call(self.kwargs["registration_dir"], "t1_to_dw.trm")],
            mock_path.join.call_args_list)
        self.assertEqual([
            mock.call(os.path.join(self.kwargs["mask_dir"],
                                   "tractography_mask.ima")),
            mock.call(os.path.join(self.kwargs["model_dir"],
                                   "{0}_odf_site_map.sitemap".format(
                                       self.kwargs["model"]))),
            mock.call(os.path.join(self.kwargs["model_dir"],
                                   "{0}_odf_texture_map.texturemap".format(
                                       self.kwargs["model"]))),
            mock.call(os.path.join(self.kwargs["model_dir"],
                                   "{0}_rgb.ima".format(
                                       self.kwargs["model"]))),
            mock.call(os.path.join(self.kwargs["registration_dir"],
                                   "t1.ima")),
            mock.call(os.path.join(self.kwargs["registration_dir"],
                                   "dw_to_t1.trm")),
            mock.call(os.path.join(self.kwargs["registration_dir"],
                                   "t1_to_dw.trm"))],
            mock_path.isfile.call_args_list)


if __name__ == "__main__":
    unittest.main()
