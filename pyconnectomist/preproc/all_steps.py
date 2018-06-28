##########################################################################
# NSAp - Copyright (C) CEA, 2013 - 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html for details.
##########################################################################

"""
Function that runs all preprocessing tabs from Connectomist.
"""

# System import
import os
import shutil

# Wrappers of Connectomist's tabs
from pyconnectomist import DEFAULT_CONNECTOMIST_PATH
from .qspace import data_import_and_qspace_sampling
from .mask import rough_mask_extraction
from .outliers import outlying_slice_detection
from .susceptibility import susceptibility_correction
from .eddy import eddy_and_motion_correction
from .eddy import export_eddy_motion_results_to_nifti
from .registration import dwi_to_anatomy
from .qc import qc_reporting


# Define steps
STEPS = [
    "01-Import_and_qspace_model",
    "02-Anatomy_Talairach",
    "03-Rough_mask",
    "04-Outliers",
    "05-Suceptibility",
    "06-Eddy_current_and_motion",
    "07-QC_reporting"
]


def complete_preprocessing(
        outdir,
        subject_id,
        project_name,
        timestep,
        dwis,
        bvals,
        bvecs,
        manufacturer,
        delta_TE,
        partial_fourier_factor,
        parallel_acceleration_factor,
        b0_magnitude,
        b0_phase=None,
        phase_axis="y",
        slice_axis="z",
        flipX=False,
        flipY=False,
        flipZ=False,
        invertX=True,
        invertY=False,
        invertZ=False,
        negative_sign=False,
        echo_spacing=None,
        EPI_factor=None,
        b0_field=3.0,
        water_fat_shift=4.68,
        t1_foot_zcropping=0,
        level_count=32,
        lower_theshold=0.0,
        apply_smoothing=True,
        init_center_gravity=False,
        similarity_measure="mi",
        transform_type=0,
        delete_steps=False,
        morphologist_dir=None,
        already_corrected=False,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Function that runs all preprocessing tabs from Connectomist.

    Steps:

    1- Create the preprocessing output directory if not existing.

    2- Import files to Connectomist and choose q-space model.

    3- Registration t1 - dwi.

    4- Create a brain mask.

    5- Detect and correct outlying diffusion slices.

    6- Susceptibility correction.

    7- Eddy current and motion correction.

    8- QC reporting.

    9- Export result as a Nifti with a .bval and a .bvec.

    10- Export outliers.

    11- Delete intermediate files and directories if requested.

    Parameters
    ----------
    outdir: str (mandatory)
        path to folder where all the preprocessing will be done.
    subject_id: str (mandatory)
        subject identifier.
    project_name: str
        the name of the project.
    timestep: str
        the time step assocaited to this diffusion dataset.
    dwis: list of str (mandatory)
        path to input Nifti DW datasets.
    bvals: list of str (mandatory)
        path to Nifti's associated .bval files.
    bvecs: list of str (mandatory)
        path to Nifti's associated .bval files.
    manufacturer: str (mandatory)
        manufacturer name (e.g. "Siemens", "GE"...).
    delta_TE: float (mandatory)
        difference in msec between the 2 echoes in B0 magnitude map
        acquisition.
    partial_fourier_factor: float (mandatory)
        percentage of k-space plane acquired (]0;1]).
    parallel_acceleration_factor: int (mandatory)
        nb of parallel acquisition in k-space plane.
    b0_magnitude: str (mandatory)
        path to B0 magnitude map, also contains phase for GE.
    b0_phase: str (optional, default None)
        not for GE, path to B0 phase map.
    phase_axis: str (optional, default 'y')
        the acquistion phase axis 'x', 'y' or 'z'.
    slice_axis: str (optional, default 'z')
        the acquistion slice axis 'x', 'y' or 'z'.
    flipX, flipY, flipZ: bool (optional, default False)
        if True invert the x, y or z-axis of data.
    invertX: bool (optional, default True)
        if True invert x-axis in diffusion model.
    invertY: bool (optional, default False)
        same as invertX but for y-axis.
    invertZ: bool (optional, default False)
        same as invertX but for z-axis.
    negative_sign: bool (optional, default False)
        if True invert direction of unwarping in usceptibility-distortion
        correction.
    echo_spacing: float (optional, default None)
        not for Philips, acquisition time in ms between 2 centers of 2
        consecutively acquired lines in k-space.
    EPI_factor: int (optional, default None)
        nb of echoes after one RF pulse, i.e. echo train length.
    b0_field: float (optional, default 3.0)
        Philips only, B0 field intensity, by default 3.0.
    water_fat_shift: float (optional, default 4.68)
        Philips only, default 4.68 pixels.
    t1_foot_zcropping: int (optional, default 0)
        crop the t1 image in the z direction in order to remove the neck.
    level_count: int (optional, default 32)
        the number of bins in the histogram.
    lower_theshold: float (optional, default 0)
        remove noise in the image by applying this lower theshold.
    apply_smoothing: bool (optional, default True)
        smooth the image before performing the histogram analysis.
    init_center_gravity: bool (optional, default False)
        initialize coefficients using the center of gravity.
    similarity_measure: str (option, default 'mi')
        the eddy + motion correction similarity measure.
    transform_type: int (optional, default 0)
        type of DWI to T1 registration(rigid=0, affine_wo_shearing=1,
        affine=2).
    delete_steps: bool (optional, default False)
        if True remove all intermediate files and directories at the end of
        preprocessing, to keep only 4 files: preprocessed Nifti + bval + bvec
        + outliers.py
    morphologist_dir: str (optional, default None)
        the path to the morphologist processings.
    already_corrected: bool (optional, default False)
        if True, only the first three step are computed in order to facilitate
        the modeling, tractography, bundeling steps.
    path_connectomist: str (optional)
        path to the Connectomist executable.

    Returns
    -------
    preproc_dwi, preproc_bval, preproc_bvec: str
        paths to output diffusion Nifti files.
    preproc_outliers: str
        path to the outliers detection summary.
    """
    # Step 1 - Create the preprocessing output directory if not existing
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # Step 2 - Import files to Connectomist and choose q-space model
    raw_dwi_dir = os.path.join(outdir, STEPS[0])
    data_import_and_qspace_sampling(
        raw_dwi_dir,
        subject_id,
        dwis,
        bvals,
        bvecs,
        manufacturer,
        flipX,
        flipY,
        flipZ,
        invertX,
        invertY,
        invertZ,
        b0_magnitude,
        b0_phase,
        phase_axis,
        slice_axis,
        path_connectomist=path_connectomist)

    # Step 3 - Registration t1 - dwi
    registration_dir = os.path.join(outdir, STEPS[1])
    dwi_to_anatomy(
        registration_dir,
        raw_dwi_dir,
        morphologist_dir,
        subject_id,
        t1_foot_zcropping=t1_foot_zcropping,
        level_count=level_count,
        lower_theshold=lower_theshold,
        apply_smoothing=apply_smoothing,
        init_center_gravity=init_center_gravity,
        transform_type=transform_type,
        path_connectomist=path_connectomist)

    # Step 4 - Create a brain mask
    rough_mask_dir = os.path.join(outdir, STEPS[2])
    rough_mask_extraction(
        rough_mask_dir,
        raw_dwi_dir,
        registration_dir,
        morphologist_dir,
        subject_id,
        level_count=level_count,
        lower_theshold=lower_theshold,
        apply_smoothing=apply_smoothing,
        path_connectomist=path_connectomist)

    # Quit if requested: preproc already performed
    if already_corrected:
        return None, None, None, None

    # Step 5 - Detect and correct outlying diffusion slices
    outliers_dir = os.path.join(outdir, STEPS[3])
    outlying_slice_detection(
        outliers_dir,
        raw_dwi_dir,
        rough_mask_dir,
        subject_id,
        path_connectomist=path_connectomist)

    # Step 6 - Susceptibility correction
    if b0_magnitude is None and b0_phase is None:
        corrected_dir = outliers_dir
        susceptibility_dir = ""
    else:
        corrected_dir = os.path.join(outdir, STEPS[4])
        susceptibility_dir = corrected_dir
        susceptibility_correction(
            corrected_dir,
            raw_dwi_dir,
            rough_mask_dir,
            outliers_dir,
            subject_id,
            delta_TE,
            partial_fourier_factor,
            parallel_acceleration_factor,
            negative_sign,
            echo_spacing,
            EPI_factor,
            b0_field,
            water_fat_shift,
            path_connectomist=path_connectomist)

    # Step 7 - Eddy current and motion correction
    eddy_motion_dir = os.path.join(outdir, STEPS[5])
    eddy_and_motion_correction(
        eddy_motion_dir,
        raw_dwi_dir,
        rough_mask_dir,
        corrected_dir,
        subject_id,
        similarity_measure,
        path_connectomist=path_connectomist)

    # Step 8 - QC reporting
    qc_dir = os.path.join(outdir, STEPS[6])
    qc_reporting(
        qc_dir,
        raw_dwi_dir,
        registration_dir,
        rough_mask_dir,
        outliers_dir,
        susceptibility_dir,
        eddy_motion_dir,
        subject_id,
        project_name=project_name,
        timestep=timestep,
        path_connectomist=path_connectomist)

    # Step 9 - Export result as a Nifti with a .bval and a .bvec
    preproc_files = export_eddy_motion_results_to_nifti(
        eddy_motion_dir,
        outdir=outdir,
        filename="dwi")
    preproc_dwi, preproc_bval, preproc_bvec = preproc_files

    # Step 10 - Export outliers.py
    path_outliers_py = os.path.join(outliers_dir, "outliers.py")
    preproc_outliers = os.path.join(outdir, "outliers.py")
    shutil.copy(path_outliers_py, preproc_outliers)

    # Step 11 - Delete intermediate files and directories if requested
    if delete_steps:
        intermediate_dirs = [raw_dwi_dir, registration_dir, rough_mask_dir,
                             outliers_dir, susceptibility_dir, eddy_motion_dir,
                             qc_dir]
        for directory in intermediate_dirs:
            shutil.rmtree(directory)

    return preproc_dwi, preproc_bval, preproc_bvec, preproc_outliers
