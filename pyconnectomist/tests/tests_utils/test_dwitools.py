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
import numpy
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist module
from pyconnectomist.utils.dwitools import read_bvals_bvecs


class ConnectomistBvecsBvals(unittest.TestCase):
    """ Test the Connectomist bvecs/bvals loader:
    'pyconnectomist.utils.dwitools.read_bvals_bvecs'
    """

    @mock.patch("numpy.loadtxt")
    def test_bvecsdim_raise(self, mock_loadtxt):
        """ A wrong bvecs dimension -> raise ValueError.
        """
        # Set the mocked functions returned values
        bvecs = numpy.array([0, 1500, 1500])
        bvals = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        mock_loadtxt.side_effect = lambda x: {"dwi.bval": bvals,
                                              "dwi.bvec": bvecs}[x]

        # Test execution
        self.assertRaises(ValueError, read_bvals_bvecs, "dwi.bval", "dwi.bvec",
                          min_bval=100.)

    @mock.patch("numpy.loadtxt")
    def test_bvalssdim_raise(self, mock_loadtxt):
        """ A wrong bvals dimension -> raise ValueError.
        """
        # Set the mocked functions returned values
        bvecs = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        bvals = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        mock_loadtxt.side_effect = lambda x: {"dwi.bval": bvals,
                                              "dwi.bvec": bvecs}[x]

        # Test execution
        self.assertRaises(ValueError, read_bvals_bvecs, "dwi.bval", "dwi.bvec",
                          min_bval=100.)

    @mock.patch("numpy.loadtxt")
    def test_nbelems_raise(self, mock_loadtxt):
        """ Bvals&bvecs shape mismatch -> raise ValueError.
        """
        # Set the mocked functions returned values
        bvecs = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        bvals = numpy.array([0, 1500])
        mock_loadtxt.side_effect = lambda x: {"dwi.bval": bvals,
                                              "dwi.bvec": bvecs}[x]

        # Test execution
        self.assertRaises(ValueError, read_bvals_bvecs, "dwi.bval", "dwi.bvec",
                          min_bval=100.)

    @mock.patch("numpy.loadtxt")
    def test_bvalsthres_raise(self, mock_loadtxt):
        """ A wrong b-value -> raise ValueError.
        """
        # Set the mocked functions returned values
        bvecs = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]).T
        bvals = numpy.array([0, 1500, 10])
        mock_loadtxt.side_effect = lambda x: {"dwi.bval": bvals,
                                              "dwi.bvec": bvecs}[x]

        # Test execution
        self.assertRaises(ValueError, read_bvals_bvecs, "dwi.bval", "dwi.bvec",
                          min_bval=100.)

    @mock.patch("numpy.loadtxt")
    def test_normal_execution(self, mock_loadtxt):
        """ Test the normal behaviour of the function.
        """
        # Set the mocked functions returned values
        bvecs = numpy.array([[0, 0, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0]]).T
        bvals = numpy.array([0, 0, 1500, 150])
        mock_loadtxt.side_effect = lambda x: {"dwi.bval": bvals,
                                              "dwi.bvec": bvecs}[x]

        # Test execution
        output_files = read_bvals_bvecs("dwi.bval", "dwi.bvec", min_bval=100.)
        self.assertTrue(numpy.allclose(output_files[0], bvals))
        self.assertTrue(numpy.allclose(output_files[1], bvecs.T))
        self.assertTrue(output_files[2] == 2)
        self.assertTrue(output_files[3] == 2)


if __name__ == "__main__":
    unittest.main()
