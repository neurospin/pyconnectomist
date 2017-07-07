##########################################################################
# NSAp - Copyright (C) CEA, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'QC Reporting' tab.
"""

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.wrappers import ConnectomistWrapper


def qc_reporting(outdir,
                 raw_dwi_dir,
                 registration_dir,
                 rough_mask_dir,
                 outliers_dir,
                 susceptibility_dir,
                 eddy_motion_dir,
                 subject_id,
                 project_name,
                 timestep,
                 path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'QC Reproting' tab.

    Parameters
    ----------
    outdir: str
        path to Connectomist's output directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI directory.
    registration_dir: str
        path to Connectomist Anatomy and Talairach directory.
    rough_mask_dir: str
        path to Connectomist Rough Mask directory.
    outliers_dir: str
        path to Connectomist Outliers directory.
    susceptibility_dir: str
        path to Connectomist Susceptibility directory.
    eddy_motion_dir: str
        path to Connectomist Eddy directory.
        subject_id: str
        the subject code in study.
    subject_id: str
        the subject code in study.
    project_name: str
        the name of the project.
    timestep: str
        the time step assocaited to this diffusion dataset.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Dict with all parameters for connectomist
    algorithm = "DWI-Quality-Check-Reporting"
    parameters_dict = {
        "_subjectName": subject_id,
        "directoryNameDataImportAndQSpaceSampling": raw_dwi_dir,
        "directoryNameEddyCurrentAndMotion": eddy_motion_dir,
        "directoryNameOutlierDetection": outliers_dir,
        "directoryNameRoughMask": rough_mask_dir,
        "directoryNameSusceptibilityArtifactCorrection": susceptibility_dir,
        "directoryNameToAnatomyMatching": registration_dir,
        "outputWorkDirectory": outdir,
        "projectName": project_name,
        "subjectName": subject_id,
        "timeStep": timestep
    }

    # Call with Connectomist
    process = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    process(algorithm, parameter_file, outdir)

    return outdir
