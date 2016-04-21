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
from pyconnectomist.preproc.eddy import eddy_and_motion_correction
from pyconnectomist.preproc.eddy import export_eddy_motion_results_to_nifti


class ConnectomistEddy(unittest.TestCase):
    """ Test the Connectomist 'Eddy current & motion' tab:
    'pyconnectomist.preproc.eddy.eddy_and_motion_correction'
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
            "subject_id": "Lola",
            "corrected_dir": "/my/path/mock_correcteddir"
        }

    def tearDown(self):
        """ Run after each test.
        """
        self.popen_patcher.stop()

    @mock.patch("pyconnectomist.preproc.eddy.ConnectomistWrapper."
                "_connectomist_version_check")
    @mock.patch("pyconnectomist.preproc.eddy.ConnectomistWrapper."
                "create_parameter_file")
    def test_normal_execution(self, mock_params, mock_version):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_params.return_value = "/my/path/mock_parameters"

        # Test execution
        outdir = eddy_and_motion_correction(**self.kwargs)
        self.assertEqual(outdir, self.kwargs["outdir"])
        self.assertTrue(len(mock_params.call_args_list) == 1)


class ConnectomistEddyExport(unittest.TestCase):
    """ Test the Connectomist 'Eddy current & motion' tab Nifti export:
    'pyconnectomist.preproc.eddy.export_eddy_motion_results_to_nifti'
    """
    def setUp(self):
        """ Define Function parameters.
        """
        self.kwargs = {
            "eddy_motion_dir": "/my/path/mock_eddydir",
            "outdir": "/my/path/mock_outdir",
            "filename": "mock_dwi"
        }
        self.bvecs = numpy.array([[1, 0, 0], [0, 1, 0]])
        self.bvals = numpy.array([1500, 1500])

    @mock.patch("os.mkdir")
    def test_badfileerror_execution(self, mock_mkdir):
        """ A wrong input -> raise ConnectomistBadFileError.
        """
        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          export_eddy_motion_results_to_nifti, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.eddy.exec_file")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_gis_to_nifti")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_concatenate_volumes")
    @mock.patch("os.path")
    @mock.patch("os.mkdir")
    def test_bvalsmiss_raise(self, mock_mkdir, mock_path, mock_concat,
                             mock_conversion, mock_exec):
        """ No bvals -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_path.isfile.side_effect = [True] * 2 + [False]
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_exec.return_value = {
            "attributes": {
                "diffusion_gradient_orientations": self.bvecs
            }
        }

        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          export_eddy_motion_results_to_nifti, **self.kwargs)

    @mock.patch("pyconnectomist.preproc.eddy.exec_file")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_gis_to_nifti")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_concatenate_volumes")
    @mock.patch("os.path")
    @mock.patch("os.mkdir")
    def test_bvecsmiss_raise(self, mock_mkdir, mock_path, mock_concat,
                             mock_conversion, mock_exec):
        """ No bvecs -> raise ConnectomistBadFileError.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_path.isfile.side_effect = [True] * 2 + [False]
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_exec.return_value = {
            "attributes": {
                "bvalues": self.bvals
            }
        }

        # Test execution
        self.assertRaises(ConnectomistBadFileError,
                          export_eddy_motion_results_to_nifti, **self.kwargs)

    @mock.patch("numpy.savetxt")
    @mock.patch("pyconnectomist.preproc.eddy.exec_file")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_gis_to_nifti")
    @mock.patch("pyconnectomist.preproc.eddy.ptk_concatenate_volumes")
    @mock.patch("os.path")
    @mock.patch("os.mkdir")
    def test_normal_execution(self, mock_mkdir, mock_path, mock_concat,
                              mock_conversion, mock_exec, mock_savetxt):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        mock_path.join.side_effect = lambda *x: x[0] + "/" + x[1]
        mock_path.isfile.side_effect = [True] * 2 + [False]
        mock_conversion.side_effect = lambda *x: x[-1]
        mock_exec.return_value = {
            "attributes": {
                "bvalues": self.bvals,
                "diffusion_gradient_orientations": self.bvecs
            }
        }

        # Test execution
        outfiles = export_eddy_motion_results_to_nifti(**self.kwargs)
        expected_outfiles = (
            os.path.join(self.kwargs["outdir"],
                         self.kwargs["filename"] + ".nii.gz"),
            os.path.join(self.kwargs["outdir"],
                         self.kwargs["filename"] + ".bval"),
            os.path.join(self.kwargs["outdir"],
                         self.kwargs["filename"] + ".bvec"))
        expected_files = [
            os.path.join(self.kwargs["eddy_motion_dir"],
                         "t2_wo_eddy_current_and_motion.ima"),
            os.path.join(self.kwargs["eddy_motion_dir"],
                         "dw_wo_eddy_current_and_motion.ima"),
            os.path.join(self.kwargs["eddy_motion_dir"],
                         "t2_dw_wo_eddy_current_and_motion.ima")]
        self.assertEqual(expected_outfiles, outfiles)
        self.assertEqual([mock.call(self.kwargs["outdir"])],
                         mock_path.isdir.call_args_list)
        self.assertEqual([mock.call(elem) for elem in expected_files[:2]],
                         mock_path.isfile.call_args_list)
        self.assertEqual([mock.call(expected_files[:2], expected_files[2])],
                         mock_concat.call_args_list)
        self.assertEqual([mock.call(expected_files[2], expected_outfiles[0])],
                         mock_conversion.call_args_list)
        self.assertEqual([mock.call(expected_files[1] + ".minf")],
                         mock_exec.call_args_list)
        self.assertTrue(len(mock_savetxt.call_args_list) == 2)


if __name__ == "__main__":
    unittest.main()
