#########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Outliers' tab.
"""

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.wrappers import ConnectomistWrapper


def outlying_slice_detection(
        outdir,
        raw_dwi_dir,
        rough_mask_dir,
        subject_id,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Outliers' tab.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI folder.
    rough_mask_dir: str
        path to Connectomist Rough Mask folder.
    subject_id: str
        the subject code in study.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Dict with all parameters for connectomist
    algorithm = "DWI-Outlier-Detection"
    parameters_dict = {
        "rawDwiDirectory": raw_dwi_dir,
        "roughMaskDirectory": rough_mask_dir,
        "outputWorkDirectory": outdir,
        "discardedOrientationList": "",
        "outlierFactor": 3.0,
        "_subjectName": subject_id
    }

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir
