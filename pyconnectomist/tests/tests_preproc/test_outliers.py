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
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist import
from pyconnectomist.preproc.outliers import outlying_slice_detection


class ConnectomistOutliers(unittest.TestCase):
    """ Test the Connectomist 'Outliers' tab:
    'pyconnectomist.preproc.outliers.outlying_slice_detection'
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
            "subject_id": "Lola"
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("pyconnectomist.preproc.outliers.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.outliers.ConnectomistWrapper."
                "create_parameter_file")
    def test_normal_execution(self, mock_params, mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"

        # Test execution
        outdir = outlying_slice_detection(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(len(mock_params.call_args_list) == 1)


if __name__ == "__main__":
    unittest.main()
