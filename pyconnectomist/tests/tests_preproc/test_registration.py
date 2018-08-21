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
import nibabel
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
            "raw_dwi_dir": "/my/path/mock_rawdwidir",
            "morphologist_dir": "/my/path/mock_morphologistdir",
            "subject_id": "Lola",
            "t1_foot_zcropping": 0
        }
        self.t1img = nibabel.Nifti1Image(numpy.zeros((2, 3, 4)), numpy.eye(4))

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("pyconnectomist.preproc.registration.os.path")
    @mock.patch("pyconnectomist.preproc.registration.glob.glob")
    def test_badfileerror_raise(self, mock_glob, mock_path):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_glob.return_value = [self.kwargs["morphologist_dir"]]
        mock_path.isfile.side_effect = [False]
        mock_path.join.side_effect = lambda *x: "/".join(x)

        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          dwi_to_anatomy, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.registration.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.registration.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("pyconnectomist.preproc.registration.ptk_nifti_to_gis")
    @mock.patch("pyconnectomist.preproc.registration.nibabel.load")
    @mock.patch("pyconnectomist.preproc.registration.os.mkdir")
    @mock.patch("pyconnectomist.preproc.registration.os.path")
    @mock.patch("pyconnectomist.preproc.registration.glob.glob")
    def test_normal_execution(self, mock_glob, mock_path, mock_mkdir,
                              mock_load, mock_conversion, mock_params,
                              mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_glob.side_effect = [
            [self.kwargs["morphologist_dir"] + os.sep +
             "{0}.APC".format(self.kwargs["subject_id"])],
            [self.kwargs["morphologist_dir"] + os.sep +
             "{0}.nii.gz".format(self.kwargs["subject_id"])],
            []]
        mock_path.isfile.side_effect = [True, True, False]
        mock_path.isdir.side_effect = [False, True]
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: "/".join(x)
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_load.return_value = self.t1img

        # Test execution
        outdir = dwi_to_anatomy(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(len(mock_params.call_args_list) == 1)
        expected_infiles = (
            os.path.join(self.kwargs["morphologist_dir"],
                         "{0}.APC".format(self.kwargs["subject_id"])),
            os.path.join(self.kwargs["morphologist_dir"],
                         "{0}.nii.gz".format(self.kwargs["subject_id"])))
        self.assertEqual([mock.call(elem) for elem in expected_infiles],
                         mock_path.isfile.call_args_list)
        self.assertEqual([mock.call(self.kwargs["outdir"])],
                         mock_mkdir.call_args_list)
        self.assertEqual(len(mock_conversion.call_args_list), 2)


if __name__ == "__main__":
    unittest.main()
