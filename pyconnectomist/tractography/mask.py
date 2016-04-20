##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

# System import
import os

# Clindmri import
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper


bool_map = {
    False: 0,
    True: 2
}


def tractography_mask(
        outdir,
        subjectid,
        morphologist_dir,
        add_cerebelum=False,
        add_commissures=True,
        nb_tries=10,
        path_connectomist=(
            "/i2bm/local/Ubuntu-14.04-x86_64/ptk/bin/connectomist")):
    """ Tractography mask computation.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    subjectid: str
        the subject code in study.
    morphologist_dir: str
        path to Morphologist directory.
    add_cerebelum: bool (optional, default False)
        if True add the cerebelum to the tractography mask.
    add_commissures: bool (optional, default False)
        if True add the commissures to the tractography mask.
    nb_tries: int (optional, default 10)
        nb of times to try an algorithm if it fails.
        It often crashes when running in parallel. The reason
        why it crashes is unknown.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get morphologist result files and check existance
    apcfile = os.path.join(
        morphologist_dir, subjectid, "t1mri", "default_acquisition",
        "{0}.APC".format(subjectid))
    histofile = os.path.join(
        morphologist_dir, subjectid, "t1mri", "default_acquisition",
        "default_analysis", "nobias_{0}.han".format(subjectid))
    t1file = os.path.join(
        morphologist_dir, subjectid, "t1mri", "default_acquisition",
        "default_analysis", "nobias_{0}.nii.gz".format(subjectid))
    voronoifile = os.path.join(
        morphologist_dir, subjectid, "t1mri", "default_acquisition",
        "default_analysis", "segmentation",
        "voronoi_{0}.nii.gz".format(subjectid))
    for fpath in (apcfile, histofile, t1file, voronoifile):
        if not os.path.isfile(fpath):
            raise ConnectomistBadFileError(fpath)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Tractography-Mask"
    parameters_dict = {
        '_subjectName': subjectid,
        'addCerebellum': bool_map[add_cerebelum],
        'addCommissures': bool_map[add_commissures],
        'addROIMask': 0,
        'fileNameCommissureCoordinates': apcfile,
        'fileNameHistogramAnalysis': histofile,
        'fileNameROIMaskToAdd': '',
        'fileNameROIMaskToRemove': '',
        'fileNameUnbiasedT1': t1file,
        'fileNameVoronoiMask': voronoifile,
        'outputWorkDirectory': outdir,
        'removeROIMask': 0,
        'removeTemporaryFiles': 2}

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir, nb_tries=nb_tries)

    return outdir
