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
import nibabel


def extract_dwi_shells(dwi_nii_path, bvals_path, bvecs_path, outdir):
    """ Convert a multi-shell serie to multiple single shell series.

    Parameters
    ----------
    dwi_nii_path: str
        path to the diffusion volume file.
    bvals_path: str
        path to the diffusion b-values file.
    bvecs_path: str
        path to the diffusion b-vectors file.
    outdir: str
        path to the destination folder.

    Returns
    -------
    nodiff_file: str
        path to the mean b0 file.
    dwis: dict
        path the each shell 'dwi', 'bvals' and 'bvecs' files: b-values are
        the keys of this dictionary.
    """
    # Load input data
    dwi = nibabel.load(dwi_nii_path)
    dwi_array = dwi.get_data()
    real_bvals, real_bvecs, nb_shells, nb_nodiff = read_bvals_bvecs(
        bvals_path, bvecs_path, min_bval=100.)

    # Detect shell indices
    bvals = real_bvals.copy()
    bvecs = real_bvecs.copy()
    b0_indices = numpy.where(bvals < 50)[0].tolist()
    bvals[b0_indices] = 0
    bvals = [int(round(bval, -2)) for bval in bvals]
    bvals_set = set(bvals) - {0}

    # Create mean b0 image
    b0 = numpy.mean(dwi_array[..., b0_indices], axis=3)
    im = nibabel.Nifti1Image(b0, affine=dwi.get_affine())
    nodiff_file = os.path.join(outdir, "nodiff.nii.gz")
    nibabel.save(im, nodiff_file)
    b0.shape += (1, )

    # Create dwi for each shell
    dwis = {}
    bvals = numpy.asarray(bvals)
    for bval in bvals_set:

        # Get shell indices
        bval_outdir = os.path.join(outdir, str(bval))
        if not os.path.isdir(bval_outdir):
            os.mkdir(bval_outdir)
        shell_indices = numpy.where(bvals == bval)[0].tolist()

        # Create single shell dwi
        shell_dwi = dwi_array[..., shell_indices]
        shell_dwi = numpy.concatenate((b0, shell_dwi), axis=3)
        im = nibabel.Nifti1Image(shell_dwi, affine=dwi.get_affine())
        dwi_file = os.path.join(bval_outdir, "dwi.nii.gz")
        nibabel.save(im, dwi_file)

        # Create associated bvecs/bvals
        shell_bvecs = real_bvecs[shell_indices]
        shell_bvecs = numpy.concatenate((numpy.zeros((1, 3)), shell_bvecs),
                                        axis=0)
        bvecs_file = os.path.join(bval_outdir, "bvecs")
        numpy.savetxt(bvecs_file, shell_bvecs)
        shell_bvals = real_bvals[shell_indices]
        shell_bvals = numpy.concatenate((numpy.zeros((1, )), shell_bvals))
        bvals_file = os.path.join(bval_outdir, "bvals")
        numpy.savetxt(bvals_file, shell_bvals)

        # Update output structure
        dwis[bval] = {
            "bvals": bvals_file,
            "bvecs": bvecs_file,
            "dwi": dwi_file
        }

    return nodiff_file, dwis


def read_bvals_bvecs(bvals_path, bvecs_path, min_bval=200.):
    """ Read b-values and associated b-vectors.

    Parameters
    ----------
    bvals_path: str or list of str
        path to the diffusion b-values file(s).
    bvecs_path: str or list of str
        path to the diffusion b-vectors file(s).
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
    # Format input path
    if not isinstance(bvals_path, list):
        bvals_path = [bvals_path]
    if not isinstance(bvecs_path, list):
        bvecs_path = [bvecs_path]

    # Read .bval & .bvecs files
    bvals = None
    bvecs = None
    for bvalfile, bvecfile in zip(bvals_path, bvecs_path):
        if bvals is None:
            bvals = np.loadtxt(bvalfile)
        else:
            bvals = np.concatenate((bvals, np.loadtxt(bvalfile)))
        if bvecs is None:
            bvecs = np.loadtxt(bvecfile)
        else:
            axis = bvecs.shape.index(max(bvecs.shape))
            bvecs = np.concatenate((bvecs, np.loadtxt(bvecfile)), axis=axis)

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
    nb_nodiff = np.sum(bvals <= 50)  # nb of volumes where bvalue<50
    b0_set = set(bvals[bvals <= 50])
    bvals_set = set(bvals) - b0_set    # set of non-zero bvalues
    bvals_set = set([int(round(bval, -2)) for bval in list(bvals_set)])
    nb_shells = len(bvals_set)
    if min(bvals_set) < min_bval:
        raise ValueError("Small b-values detected (<{0}) in '{1}'.".format(
            min_bval, bvals_path))

    return bvals, bvecs, nb_shells, nb_nodiff
