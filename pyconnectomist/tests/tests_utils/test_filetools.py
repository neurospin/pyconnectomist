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
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistRuntimeError
from pyconnectomist.utils.filetools import ptk_nifti_to_gis
from pyconnectomist.utils.filetools import ptk_gis_to_nifti
from pyconnectomist.utils.filetools import ptk_concatenate_volumes
from pyconnectomist.utils.filetools import ptk_split_t2_and_diffusion
from pyconnectomist.utils.filetools import ptk_bundle_to_trk
from pyconnectomist.utils.filetools import exec_file


class ConnectomistBundleToTrk(unittest.TestCase):
    """ Test the Connectomist bundles to trackvis conversion:
    'pyconnectomist.utils.filetools.ptk_bundle_to_trk'
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_bundle_to_trk,
                          "bundle.bundles", "trk")

    @mock.patch("pyconnectomist.utils.filetools.os.path")
    def test_normal_execution(self, mock_path):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True]

        # Test execution
        output_file = ptk_bundle_to_trk("bundle.bundles", "trk")
        self.assertEqual(output_file, "trk.trk")
        self.assertEqual([mock.call("bundle.bundles")],
                         mock_path.isfile.call_args_list)
        self.assertTrue(len(self.mock_popen.call_args_list) == 2)


class ConnectomistNiftiToGis(unittest.TestCase):
    """ Test the Connectomist nifti to gis conversion:
    'pyconnectomist.utils.filetools.ptk_nifti_to_gis'
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_nifti_to_gis,
                          "nifti.nii.gz", "gis")

    @mock.patch("os.path")
    def test_normal_execution(self, mock_path):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, False]

        # Test execution
        output_files = ptk_nifti_to_gis("nifti.nii.gz", "gis")
        self.assertEqual(output_files, "gis.ima")
        self.assertEqual([mock.call("nifti.nii.gz")],
                         mock_path.isfile.call_args_list)
        self.assertTrue(len(self.mock_popen.call_args_list) == 2)


class ConnectomistGitToNifti(unittest.TestCase):
    """ Test the Connectomist gis to nifti conversion:
    'pyconnectomist.utils.filetools.ptk_gis_to_nifti'
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_gis_to_nifti,
                          "gis.ima", "nifti.nii.gz")

    @mock.patch("pyconnectomist.utils.filetools.gz_compress")
    @mock.patch("os.path")
    def test_normal_execution(self, mock_path, mock_gz):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, False]
        mock_gz.return_value = "out_nifti.nii.gz"

        # Test execution
        output_files = ptk_gis_to_nifti("gis.ima", "nifti.nii.gz")
        self.assertEqual(output_files, "out_nifti.nii.gz")
        self.assertEqual([mock.call("gis.ima")],
                         mock_path.isfile.call_args_list)
        self.assertTrue(len(self.mock_popen.call_args_list) == 2)


class ConnectomistConcatenate(unittest.TestCase):
    """ Test the Connectomist function that concatenates volumes:
    'pyconnectomist.utils.filetools.ptk_concatenate_volumes'
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_concatenate_volumes,
                          ["input1", "input2"], "output", axis="t")

    @mock.patch("os.path")
    def test_normal_execution(self, mock_path):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, True, False]

        # Test execution
        output_path = ptk_concatenate_volumes(["input1", "input2"], "output",
                                              axis="t")
        self.assertEqual(output_path, "output.ima")
        self.assertEqual([mock.call("input1"), mock.call("input2")],
                         mock_path.isfile.call_args_list)
        self.assertTrue(len(self.mock_popen.call_args_list) == 2)


class ConnectomistSplit(unittest.TestCase):
    """ Test the Connectomist function that split non weighted from weighted
    volumes:
    'pyconnectomist.utils.filetools.ptk_split_t2_and_diffusion'
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

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_badfileerror_raise(self):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_split_t2_and_diffusion,
                          "t2_dw_input", "t2_output", "dw_output")

    @mock.patch("os.path")
    def test_badtypeerror_raise(self, mock_path):
        """ A wrong input type -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, False]

        # Test execution
        self.assertRaises(ConnectomistBadFileError, ptk_split_t2_and_diffusion,
                          "t2_dw_input", "t2_output", "dw_output")

    @mock.patch("os.path")
    def test_normal_execution(self, mock_path):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [True, False]

        # Test execution
        output_files = ptk_split_t2_and_diffusion(
            "t2_dw_input.ima", "t2_output", "dw_output")
        expected_files = ("t2_output.ima", "dw_output.ima")
        self.assertEqual(output_files, expected_files)
        self.assertEqual([mock.call("t2_dw_input.ima")],
                         mock_path.isfile.call_args_list)
        self.assertTrue(len(self.mock_popen.call_args_list) == 4)


class ConnectomistExecFile(unittest.TestCase):
    """ Test the Connectomist function that executes a file in a dictionary:
    'pyconnectomist.utils.filetools.exec_file'
    """
    def test_normal_execution(self):
        """ Test the normal behaviour of the function.
        """
        # Test execution
        from pyconnectomist import info
        exec_dict = exec_file(info.__file__.replace(".pyc", ".py"))
        self.assertEqual(exec_dict["NAME"], "pyConnectomist")


if __name__ == "__main__":
    unittest.main()
