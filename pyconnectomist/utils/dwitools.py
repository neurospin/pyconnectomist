##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
Utility Python functions to load diffusion metadata.
"""

# System import
import numpy
import math
import os
import numpy as np


def read_bvals_bvecs(bvals_path, bvecs_path, min_bval=100.):
    """ Read b-values and associated b-vectors.

    Parameters
    ----------
    bvals_path: str
        path to the diffusion b-values file.
    bvecs_path: str
        path to the diffusion b-vectors file.
    min_bval: float, optional
        if a b-value under this threshold is detected raise an ValueError.

    Returns
    -------
    bvals: array (N, )
        array containing the diffusion b-values.
    bvecs: array (N, 3)
        array containing the diffusion b-vectors.
    nb_shells: int
        the number of shells.
    nb_nodiff: int
        the number of no diffusion weighted images.

    Raises
    ------
    ValueError: if the b-values or the corresponding b-vectors have not
        matching sizes this exception is raised.
    """
    # Read .bval & .bvecs files
    bvals = np.loadtxt(bvals_path)
    bvecs = np.loadtxt(bvecs_path)

    # Check consistency between bvals and associated bvecs
    if bvecs.ndim != 2:
        raise ValueError("b-vectors file should be saved as a two dimensional "
                         "array: '{0}'.".format(bvecs_path))
    if bvals.ndim != 1:
        raise ValueError("b-values file should be saved as a one dimensional "
                         "array: '{0}'.".format(bvals_path))
    if bvecs.shape[1] > bvecs.shape[0]:
        bvecs = bvecs.T
    if bvals.shape[0] != bvecs.shape[0]:
        raise ValueError("b-values and b-vectors shapes do not correspond.")

    # Infer nb of T2 and nb of shells.
    nb_nodiff = np.sum(bvals == 0)  # nb of volumes where bvalue=0
    bvals_set = set(bvals) - {0}    # set of non-zero bvalues
    nb_shells = len(bvals_set)
    if min(bvals_set) < min_bval:
        raise ValueError("Small b-values detected (<{0}) in '{1}'.".format(
            min_bval, bvals_path))

    return bvals, bvecs, nb_shells, nb_nodiff
