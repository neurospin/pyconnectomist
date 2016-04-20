##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

# System import
import os
import glob

# Wrappers of Connectomist's tabs
from pyconnectomist.exceptions import ConnectomistError
from .dwi_local_modeling import dwi_local_modeling
from .mask import tractography_mask
from .tractography import tractography


def complete_tractography(
        outdir,
        dwi_preproc_dir,
        morphologist_dir,
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
        add_cerebelum=False,
        add_commissures=True,
        tracking_type="streamline_regularize_deterministic",
        bundlemap="vtkbundlemap",
        min_fiber_length=5.,
        max_fiber_length=300.,
        aperture_angle=30.,
        forward_step=0.2,
        voxel_sampler_point_count=1,
        gibbs_temperature=1.,
        storing_increment=10,
        output_orientation_count=500,
        nb_tries=10,
        path_connectomist=(
            "/i2bm/local/Ubuntu-14.04-x86_64/ptk/bin/connectomist")):
    """
    Function that runs all preprocessing tabs from Connectomist.

    Steps:

    1- Create the tractography output directory if not existing.
    2- Detect the Connectomist registration folder.
    3- Compute the diffusion model.
    4- Create the tractography mask.
    5- The tractography algorithm.

    Parameters
    ----------
    outdir: str (mandatory)
        path to folder where all the tractography will be done.
    dwi_preproc_dir: str (mandatory)
        path to folder where all the preprocessings have been done.
    morphologist_dir: str
        path to Morphologist directory.
    subject_id: str (mandatory)
        subject identifier.
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
    add_cerebelum: bool (optional, default False)
        if True add the cerebelum to the tractography mask.
    add_commissures: bool (optional, default False)
        if True add the commissures to the tractography mask.
    tracking_type: str (optional, default
            'streamline_regularize_deterministic')
        the tractography algorithm: 'streamline_regularize_deterministic',
        'streamline_deterministic' or 'streamline_probabilistic'
    bundlemap: str (optional, default 'vtkbundlemap')
        the bundle format.
    min_fiber_length: float (optional, default 5)
        the length threshold in mm from which fiber are considered.
    max_fiber_length: float (optional, default 300)
        the length threshold in mm under which fiber are considered.
    aperture_angle: float (optional, default 30)
        the search angle in degrees: for the probabilistic tractography,
        the default connectomist value is 90 degs.
    forward_step: float (optional, default 0.2)
        the propagation step in mm.
    voxel_sampler_point_count: int (optional, default 1)
        the number of seeds per voxel
    gibbs_temperature: float (optional, default 1)
        the temperature if the Gibb's sampler: only for the probabilistic
        tractography.
    storing_increment: int (optional, default 10)
        undersample the fiber with the specified rate.
    output_orientation_count: int (optional, default 500)
        the number of the point in the sphere, default is equivalent to a
        2 degs resolution.
    nb_tries: int (optional, default 10)
        nb of times to try an algorithm if it fails.
        It often crashes when running in parallel. The reason
        why it crashes is unknown.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------

    """
    # Step 1 - Create the tractography output directory if not existing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # Step 2 - Detect the Connectomist registration folder
    registered_dwi_dir = glob.glob(os.path.join(dwi_preproc_dir,
                                                "*Anatomy_Talairach"))
    if (len(registered_dwi_dir) != 1 or not os.path.isdir(
            registered_dwi_dir[0])):
        raise ConnectomistError(
            "In '{0}' can't detect Connectomist registration "
            "folder.".format(registered_dwi_dir))
    registered_dwi_dir = registered_dwi_dir[0]

    # Step 3 - Compute the diffusion model
    model_dir = os.path.join(outdir, "07-Local_modeling_{0}".format(model))
    dwi_local_modeling(
        model_dir,
        registered_dwi_dir,
        subject_id,
        model=model,
        order=order,
        aqbi_laplacebeltrami_sharpefactor=aqbi_laplacebeltrami_sharpefactor,
        regularization_lccurvefactor=regularization_lccurvefactor,
        dti_estimator=dti_estimator,
        constrained_sd=constrained_sd,
        sd_kernel_type=sd_kernel_type,
        sd_kernel_lower_fa=sd_kernel_lower_fa,
        sd_kernel_upper_fa=sd_kernel_upper_fa,
        sd_kernel_voxel_count=sd_kernel_voxel_count,
        nb_tries=nb_tries,
        path_connectomist=path_connectomist)

    # Step 4 - Create the tractography mask
    mask_dir = os.path.join(outdir, "08-Tractography_mask")
    tractography_mask(
        mask_dir,
        subject_id,
        morphologist_dir=morphologist_dir,
        add_cerebelum=add_cerebelum,
        add_commissures=add_commissures,
        nb_tries=nb_tries,
        path_connectomist=path_connectomist)

    # Step 5 - The tractography algorithm
    tractography_dir = os.path.join(outdir, "09-Tractography_{0}".format(
        tracking_type))
    tractography(
        tractography_dir,
        subject_id,
        mask_dir,
        model,
        model_dir,
        registered_dwi_dir,
        tracking_type=tracking_type,
        bundlemap=bundlemap,
        min_fiber_length=min_fiber_length,
        max_fiber_length=max_fiber_length,
        aperture_angle=aperture_angle,
        forward_step=forward_step,
        voxel_sampler_point_count=voxel_sampler_point_count,
        gibbs_temperature=gibbs_temperature,
        storing_increment=storing_increment,
        output_orientation_count=output_orientation_count,
        nb_tries=nb_tries,
        path_connectomist=path_connectomist)
