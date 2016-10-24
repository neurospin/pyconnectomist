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
import glob

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper
from pyconnectomist.utils.filetools import ptk_nifti_to_gis


def dwi_to_anatomy(
        outdir,
        raw_dwi_dir,
        morphologist_dir,
        subject_id,
        t1_foot_zcropping=0,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Anatomy & Talairach' tab.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI directory.
    morphologist_dir: str
        path to Morphologist directory.
    subject_id: str
        the subject code in study.
    t1_foot_zcropping: int (optional, default 0)
        crop the t1 image in the z direction in order to remove the neck.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get morphologist result files and check existance
    subject_morphologist_dir = os.path.join(morphologist_dir, subject_id)
    apcpattern = os.path.join(subject_morphologist_dir,
                              "t1mri", "*", "{0}.APC".format(subject_id))
    t1pattern = os.path.join(subject_morphologist_dir,
                             "t1mri", "*","{0}.nii.gz".format(subject_id))
    files = []
    for fpattern in (apcpattern, t1pattern):
        fpath = glob.glob(fpattern)
        if len(fpath) != 1 or not os.path.isfile(fpath[0]):
            raise ConnectomistBadFileError(fpattern)
        files.append(fpath[0])
    acpcfile, t1file = files

    # Create the directory if not existing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # Convert the t1file in gis format
    t1gisfile = os.path.join(outdir, "t1_morphologist.ima")
    t1gisfile = ptk_nifti_to_gis(t1file, t1gisfile)

    # Dict with all parameters for connectomist
    algorithm = "DWI-To-Anatomy-Matching"
    parameters_dict = {
        "useCustomMorphologistDirectory": 2,
        "customMorphologistDirectory": subject_morphologist_dir,
        "computeNormalization": 2,
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
        "correctedDwiDirectory": raw_dwi_dir,
        "fileNameDwToT1Transformation": "",
        "fileNameT1": t1gisfile,
        "generateDwToT1Transformation": 1,
        "headFootAdditionSliceCount": 0,
        "importDwToT1Transformation": 0,
        "leftRightAdditionSliceCount": 0,
        "outputWorkDirectory": outdir,
        "roughMaskDirectory": "",
        "t1AnteriorYCropping": 0,
        "t1FootZCropping": t1_foot_zcropping,
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
