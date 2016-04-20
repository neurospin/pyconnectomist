##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Anatomy & Talairach' tab.
"""

# System import
import os

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper


def dwi_to_anatomy(
        outdir,
        corrected_dwi_dir,
        rough_mask_dir,
        morphologist_dir,
        subject_id,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Anatomy & Talairach' tab.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    corrected_dwi_dir: str
        path to Connectomist Corrected DWI directory.
    rough_mask_dir: str
        path to Connectomist Rough Mask directory.
    morphologist_dir: str
        path to Morphologist directory.
    subject_id: str
        the subject code in study.
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
    t1file = os.path.join(
        morphologist_dir, subject_id, "t1mri", "default_acquisition",
        "{0}.nii.gz".format(subject_id))
    for fpath in (apcfile, t1file):
        if not os.path.isfile(fpath):
            raise ConnectomistBadFileError(fpath)

    # Dict with all parameters for connectomist
    algorithm = "DWI-To-Anatomy-Matching"
    parameters_dict = {
        "dwToT1RegistrationParameter": {
            "applySmoothing": 1,
            "floatingLowerThreshold": 0.0,
            "initialParametersRotationX": 0,
            "initialParametersRotationY": 0,
            "initialParametersRotationZ": 0,
            "initialParametersScalingX": 1.0,
            "initialParametersScalingY": 1.0,
            "initialParametersScalingZ": 1.0,
            "initialParametersShearingXY": 0.0,
            "initialParametersShearingXZ": 0.0,
            "initialParametersShearingYZ": 0.0,
            "initialParametersTranslationX": 0,
            "initialParametersTranslationY": 0,
            "initialParametersTranslationZ": 0,
            "initializeCoefficientsUsingCenterOfGravity": True,
            "levelCount": 32,
            "maximumIterationCount": 1000,
            "maximumTestGradient": 1000.0,
            "maximumTolerance": 0.01,
            "optimizerName": 0,
            "optimizerParametersRotationX": 5,
            "optimizerParametersRotationY": 5,
            "optimizerParametersRotationZ": 5,
            "optimizerParametersScalingX": 0.05,
            "optimizerParametersScalingY": 0.05,
            "optimizerParametersScalingZ": 0.05,
            "optimizerParametersShearingXY": 0.05,
            "optimizerParametersShearingXZ": 0.05,
            "optimizerParametersShearingYZ": 0.05,
            "optimizerParametersTranslationX": 30,
            "optimizerParametersTranslationY": 30,
            "optimizerParametersTranslationZ": 30,
            "referenceLowerThreshold": 0.0,
            "resamplingOrder": 1,
            "similarityMeasureName": 1,
            "stepSize": 0.1,
            "stoppingCriterionError": 0.01,
            "subSamplingMaximumSizes": "64",
            "transform3DType": 0},
        "_subjectName": subject_id,
        "anteriorPosteriorAdditionSliceCount": 0,
        "correctedDwiDirectory": corrected_dwi_dir,
        "fileNameACP": apcfile,
        "fileNameDwToT1Transformation": "",
        "fileNameT1": t1file,
        "generateDwToT1Transformation": 1,
        "headFootAdditionSliceCount": 0,
        "importDwToT1Transformation": 0,
        "leftRightAdditionSliceCount": 0,
        "outputWorkDirectory": outdir,
        "roughMaskDirectory": rough_mask_dir,
        "t1AnteriorYCropping": 0,
        "t1FootZCropping": 0,
        "t1HeadZCropping": 0,
        "t1LeftXCropping": 0,
        "t1PosteriorYCropping": 0,
        "t1RightXCropping": 0}

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir
