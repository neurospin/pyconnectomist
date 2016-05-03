##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Tractography mask' tab.
"""

# System import
import os

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper
from pyconnectomist.utils.filetools import ptk_gis_to_nifti

# Boolean map used by Connectomist
BOOL_MAP = {
    False: 0,
    True: 2
}


def tractography_mask(
        outdir,
        subject_id,
        morphologist_dir,
        add_cerebelum=False,
        add_commissures=True,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Tractography mask computation.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    subject_id: str
        the subject code in study.
    morphologist_dir: str
        path to Morphologist directory.
    add_cerebelum: bool (optional, default False)
        if True add the cerebelum to the tractography mask.
    add_commissures: bool (optional, default False)
        if True add the commissures to the tractography mask.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get morphologist result files and check existance
    apcfile = os.path.join(
        morphologist_dir, subject_id, "t1mri", "default_acquisition",
        "{0}.APC".format(subject_id))
    histofile = os.path.join(
        morphologist_dir, subject_id, "t1mri", "default_acquisition",
        "default_analysis", "nobias_{0}.han".format(subject_id))
    t1file = os.path.join(
        morphologist_dir, subject_id, "t1mri", "default_acquisition",
        "default_analysis", "nobias_{0}.nii.gz".format(subject_id))
    voronoifile = os.path.join(
        morphologist_dir, subject_id, "t1mri", "default_acquisition",
        "default_analysis", "segmentation",
        "voronoi_{0}.nii.gz".format(subject_id))
    for fpath in (apcfile, histofile, t1file, voronoifile):
        if not os.path.isfile(fpath):
            raise ConnectomistBadFileError(fpath)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Tractography-Mask"
    parameters_dict = {
        "_subjectName": subject_id,
        "addCerebellum": BOOL_MAP[add_cerebelum],
        "addCommissures": BOOL_MAP[add_commissures],
        "addROIMask": 0,
        "fileNameCommissureCoordinates": apcfile,
        "fileNameHistogramAnalysis": histofile,
        "fileNameROIMaskToAdd": "",
        "fileNameROIMaskToRemove": "",
        "fileNameUnbiasedT1": t1file,
        "fileNameVoronoiMask": voronoifile,
        "outputWorkDirectory": outdir,
        "removeROIMask": 0,
        "removeTemporaryFiles": 2}

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir


def export_mask_to_nifti(
        mask_dir,
        outdir=None,
        filename="mask"):
    """ After Connectomist has done the tractography mask, convert the result
    to Nifti.

    Parameters
    ----------
    mask_dir: str
        path to the Connectomist 'Tractography mask' directory.
    outdir: str (optional)
        path to directory where to output:
        <outdir>/<filename>.nii.gz
        By default <outdir> is <mask_dir>.
    filename: str (optional)
        to change output filename, by default 'mask'.

    Returns
    -------
    mask: str
        the mask nifti image.
    """
    # Step 1 - Set outdir path and check directory existence
    if outdir is None:
        outdir = mask_dir
    else:
        if not os.path.isdir(outdir):  # If outdir does not exist, create it
            os.mkdir(outdir)

    # Step 2 - Convert to Nifti
    mask = os.path.join(mask_dir, "tractography_mask.ima")
    if not os.path.isfile(mask):
        raise ConnectomistBadFileError(mask)
    mask = ptk_gis_to_nifti(mask, os.path.join(outdir, "%s.nii.gz" % filename))

    return mask
