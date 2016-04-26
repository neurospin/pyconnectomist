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


# Define steps
STEPS = [
    "01-Import_and_qspace_model",
    "02-Rough_mask",
    "03-Outliers",
    "04-Suceptibility",
    "05-Eddy_current_and_motion",
    "06-Anatomy_Talairach"
]


def complete_preprocessing(
        outdir,
        subject_id,
        dwi,
        bval,
        bvec,
        manufacturer,
        delta_TE,
        partial_fourier_factor,
        parallel_acceleration_factor,
        b0_magnitude,
        b0_phase=None,
        invertX=True,
        invertY=False,
        invertZ=False,
        negative_sign=False,
        echo_spacing=None,
        EPI_factor=None,
        b0_field=3.0,
        water_fat_shift=4.68,
        delete_steps=False,
        morphologist_dir=None,
        path_connectomist=DEFAULT_CONNECTOMIST_PATH):
    """ Function that runs all preprocessing tabs from Connectomist.

    Steps:

    1- Create the preprocessing output directory if not existing.

    2- Import files to Connectomist and choose q-space model.

    3- Create a brain mask.

    4- Detect and correct outlying diffusion slices.

    5- Susceptibility correction.

    6- Eddy current and motion correction.

    7- Export result as a Nifti with a .bval and a .bvec.

    8- Export outliers.

    9- Registration t1 - dwi.

    10- Delete intermediate files and directories if requested.

    Parameters
    ----------
    outdir: str (mandatory)
        path to folder where all the preprocessing will be done.
    subject_id: str (mandatory)
        subject identifier.
    dwi: str (mandatory)
        path to input Nifti DW data.
    bval: str (mandatory)
        path to Nifti's associated .bval file.
    bvec: str (mandatory)
        path to Nifti's associated .bval file.
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
    delete_steps: bool (optional, default False)
        if True remove all intermediate files and directories at the end of
        preprocessing, to keep only 4 files: preprocessed Nifti + bval + bvec
        + outliers.py
    morphologist_dir: str (optional, default None)
        the path to the morphologist processings.
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
        dwi,
        bval,
        bvec,
        manufacturer,
        invertX,
        invertY,
        invertZ,
        b0_magnitude,
        b0_phase,
        path_connectomist=path_connectomist)

    # Step 3 - Create a brain mask
    rough_mask_dir = os.path.join(outdir, STEPS[1])
    rough_mask_extraction(
        rough_mask_dir,
        raw_dwi_dir,
        subject_id,
        path_connectomist=path_connectomist)

    # Step 4 - Detect and correct outlying diffusion slices
    outliers_dir = os.path.join(outdir, STEPS[2])
    outlying_slice_detection(
        outliers_dir,
        raw_dwi_dir,
        rough_mask_dir,
        subject_id,
        path_connectomist=path_connectomist)

    # Step 5 - Susceptibility correction
    susceptibility_dir = os.path.join(outdir, STEPS[3])
    susceptibility_correction(
        susceptibility_dir,
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

    # Step 6 - Eddy current and motion correction
    eddy_motion_dir = os.path.join(outdir, STEPS[4])
    eddy_and_motion_correction(
        eddy_motion_dir,
        raw_dwi_dir,
        rough_mask_dir,
        susceptibility_dir,
        subject_id,
        path_connectomist=path_connectomist)

    # Step 7 - Export result as a Nifti with a .bval and a .bvec
    preproc_files = export_eddy_motion_results_to_nifti(
        eddy_motion_dir,
        outdir=outdir,
        filename="dwi")
    preproc_dwi, preproc_bval, preproc_bvec = preproc_files

    # Step 8 - Export outliers.py
    path_outliers_py = os.path.join(outliers_dir, "outliers.py")
    preproc_outliers = os.path.join(outdir, "outliers.py")
    shutil.copy(path_outliers_py, preproc_outliers)

    # Step 9 - Registration t1 - dwi
    if morphologist_dir is not None:
        registration_dir = os.path.join(outdir, STEPS[5])
        dwi_to_anatomy(
            registration_dir,
            eddy_motion_dir,
            rough_mask_dir,
            morphologist_dir,
            subject_id,
            path_connectomist=path_connectomist)

    # Step 10 - Delete intermediate files and directories if requested
    if delete_steps:
        intermediate_dirs = [raw_dwi_dir, rough_mask_dir, outliers_dir,
                             susceptibility_dir, eddy_motion_dir]
        for directory in intermediate_dirs:
            shutil.rmtree(directory)

    return preproc_dwi, preproc_bval, preproc_bvec, preproc_outliers
