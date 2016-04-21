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

# pyConnectomist import
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.preproc.registration import dwi_to_anatomy


class ConnectomistRegistration(unittest.TestCase):
    """ Test the Connectomist 'Anatomy & Talairach' tab:
    'pyconnectomist.preproc.registration.dwi_to_anatomy'
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
            "corrected_dwi_dir": "/my/path/mock_correcteddwidir",
            "rough_mask_dir": "/my/path/mock_maskdir",
            "morphologist_dir": "/my/path/mock_morphologistdir",
            "subject_id": "Lola"
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("os.path")
    def test_badfileerror_raise(self, mock_path):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [False]
        mock_path.join.side_effect = lambda *x: (
            x[0] + "/" + x[1] + "/" + x[2] + "/" + x[3] + "/" + x[4])

        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          dwi_to_anatomy, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.registration.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.registration.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_params, mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, False]
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: (
            x[0] + "/" + x[1] + "/" + x[2] + "/" + x[3] + "/" + x[4])

        # Test execution
        outdir = dwi_to_anatomy(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(len(mock_params.call_args_list) == 1)
        expected_infiles = (
            os.path.join(self.kwargs["morphologist_dir"],
                         self.kwargs["subject_id"], "t1mri",
                         "default_acquisition",
                         "{0}.APC".format(self.kwargs["subject_id"])),
            os.path.join(self.kwargs["morphologist_dir"],
                         self.kwargs["subject_id"], "t1mri",
                         "default_acquisition",
                         "{0}.nii.gz".format(self.kwargs["subject_id"])))
        self.assertEqual([mock.call(elem) for elem in expected_infiles],
                         mock_path.isfile.call_args_list)


if __name__ == "__main__":
    unittest.main()
