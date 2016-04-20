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

# Clindmri import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError
from pyconnectomist.wrappers import ConnectomistWrapper


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


def fast_bundle_labeling(
        outdir,
        paths_bundle_map,
        path_bundle_map_to_t1_trf,
        path_t1_to_tal_trf,
        atlas="Guevara long bundle",
        custom_atlas_dir=None,
        bundle_names=None,
        nb_fibers_to_process_at_once=50000,
        resample_fibers=True,
        subject_id=None,
        remove_temporary_files=True,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Fast Bundle Labeling' tab.

    Parameters
    ----------
    outdir: str
        Path to Connectomist output work directory.
    paths_bundle_map: list of str
        Paths to the bundle maps.
    path_bundle_map_to_t1_trf: str
        Path to the transform: bundle map(s) -> T1.
    path_t1_to_tal_trf: str
        Path to the transform: T1 -> Talairach.
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
    subject_id: str, optional
        Subject identifier.
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
        bundle_names = []

    # Check input parameter files existence
    required_files = paths_bundle_map + [path_bundle_map_to_t1_trf,
                                         path_t1_to_tal_trf]
    for path in required_files:
        if not os.path.isfile(path):
            raise ConnectomistBadFileError(path)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Fast-Bundle-Labelling"
    parameters_dict = {
        # Options are ordered like in the GUI

        # 'Input data' panel
        "inputBundleMapFileNames": " ".join(paths_bundle_map),
        "fileNameBundleMapToTalairachTransformation":
            path_bundle_map_to_t1_trf,
        "fileNameT1ToTalairachTransformation": path_t1_to_tal_trf,
        "atlasName": INDEX_OF_ATLAS[atlas],
        "customAtlasDirectory": custom_atlas_dir if custom_atlas_dir else "",

        # 'Bundle Selection' panel
        "bundleNameSelection": " ".join(bundle_names),

        # 'Labelling option' panel
        "fiberCount": nb_fibers_to_process_at_once,
        "doResampling": 2 if resample_fibers else 0,

        # 'Output option' panel
        "removeTemporaryFiles": remove_temporary_files,

        # 'Work directory' panel
        "outputWorkDirectory": outdir,

        # Parameter not in GUI
        "_subjectName": subject_id if subject_id is not None else "",

    }

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir
