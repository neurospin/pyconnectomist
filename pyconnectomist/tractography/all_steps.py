##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Function that runs all tractography tabs from Connectomist.
"""

# System import
import os
import glob

# Wrappers of Connectomist's tabs
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from pyconnectomist.exceptions import ConnectomistError
from .model import dwi_local_modeling
from .model import export_scalars_to_nifti
from .mask import tractography_mask
from .mask import export_mask_to_nifti
from .tractography import tractography
from pyconnectomist.clustering.labeling import export_bundles_to_trk
from pyconnectomist.clustering.labeling import fast_bundle_labeling
from pyconnectomist.preproc.all_steps import STEPS as PREPROC_STEPS


# Define steps
STEPS = [
    "07-Local_modeling_{0}",
    "08-Tractography_mask",
    "09-Tractography_{0}",
    "10-Fast_bundle_labeling"
]


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
        bundlemap="aimsbundlemap",
        min_fiber_length=5.,
        max_fiber_length=300.,
        aperture_angle=30.,
        forward_step=0.2,
        voxel_sampler_point_count=1,
        gibbs_temperature=1.,
        storing_increment=10,
        output_orientation_count=500,
        rgbscale=1.0,
        model_only=False,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Function that runs all preprocessing tabs from Connectomist.

    Steps:

    1- Create the tractography output directory if not existing.

    2- Detect the Connectomist registration folder.

    3- Detect the Connectomist eddy motion correction folder.

    4- Detect the Connectomist rough mask folder.

    5- Compute the diffusion model.

    6- Create the tractography mask.

    7- The tractography algorithm.

    8- Fast bundle labeling.

    9 - Export diffusion scalars.

    10 - Export tractography mask.

    11 - Export bundels.

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
        the secend order tensor fitting method ('linear' or 'positive').
        The second method generates positive definite tensors.
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
    tracking_type: str (optional)
        the tractography algorithm: 'streamline_regularize_deterministic',
        'streamline_deterministic' or 'streamline_probabilistic'
    bundlemap: str (optional, default 'aimsbundlemap')
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
    rgbscale: float (optional, default 1)
        a multiplicative factor used to vizualize the anisotropy map over
        the t1 map.
    model_only: bool (optional, default False)
        if True estimate only the diffusion model, skip steps 6, 7, 8, 10 ,11.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    gfa, md: str
        some scalars computed from the diffusion local model, here the
        generalized fractional anisotropy and the mean diffusivity.
    mask: str
        the tractography mask.
    bundles: list of str
        the labeled fiber bundles.
    """
    # Step 1 - Create the tractography output directory if not existing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # Step 2 - Detect the Connectomist registration folder
    registered_dwi_dir = os.path.join(dwi_preproc_dir, PREPROC_STEPS[5])
    if not os.path.isdir(registered_dwi_dir):
        raise ConnectomistError(
            "In '{0}' can't detect Connectomist registration "
            "folder '{1}'.".format(dwi_preproc_dir, PREPROC_STEPS[5]))

    # Step 3 - Detect the Connectomist eddy motion correction folder
    eddy_motion_dir = os.path.join(dwi_preproc_dir, PREPROC_STEPS[4])
    if not os.path.isdir(eddy_motion_dir):
        raise ConnectomistError(
            "In '{0}' can't detect Connectomist eddy motion correction "
            "folder '{1}'.".format(dwi_preproc_dir, PREPROC_STEPS[4]))

    # Step 4 - Detect the Connectomist rough mask folder
    rough_mask_dir = os.path.join(dwi_preproc_dir, PREPROC_STEPS[1])
    if not os.path.isdir(rough_mask_dir):
        raise ConnectomistError(
            "In '{0}' can't detect Connectomist rough mask "
            "folder '{1}'.".format(dwi_preproc_dir, PREPROC_STEPS[1]))

    # Step 5 - Compute the diffusion model
    model_dir = os.path.join(outdir, STEPS[0].format(model))
    dwi_local_modeling(
        model_dir,
        registered_dwi_dir,
        eddy_motion_dir,
        rough_mask_dir,
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
        rgbscale=rgbscale,
        path_connectomist=path_connectomist)

    # Step 6 - Create the tractography mask
    if not model_only:
        mask_dir = os.path.join(outdir, STEPS[1])
        tractography_mask(
            mask_dir,
            subject_id,
            morphologist_dir=morphologist_dir,
            add_cerebelum=add_cerebelum,
            add_commissures=add_commissures,
            path_connectomist=path_connectomist)

    # Step 7 - The tractography algorithm
    if not model_only:
        tractography_dir = os.path.join(outdir, STEPS[2].format(tracking_type))
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
            path_connectomist=path_connectomist)

    # Step 8 - Fast bundle labeling
    if not model_only:
        labeling_dir = os.path.join(outdir, STEPS[3])
        paths_bundle_map = glob.glob(
            os.path.join(tractography_dir, "*.bundlesdata"))
        paths_bundle_map = [item.replace(".bundlesdata", ".bundles")
                            for item in paths_bundle_map]
        fast_bundle_labeling(
            labeling_dir,
            registered_dwi_dir,
            morphologist_dir,
            subject_id,
            paths_bundle_map,
            atlas="Guevara long bundle",
            custom_atlas_dir=None,
            bundle_names=None,
            nb_fibers_to_process_at_once=50000,
            resample_fibers=True,
            remove_temporary_files=True,
            path_connectomist=path_connectomist)

    # Step 9 - Export diffusion scalars
    gfa, md = export_scalars_to_nifti(model_dir, model, outdir,
                                      gfafilename="gfa", mdfilename="md")

    # Step 10 - Export tractography mask
    mask = None
    if not model_only:
        mask = export_mask_to_nifti(mask_dir, outdir, "mask")

    # Step 11 - Export bundels
    bundles = None
    if not model_only:
        bundles = export_bundles_to_trk(labeling_dir, outdir)

    return gfa, md, mask, bundles
