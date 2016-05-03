##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Fast bundle labeling' tab.
"""

# System import
import os
import glob

# Clindmri import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError
from pyconnectomist.wrappers import ConnectomistWrapper
from pyconnectomist.utils.filetools import ptk_bundle_to_trk

# Set for checking bundle names that can take values in a finite set
BUNDLE_NAMES = frozenset([
    "Arcuate_Anterior_Left",
    "Arcuate_Anterior_Right",
    "Arcuate_Left",
    "Arcuate_Posterior_Left",
    "Arcuate_Posterior_Right",
    "Arcuate_Right",
    "Cingulum_Long_Left",
    "Cingulum_Long_Right",
    "Cingulum_Short_Left",
    "Cingulum_Short_Right",
    "Cingulum_Temporal_Left",
    "Cingulum_Temporal_Right",
    "CorpusCallosum_Body",
    "CorpusCallosum_Genu",
    "CorpusCallosum_Rostrum",
    "CorpusCallosum_Splenium",
    "CorticoSpinalTract_Left",
    "CorticoSpinalTract_Right",
    "Fornix_Left",
    "Fornix_Right",
    "InferiorFrontoOccipital_Left",
    "InferiorFrontoOccipital_Right",
    "InferiorLongitudinal_Left",
    "InferiorLongitudinal_Right",
    "ThalamicRadiations_Anterior_Left",
    "ThalamicRadiations_Anterior_Right",
    "ThalamicRadiations_Inferior_Left",
    "ThalamicRadiations_Inferior_Right",
    "ThalamicRadiations_Motor_Left",
    "ThalamicRadiations_Motor_Right",
    "ThalamicRadiations_Parietal_Left",
    "ThalamicRadiations_Parietal_Right",
    "ThalamicRadiations_Posterior_Left",
    "ThalamicRadiations_Posterior_Right",
    "Uncinate_Left",
    "Uncinate_Right"
])

# Map atlas name to index used by Connectomist
INDEX_OF_ATLAS = {
    "Guevara long bundle":  0,
    "Guevara short bundle": 1,
    "custom":               2
}

# Boolean map used by Connectomist
BOOL_MAP = {
    False: 0,
    True: 2
}


def fast_bundle_labeling(
        outdir,
        registered_dwi_dir,
        morphologist_dir,
        subject_id,
        paths_bundle_map,
        atlas="Guevara long bundle",
        custom_atlas_dir=None,
        bundle_names=None,
        nb_fibers_to_process_at_once=50000,
        resample_fibers=True,
        remove_temporary_files=True,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Fast Bundle Labeling' tab.

    Parameters
    ----------
    outdir: str
        Path to the Connectomist output working directory.
    registered_dwi_dir: str
        path to Connectomist register DWI directory.
    morphologist_dir: str
        path to Morphologist directory.
    subject_id: str
        the subject identifier.
    paths_bundle_map: list of str
        Paths to the bundle maps.
    atlas: str, {["Guevara long bundle"], "Guevara short bundle", "custom"}
        Atlas to use.
    custom_atlas_dir: str, optional
        Path to directory where to find the custom atlas when 'atlas' is set
        to 'custom'.
    bundle_names: list of str, optional
        Names of the bundles to select.
    nb_fibers_to_process_at_once: int, optional
        Number of fibers to process at once, to avoid memory overflow.
    resample_fibers: bool, optional
        If True resample fibers, mandatory if fibers are not 21 points
        resampled.
    remove_temporary_files: bool, optional
        If True remove temporary files.
    path_connectomist: str, optional
        Path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Check input parameters
    if atlas not in set(INDEX_OF_ATLAS):
        raise ConnectomistError(
            "'{0}' atlas name not supported (must be in {1}).".format(
                atlas, set(INDEX_OF_ATLAS)))
    if custom_atlas_dir is not None:
        if atlas != "custom":
            raise ConnectomistError(
                "'atlas' argument has to be set to 'custom' when setting "
                "'custom_atlas_dir'.")
        if not os.path.isdir(custom_atlas_dir):
            raise ConnectomistError("'{0}' is not a valid atlas "
                                    "directory.".format(custom_atlas_dir))
    if bundle_names is not None:
        for bundle_name in bundle_names:
            if bundle_name not in BUNDLE_NAMES:
                raise ConnectomistError(
                    "'{0}' bundle name not supported (must be in {1}).".format(
                        bundle_name, BUNDLE_NAMES))
    else:
        bundle_names = BUNDLE_NAMES

    # Get Connectomist transformations
    dwtot1file = os.path.join(registered_dwi_dir, "dw_to_t1.trm")
    t1total = os.path.join(
            morphologist_dir, subject_id, "t1mri", "default_acquisition",
            "registration",
            "RawT1-{0}_default_acquisition_TO_Talairach-ACPC.trm".format(
                subject_id))

    # Check input parameter files existence
    required_files = paths_bundle_map + [dwtot1file, t1total]
    for path in required_files:
        if not os.path.isfile(path):
            raise ConnectomistBadFileError(path)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Fast-Bundle-Labelling"
    parameters_dict = {
        # Options are ordered like in the GUI

        # 'Input data' panel
        "inputBundleMapFileNames": " ".join(paths_bundle_map),
        "fileNameBundleMapToTalairachTransformation": dwtot1file,
        "fileNameT1ToTalairachTransformation": t1total,
        "atlasName": INDEX_OF_ATLAS[atlas],
        "customAtlasDirectory": custom_atlas_dir if custom_atlas_dir else "",

        # 'Bundle Selection' panel
        "bundleNameSelection": " ".join(bundle_names),

        # 'Labelling option' panel
        "fiberCount": nb_fibers_to_process_at_once,
        "doResampling": BOOL_MAP[resample_fibers],

        # 'Output option' panel
        "removeTemporaryFiles": BOOL_MAP[remove_temporary_files],

        # 'Work directory' panel
        "outputWorkDirectory": outdir,

        # Parameter not in GUI
        "_subjectName": subject_id,

    }

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir


def export_bundles_to_trk(
        labeling_dir,
        outdir=None):
    """ After Connectomist has done the fibers labeling, convert the result
    to Trackvis format.

    Parameters
    ----------
    labeling_dir: str
        path to the Connectomist 'Labeling' directory.
    outdir: str (optional)
        path to directory where to output.
        By default <outdir> is <labeling_dir>.

    Returns
    -------
    bundles: list of str
        path to the labeled fiber bundles Trackvis files.
    """
    # Step 1 - Set outdir path and check directory existence
    if outdir is None:
        outdir = labeling_dir
    else:
        if not os.path.isdir(outdir):  # If outdir does not exist, create it
            os.mkdir(outdir)

    # Step 2 - Convert to Trackvis
    bundles = []
    bundles = glob.glob(os.path.join(labeling_dir, "bundleMapsReferential",
                                     "*", "*.bundlesdata"))
    bundles = [item.replace(".bundlesdata", ".bundles") for item in bundles]
    for index, path in enumerate(bundles):
        basename = os.path.basename(path)
        basename = basename.split(".")[0]
        dirname = os.path.dirname(path)
        region = dirname.split(os.path.sep)[-1]
        outbasedir = os.path.join(outdir, "bundles", region)
        if not os.path.isdir(outbasedir):
            os.makedirs(outbasedir)
        trk = os.path.join(outbasedir, basename + ".trk")
        bundles[index] = ptk_bundle_to_trk(path, trk)

    return bundles
