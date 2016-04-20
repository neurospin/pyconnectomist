##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Rough mask' tab.
"""

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.wrappers import ConnectomistWrapper


def rough_mask_extraction(
        outdir,
        raw_dwi_dir,
        subject_id,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Rough mask' tab.

    Parameters
    ----------
    outdir:  str
        path to Connectomist output work directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI folder.
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
    algorithm = "DWI-Rough-Mask-Extraction"
    parameters_dict = {
        # ---------------------------------------------------------------------
        # Used parameters
        "outputWorkDirectory":      outdir,
        "rawDwiDirectory":     raw_dwi_dir,
        # ---------------------------------------------------------------------
        # Parameters not used/handled by the code
        "_subjectName": subject_id,
        "anatomy": "",
        "dwToT1RegistrationParameter": {
            "applySmoothing":                                1,
            "floatingLowerThreshold":                      0.0,
            "initialParametersRotationX":                    0,
            "initialParametersRotationY":                    0,
            "initialParametersRotationZ":                    0,
            "initialParametersScalingX":                   1.0,
            "initialParametersScalingY":                   1.0,
            "initialParametersScalingZ":                   1.0,
            "initialParametersShearingXY":                 0.0,
            "initialParametersShearingXZ":                 0.0,
            "initialParametersShearingYZ":                 0.0,
            "initialParametersTranslationX":                 0,
            "initialParametersTranslationY":                 0,
            "initialParametersTranslationZ":                 0,
            "initializeCoefficientsUsingCenterOfGravity": True,
            "levelCount":                                   32,
            "maximumIterationCount":                      1000,
            "maximumTestGradient":                      1000.0,
            "maximumTolerance":                           0.01,
            "optimizerName":                                 0,
            "optimizerParametersRotationX":                  5,
            "optimizerParametersRotationY":                  5,
            "optimizerParametersRotationZ":                  5,
            "optimizerParametersScalingX":                0.05,
            "optimizerParametersScalingY":                0.05,
            "optimizerParametersScalingZ":                0.05,
            "optimizerParametersShearingXY":              0.05,
            "optimizerParametersShearingXZ":              0.05,
            "optimizerParametersShearingYZ":              0.05,
            "optimizerParametersTranslationX":              30,
            "optimizerParametersTranslationY":              30,
            "optimizerParametersTranslationZ":              30,
            "referenceLowerThreshold":                     0.0,
            "resamplingOrder":                               1,
            "similarityMeasureName":                         1,
            "stepSize":                                    0.1,
            "stoppingCriterionError":                     0.01,
            "subSamplingMaximumSizes":                    "64",
            "transform3DType":                               0
        },
        "maskClosingRadius":        0.0,
        "maskDilationRadius":       4.0,
        "morphologistBrainMask":     "",
        "noiseThresholdPercentage": 2.0,
        "strategyRoughMaskFromT1":    0,
        "strategyRoughMaskFromT2":    1
    }

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir
