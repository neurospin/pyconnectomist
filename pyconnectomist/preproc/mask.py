##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Rough mask' tab.
"""

# System import
import os
import glob
import nibabel

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper


def rough_mask_extraction(
        outdir,
        raw_dwi_dir,
        registration_dir,
        morphologist_dir,
        subject_id,
        level_count=32,
        lower_theshold=0.0,
        apply_smoothing=True,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Rough mask' tab.

    Parameters
    ----------
    outdir:  str
        path to Connectomist output work directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI folder.
    registration_dir: str
        path to Connectomist registration folder.
    morphologist_dir: str
        path to Morphologist directory.
    subject_id: str
        the subject code in study.
    level_count: int (optional, default 32)
        the number of bins in the histogram.
    lower_theshold: float (optional, default 0)
        remove noise in the image by applying this lower theshold.
    apply_smoothing: bool (optional, default True)
        smooth the image before performing the histogram analysis.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get t1 and brain t1: check existance
    t1file = os.path.join(registration_dir, "t1.ima")
    t1brain = os.path.join(registration_dir, "Morphologist", "brain_t1.ima")
    for fpath in (t1file, t1brain):
        if not os.path.isfile(fpath):
            raise ConnectomistBadFileError(fpath)
    extensions = (".nii.gz", ".nii")
    subject_morphologist_dir = os.path.join(morphologist_dir, subject_id)
    t1pattern = os.path.join(subject_morphologist_dir, "t1mri", "*", "{0}{1}")
    t1patterns = [t1pattern.format(subject_id, ext) for ext in extensions]
    files = []
    for fpattern in t1patterns:
        files.extend(glob.glob(fpattern))
    print(files)
    if len(files) != 1 or not os.path.isfile(files[0]):
        raise ConnectomistBadFileError(str(t1patterns))
    niit1file = files[0]

    # Get the min image dimension
    im = nibabel.load(niit1file)
    mindim = min(im.shape)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Rough-Mask-Extraction"
    parameters_dict = {
        # ---------------------------------------------------------------------
        # Used parameters
        "outputWorkDirectory":      outdir,
        "rawDwiDirectory":          raw_dwi_dir,
        # ---------------------------------------------------------------------
        # Parameters not used/handled by the code
        "_subjectName": subject_id,
        "anatomy": t1file,
        "dwToT1RegistrationParameter": {
            "applySmoothing":                  apply_smoothing,
            "floatingLowerThreshold":           lower_theshold,
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
            "initializeCoefficientsUsingCenterOfGravity": False,
            "levelCount":                          level_count,
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
            "subSamplingMaximumSizes": "64 {0}".format(mindim),
            "transform3DType":                               0
        },
        "maskClosingRadius":          0.0,
        "maskDilationRadius":         4.0,
        "morphologistBrainMask":      t1brain,
        "noiseThresholdPercentage":   2.0,
        "strategyRoughMaskFromT1":    1,
        "strategyRoughMaskFromT2":    0
    }

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir
