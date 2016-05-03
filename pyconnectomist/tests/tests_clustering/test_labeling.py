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
from pyconnectomist.clustering.labeling import fast_bundle_labeling
from pyconnectomist.clustering.labeling import export_bundles_to_trk
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError


class ConnectomistFastLabeling(unittest.TestCase):
    """ Test the Connectomist 'Fast bundle labeling' tab:
    'pyconnectomist.clustering.labeling.fast_bundle_labeling'
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
            "registered_dwi_dir": "/my/path/mock_regdwidir",
            "morphologist_dir": "/my/path/mock_morphologistdir",
            "paths_bundle_map": ["/my/path/mock_bundle1",
                                 "/my/path/mock_bundle2"],
            "atlas": "Guevara long bundle",
            "custom_atlas_dir": None,
            "bundle_names": None,
            "nb_fibers_to_process_at_once": 50000,
            "resample_fibers": True,
            "subject_id": "Lola",
            "remove_temporary_files": True,
            "path_connectomist": "/my/path/mock_connectomist"
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    def test_atlaserror_raise(self):
        """ A bad atlas name -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["atlas"] = "WRONG"
        self.assertRaises(ConnectomistError, fast_bundle_labeling,
                          **wrong_kwargs)

    def test_customdirerror_raise(self):
        """ A bad atlas name when custum dir -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["custom_atlas_dir"] = "WRONG"
        self.assertRaises(ConnectomistError, fast_bundle_labeling,
                          **wrong_kwargs)

    def test_bundlesderror_raise(self):
        """ A bad bundle name -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["bundle_names"] = ["WRONG"]
        self.assertRaises(ConnectomistError, fast_bundle_labeling,
                          **wrong_kwargs)

    def test_badatlasdirerror_raise(self):
        """ A bad atlas dir -> raise ConnectomistError.
        """
        # Test execution
        wrong_kwargs = copy.copy(self.kwargs)
        wrong_kwargs["atlas"] = "custom"
        wrong_kwargs["custom_atlas_dir"] = "WRONG"
        self.assertRaises(ConnectomistError, fast_bundle_labeling,
                          **wrong_kwargs)

    @mock.patch("os.path")
    def test_badfileerror_raise(self, mock_path):
        """ A bad input file -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.isfile.side_effect = [False, True, True, True]

        # Test execution
        self.assertRaises(ConnectomistBadFileError, fast_bundle_labeling,
                          **self.kwargs)

    @mock.patch("pyconnectomist.clustering.labeling.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.clustering.labeling.ConnectomistWrapper."
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
        outdir = fast_bundle_labeling(**self.kwargs)
        dwtot1file = os.path.join(self.kwargs["registered_dwi_dir"],
                                  "dw_to_t1.trm")
        t1total = os.path.join(
                self.kwargs["morphologist_dir"], self.kwargs["subject_id"],
                "t1mri", "default_acquisition", "registration",
                "RawT1-{0}_default_acquisition_TO_Talairach-ACPC.trm".format(
                    self.kwargs["subject_id"]))
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertEqual(len(mock_params.call_args_list), 1)
        self.assertEqual(len(self.mock_popen.call_args_list), 2)
        self.assertEqual([
            mock.call(self.kwargs["paths_bundle_map"][0]),
            mock.call(self.kwargs["paths_bundle_map"][1]),
            mock.call(dwtot1file), mock.call(t1total)],
            mock_path.isfile.call_args_list)


class ConnectomistLabelingExport(unittest.TestCase):
    """ Test the Connectomist 'Fast bundle labeling' tab Nifti export:
    'pyconnectomist.clustering.labeling.export_bundles_to_trk'
    """
    def setUp(self):
        """ Define Function parameters.
        """
        self.kwargs = {
            "labeling_dir": "/my/path/mock_labelingdir",
            "outdir": "/my/path/mock_outdir"
        }

    @mock.patch("pyconnectomist.clustering.labeling.ptk_bundle_to_trk")
    @mock.patch("pyconnectomist.clustering.labeling.os.path.isdir")
    @mock.patch("pyconnectomist.clustering.labeling.glob.glob")
    @mock.patch("pyconnectomist.clustering.labeling.os.mkdir")
    @mock.patch("pyconnectomist.clustering.labeling.os.makedirs")
    def test_normal_execution(self, mock_mkdirs, mock_mkdir, mock_glob,
                              mock_isdir, mock_conversion):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_isdir.return_value = False
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_glob.return_value = [
            os.path.join(self.kwargs["labeling_dir"], "bundleMapsReferential",
                         "region1", "bundle1.bundlesdata"),
            os.path.join(self.kwargs["labeling_dir"], "bundleMapsReferential",
                         "region2", "bundle2.bundlesdata")]

        # Test execution
        bundles = export_bundles_to_trk(**self.kwargs)
        bundlesdata = [item.replace("bundlesdata", "bundles")
                       for item in mock_glob.return_value]
        expected_bundles = [
            os.path.join(self.kwargs["outdir"], "bundles", "region1",
                         "bundle1.trk"),
            os.path.join(self.kwargs["outdir"], "bundles", "region2",
                         "bundle2.trk")]
        self.assertEqual(expected_bundles, bundles)
        self.assertEqual([
            mock.call(self.kwargs["outdir"]),
            mock.call(os.path.dirname(expected_bundles[0])),
            mock.call(os.path.dirname(expected_bundles[1]))],
            mock_isdir.call_args_list)
        self.assertEqual([mock.call(self.kwargs["outdir"])],
                         mock_mkdir.call_args_list)
        self.assertEqual([
            mock.call(bundlesdata[0], expected_bundles[0]),
            mock.call(bundlesdata[1], expected_bundles[1])],
            mock_conversion.call_args_list)


if __name__ == "__main__":
    unittest.main()
