##########################################################################
# NSAp - Copyright (C) CEA, 2015 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Susceptibility' tab.
"""

# System import
import os

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.manufacturers import MANUFACTURERS
from pyconnectomist.exceptions import ConnectomistMissingParametersError
from pyconnectomist.exceptions import ConnectomistBadManufacturerNameError
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.wrappers import ConnectomistWrapper
from pyconnectomist.utils.filetools import exec_file


def susceptibility_correction(
        outdir,
        raw_dwi_dir,
        rough_mask_dir,
        outliers_dir,
        subject_id,
        delta_TE,
        partial_fourier_factor,
        parallel_acceleration_factor,
        negative_sign=False,
        echo_spacing=None,
        EPI_factor=None,
        b0_field=3.0,
        water_fat_shift=4.68,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Wrapper to Connectomist's 'Susceptibility' tab.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    raw_dwi_dir: str
        path to Connectomist Raw DWI folder.
    rough_mask_dir: str
        path to Connectomist Rough Mask folder.
    outliers_dir: str
        path to Connectomist Outliers folder.
    subject_id: str
        the subject code in study.
    delta_TE: float
        difference in seconds between the 2 echoes
        in B0 magnitude map acquisition.
    partial_fourier_factor: float (]0;1])
        percentage of k-space plane acquired.
    parallel_acceleration_factor: int
        nb of parallel acquisition in k-space plane.
    negative_sign: bool
        if True invert direction of unwarping in
        susceptibility-distortion correction.
    echo_spacing: float
        not for Philips, acquisition time in ms between
        2 centers of 2 consecutively acquired lines in k-space.
    EPI_factor: int
        nb of echoes after one excitation (90 degrees),
        i.e. echo train length.
    b0_field: float
        Philips only, B0 field intensity, by default 3.0.
    water_fat_shift: float
        Philips only, default 4.68 pixels.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get the b0 amplitude and phase image
    b0_magnitude = os.path.join(raw_dwi_dir, "b0_magnitude.ima")
    b0_phase = os.path.join(raw_dwi_dir, "b0_phase.ima")

    # Get the manufacturer from Connectomist's parameter file
    try:
        parameter_file = os.path.join(raw_dwi_dir, "acquisition_parameters.py")
        exec_dict = exec_file(parameter_file)
        manufacturer = exec_dict["acquisitionParameters"][
            "manufacturer"].split(" ")[0]
    except:
        raise ConnectomistBadFileError(parameter_file)
    if manufacturer not in MANUFACTURERS:
        raise ConnectomistBadManufacturerNameError(manufacturer)

    # Dict with all parameters for connectomist
    algorithm = "DWI-Susceptibility-Artifact-Correction"
    parameters_dict = {
        # ---------------------------------------------------------------------
        # Paths parameters
        "rawDwiDirectory":                raw_dwi_dir,
        "roughMaskDirectory":          rough_mask_dir,
        "outlierFilteredDwiDirectory":   outliers_dir,
        "outputWorkDirectory":                 outdir,

        # ---------------------------------------------------------------------
        # Fieldmap correction only
        "correctionStrategy":            0,
        "importDwToB0Transformation":    0,
        "generateDwToB0Transformation":  1,
        "fileNameDwToB0Transformation": "",

        # ---------------------------------------------------------------------
        # Bruker parameters
        "brukerDeltaTE":                      2.46,
        "brukerEchoSpacing":                  0.75,
        "brukerPhaseNegativeSign":               0,
        "brukerPartialFourierFactor":          1.0,
        "brukerParallelAccelerationFactor":      1,
        "brukerFileNameFirstEchoB0Magnitude":   "",
        "brukerFileNameB0PhaseDifference":      "",

        # ---------------------------------------------------------------------
        # GE parameters
        "geDeltaTE":                                         2.46,
        "geEchoSpacing":                                     0.75,
        "gePhaseNegativeSign":                                  0,
        "gePartialFourierFactor":                             1.0,
        "geParallelAccelerationFactor":                         1,
        "geFileNameDoubleEchoB0MagnitudePhaseRealImaginary":   "",

        # ---------------------------------------------------------------------
        # Philips parameters
        "philipsDeltaTE":                      2.46,
        "philipsEchoSpacing":                  0.75,  # Not requested in GUI;
        "philipsPhaseNegativeSign":               0,
        "philipsPartialFourierFactor":          1.0,
        "philipsParallelAccelerationFactor":      1,
        "philipsFileNameFirstEchoB0Magnitude":   "",
        "philipsFileNameB0PhaseDifference":      "",
        "philipsEPIFactor":                     128,
        "philipsStaticB0Field":                 3.0,
        "philipsWaterFatShiftPerPixel":         0.0,

        # ---------------------------------------------------------------------
        # Siemens parameters
        "siemensDeltaTE":                       2.46,
        "siemensEchoSpacing":                   0.75,
        "siemensPhaseNegativeSign":                2,
        "siemensPartialFourierFactor":           1.0,
        "siemensParallelAccelerationFactor":       1,
        "siemensFileNameDoubleEchoB0Magnitude":   "",
        "siemensFileNameB0PhaseDifference":       "",

        # ---------------------------------------------------------------------
        # Parameters not used/handled by the code
        "_subjectName": subject_id,
        "DwToB0RegistrationParameter": {
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
            "optimizerParametersRotationX":                 10,
            "optimizerParametersRotationY":                 10,
            "optimizerParametersRotationZ":                 10,
            "optimizerParametersScalingX":                0.05,
            "optimizerParametersScalingY":                0.05,
            "optimizerParametersScalingZ":                0.05,
            "optimizerParametersShearingXY":              0.05,
            "optimizerParametersShearingXZ":              0.05,
            "optimizerParametersShearingYZ":              0.05,
            "optimizerParametersTranslationX":              10,
            "optimizerParametersTranslationY":              10,
            "optimizerParametersTranslationZ":              10,
            "referenceLowerThreshold":                     0.0,
            "resamplingOrder":                               1,
            "similarityMeasureName":                         1,
            "stepSize":                                    0.1,
            "stoppingCriterionError":                     0.01,
            "subSamplingMaximumSizes":                    "56",
            "transform3DType":                               0
        },
    }

    # Maps required parameters in Connectomist, for each manufacturer, to the
    # arguments of the function.
    args_map = {
        "Bruker": {
            "brukerDeltaTE":                      delta_TE,
            "brukerPartialFourierFactor":         partial_fourier_factor,
            "brukerParallelAccelerationFactor":   parallel_acceleration_factor,
            "brukerFileNameFirstEchoB0Magnitude": b0_magnitude,
            "brukerFileNameB0PhaseDifference":    b0_phase,
            "brukerPhaseNegativeSign":            2 if negative_sign else 0,
            "brukerEchoSpacing":                  echo_spacing
        },
        "GE": {
            "geDeltaTE":                          delta_TE,
            "gePartialFourierFactor":             partial_fourier_factor,
            "geParallelAccelerationFactor":       parallel_acceleration_factor,
            "geFileNameDoubleEchoB0MagnitudePhaseRealImaginary": b0_magnitude,
            "gePhaseNegativeSign":                2 if negative_sign else 0,
            "geEchoSpacing":                      echo_spacing

        },
        "Philips": {
            "philipsDeltaTE":                     delta_TE,
            "philipsPartialFourierFactor":        partial_fourier_factor,
            "philipsParallelAccelerationFactor":  parallel_acceleration_factor,
            "philipsFileNameFirstEchoB0Magnitude": b0_magnitude,
            "philipsFileNameB0PhaseDifference":   b0_phase,
            "philipsPhaseNegativeSign":           2 if negative_sign else 0,
            "philipsEPIFactor":                   EPI_factor,
            "philipsStaticB0Field":               b0_field,
            "philipsWaterFatShiftPerPixel":       water_fat_shift
        },
        "Siemens": {
            "siemensDeltaTE":                      delta_TE,
            "siemensPartialFourierFactor":         partial_fourier_factor,
            "siemensParallelAccelerationFactor":  parallel_acceleration_factor,
            "siemensFileNameDoubleEchoB0Magnitude": b0_magnitude,
            "siemensFileNameB0PhaseDifference":    b0_phase,
            "siemensPhaseNegativeSign":            2 if negative_sign else 0,
            "siemensEchoSpacing":                  echo_spacing
        }
    }

    # Check that all needed parameters have been passed: a missing parameter
    # is a parameter with a None value
    required_parameters = set(args_map[manufacturer])
    missing_parameters = [p for p in required_parameters
                          if args_map[manufacturer][p] is None]
    if len(missing_parameters) > 0:
        raise ConnectomistMissingParametersError(algorithm, missing_parameters)

    # Set given parameters
    for p in required_parameters:
        parameters_dict[p] = args_map[manufacturer][p]

    # Call with Connectomist
    process = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    process(algorithm, parameter_file, outdir)

    return outdir
