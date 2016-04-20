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
from pyconnectomist.tractography.mask import tractography_mask
from pyconnectomist.exceptions import ConnectomistBadFileError


class ConnectomistMask(unittest.TestCase):
    """ Test the Connectomist 'Tractography mask' tab:
    'pyconnectomist.tractography.mask.tractography_mask'
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
            "morphologist_dir": "/my/path/mock_morphologist",
            "add_cerebelum": False,
            "add_commissures": True,
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
        mock_path.isfile.side_effect = [False, True, True, True]

        # Test execution
        self.assertRaises(ConnectomistBadFileError, tractography_mask,
                          **self.kwargs)

    @mock.patch("pyconnectomist.tractography.mask.ConnectomistWrapper."
                "create_parameter_file")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_params):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"
        mock_path.join.side_effect = lambda *x: x[-1]
        mock_path.isfile.side_effect = [True, True, True, True]

        # Test execution
        outdir = tractography_mask(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertEqual(len(mock_params.call_args_list), 1)
        self.assertEqual(len(self.mock_popen.call_args_list), 2)
        self.assertEqual([
            mock.call("{0}.APC".format(self.kwargs["subject_id"])),
            mock.call("nobias_{0}.han".format(self.kwargs["subject_id"])),
            mock.call("nobias_{0}.nii.gz".format(self.kwargs["subject_id"])),
            mock.call("voronoi_{0}.nii.gz".format(self.kwargs["subject_id"]))],
            mock_path.isfile.call_args_list)


if __name__ == "__main__":
    unittest.main()
