##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Wrapper to Connectomist's 'Local modeling' tab.
"""

# System import
import os

# pyConnectomist import
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistBadFileError
from pyconnectomist.exceptions import ConnectomistError
from pyconnectomist.wrappers import ConnectomistWrapper
from pyconnectomist.utils.filetools import ptk_gis_to_nifti

# Map ODF model to index used by Connectomist
ODF_MODEL_MAP = {
    "dot": 0,
    "sd": 3,
    "sdt": 4,
    "aqbi": 5,
    "sa-aqbi": 6,
    "dti": 7
}

# Map estimator to index used by Connectomist
DTI_ESTIMATOR_MAP = {
    "linear": 0,
    "positive": 1
}

# Map SD kernel to index used by Connectomist
SD_KERNEL_MAP = {
    "symmetric_tensor": 0,
    "normal": 1
}


def dwi_local_modeling(
        outdir,
        registered_dwi_dir,
        eddy_motion_dir,
        rough_mask_dir,
        subject_id,
        model="aqbi",
        order=4,
        aqbi_laplacebeltrami_sharpefactor=0.0,
        regularization_lccurvefactor=0.006,
        dti_estimator="linear",
        constrained_sd=False,
        sd_kernel_type="symmetric_tensor",
        sd_kernel_lower_fa=0.65,
        sd_kernel_upper_fa=0.85,
        sd_kernel_voxel_count=300,
        rgbscale=1.0,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Diffusion model estimation.

    Parameters
    ----------
    outdir: str
        path to Connectomist output work directory.
    registered_dwi_dir: str
        path to Connectomist register DWI directory.
    eddy_motion_dir: str
        path to Connectomist eddy motion correction directory.
    rough_mask_dir: str
        path to Connectomist rough mask directory.
    subject_id: str
        the subject code in study.
    model: str (optional, default 'aqbi')
        the name of the model to be estimated: 'dot', 'sd', 'sdt', 'aqbi',
        'sa-qbi', 'dti'.
    order: int (optional, default 4)
        the order of the desired model which is directly related to the
        nulber of maxima that can be modeled considering the data SNR. For
        'dti' model this parameter has no effect since it is by definition a
        second order model
    aqbi_laplacebeltrami_sharpefactor: float (optional default 0.0)
        for 'aqbi' and 'sa-aqbi' sharpening factor.
    regularization_lccurvefactor: float (optional default 0.006)
        for 'sdt', 'aqbi' and 'sa-aqbi' regularization factor.
    dti_estimator: str (optional default 'linear')
        the secend order tensor fitting method: 'linear' or 'positive'.
        The seconf method generates positive definite tensors.
    constrained_sd: bool (optiona, default False)
        If True us constrained spherical deconvolution.
    sd_kernel_type: str (optional, default 'symmetric_tensor')
        the spherical deconvolution kernel type: 'symmetric_tensor' or
        'normal'.
    sd_kernel_lower_fa: float (optional, default 0.65)
        lower fractional anisotrpy threshold.
    sd_kernel_upper_fa: float (optional, default 0.85)
        upper fractional anisotrpy threshold.
    sd_kernel_voxel_count: int (optional, default 300)
        kernel size in voxels.
    rgbscale: float (optional, default 1)
        a multiplicative factor used to vizualize the anisotropy map over
        the t1 map.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    outdir: str
        path to Connectomist's output directory.
    """
    # Get Connectomist registration result files and check existance
    dwifile = os.path.join(eddy_motion_dir,
                           "dw_wo_eddy_current_and_motion.ima")
    maskfile = os.path.join(rough_mask_dir, "mask.ima")
    t1file = os.path.join(registered_dwi_dir, "t1.ima")
    t2file = os.path.join(eddy_motion_dir, "t2_wo_eddy_current_and_motion.ima")
    dwtot1file = os.path.join(registered_dwi_dir, "dw_to_t1.trm")
    for fpath in (dwifile, maskfile, t1file, t2file, dwtot1file):
        if not os.path.isfile(fpath):
            raise ConnectomistBadFileError(fpath)

    # Check input parameters
    if model not in ODF_MODEL_MAP:
        raise ConnectomistError(
            "'{0}' local DWI model not supported (must be in {1}).".format(
                model, ODF_MODEL_MAP.keys()))
    if dti_estimator not in DTI_ESTIMATOR_MAP:
        raise ConnectomistError(
            "'{0}' dti estimator not supported (must be in {1}).".format(
                dti_estimator,  DTI_ESTIMATOR_MAP.keys()))
    if not isinstance(constrained_sd, bool):
        raise ConnectomistError(
            "'constrained_sd' input parameter must be a boolean.")
    constrained_sd = int(constrained_sd)
    if sd_kernel_type not in SD_KERNEL_MAP:
        raise ConnectomistError(
            "'{0}' kernel not supported (must be in {1}).".format(
                sd_kernel_type, SD_KERNEL_MAP.keys()))

    # Dict with all parameters for connectomist
    algorithm = "DWI-Local-Modeling"
    parameters_dict = {
        "_subjectName": subject_id,
        "odfType": ODF_MODEL_MAP[model],
        "viewType": ODF_MODEL_MAP[model],
        "computeOdfVolume": 0,
        "rgbScale": rgbscale,
        "outputOrientationCount": 500,
        "outputWorkDirectory": outdir,
        "fileNameDw": dwifile,
        "fileNameMask": maskfile,
        "fileNameT1": t1file,
        "fileNameT2": t2file,
        "fileNameTransformationDwToT1": dwtot1file}
    parameters_dict.update({
        "aqbiLaplaceBeltramiSharpeningFactor": (
            aqbi_laplacebeltrami_sharpefactor),
        "aqbiMaximumSHOrder": order,
        "aqbiRegularizationLcurveFactor": regularization_lccurvefactor})
    parameters_dict.update({
        "dotEffectiveDiffusionTime": 25.0,
        "dotMaximumSHOrder": order,
        "dotOdfComputation": 2,
        "dotR0": 12.0})
    parameters_dict.update({
        "dsiFilteringDataBeforeFFT": 2,
        "dsiMarginalOdf": 2,
        "dsiMaximumR0": 15.0,
        "dsiMinimumR0": 1.0})
    parameters_dict.update({
        "dtiEstimatorType": DTI_ESTIMATOR_MAP[dti_estimator]})
    parameters_dict.update({
        "qbiEquatorPointCount": 50,
        "qbiPhiFunctionAngle": 0.0,
        "qbiPhiFunctionMaximumAngle": 0.0,
        "qbiPhiFunctionType": 0})
    parameters_dict.update({
        "saAqbiLaplaceBeltramiSharpeningFactor": (
            aqbi_laplacebeltrami_sharpefactor),
        "saAqbiMaximumSHOrder": order,
        "saAqbiRegularizationLcurveFactor": regularization_lccurvefactor})
    parameters_dict.update({
        "sdFilterCoefficients": (
            "1 1 1 0.5 0.1 0.02 0.002 0.0005 0.0001 0.00010.00001 0.00001 "
            "0.00001 0.00001 0.00001 0.00001 0.00001"),
        "sdKernelLowerFAThreshold": sd_kernel_lower_fa,
        "sdKernelType": SD_KERNEL_MAP[sd_kernel_type],
        "sdKernelUpperFAThreshold": sd_kernel_upper_fa,
        "sdKernelVoxelCount": sd_kernel_voxel_count,
        "sdMaximumSHOrder": order,
        "sdUseCSD": constrained_sd})
    parameters_dict.update({
        "sdtKernelLowerFAThreshold": sd_kernel_lower_fa,
        "sdtKernelType": SD_KERNEL_MAP[sd_kernel_type],
        "sdtKernelUpperFAThreshold": sd_kernel_upper_fa,
        "sdtKernelVoxelCount": sd_kernel_voxel_count,
        "sdtMaximumSHOrder": order,
        "sdtRegularizationLcurveFactor": regularization_lccurvefactor,
        "sdtUseCSD": constrained_sd})

    # Call with Connectomist
    connprocess = ConnectomistWrapper(path_connectomist)
    parameter_file = ConnectomistWrapper.create_parameter_file(
        algorithm, parameters_dict, outdir)
    connprocess(algorithm, parameter_file, outdir)

    return outdir


def export_scalars_to_nifti(
        model_dir,
        model,
        outdir=None,
        gfafilename="gfa",
        mdfilename="md"):
    """ After Connectomist has done the diffusion local modeling, convert the
    result scalar maps to Nifti.

    Parameters
    ----------
    model_dir: str
        path to the Connectomist 'Local modeling' directory.
    model: str (mandatory)
        the name of the model to be estimated: 'dot', 'sd', 'sdt', 'aqbi',
        'sa-qbi', 'dti'.
    outdir: str (optional)
        path to directory where to output:
        <outdir>/<gfafilename>.nii.gz
        <outdir>/<mdfilename>.nii.gz
        By default <outdir> is <model_dir>.
    gfafilename: str (optional)
        to change generalize anisotropy output filename, by default 'gfa'.
    mdfilename: str (optional)
        to change mean diffusivity output filename, by default 'md'.

    Returns
    -------
    gfa, md: str
        the generalize fractional anisotropy and the mean diffusivity
        nifti images.
    """
    # Step 1 - Set outdir path and check directory existence
    if outdir is None:
        outdir = model_dir
    else:
        if not os.path.isdir(outdir):  # If outdir does not exist, create it
            os.mkdir(outdir)

    # Step 2 - Convert to Nifti
    gfa = os.path.join(model_dir, "{0}_gfa.ima".format(model))
    md = os.path.join(model_dir, "{0}_mean_diffusivity.ima".format(model))
    for path in (gfa, md):
        if not os.path.isfile(path):
            raise ConnectomistBadFileError(path)
    gfa = ptk_gis_to_nifti(gfa, os.path.join(outdir, gfafilename + ".nii.gz"))
    md = ptk_gis_to_nifti(md, os.path.join(outdir, mdfilename + ".nii.gz"))

    return gfa, md
