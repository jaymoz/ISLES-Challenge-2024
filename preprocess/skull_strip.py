import os
import nibabel as nib
import numpy as np
from tqdm import tqdm


def apply_mask(mask_img, target_img):
    """
    Applies a binary mask to a target image.
    
    Parameters:
    - mask_img: A NIfTI image object representing the skull-stripped mask.
    - target_img: A NIfTI image object representing the target image to be masked.
    
    Returns:
    - A new NIfTI image object containing the masked data.
    """
    mask_data = mask_img.get_fdata()
    target_data = target_img.get_fdata()
    masked_data = target_data * (mask_data > 0)
    return nib.Nifti1Image(masked_data, target_img.affine)

def skullStrip(input_dir: str):
    """
    Groups NIfTI images by patient ID and applies the skull-stripped mask from the first time point 
    to all other modalities for each patient.

    Parameters:
    - input_dir: The directory containing the NIfTI images.
    """
    patients = {}
    for img_filename in tqdm(os.listdir(input_dir), desc="Grouping imaging modalities by patients"):
        if img_filename.endswith('.nii.gz') or img_filename.endswith(".nii"):
            patient_id = img_filename.split('_')[1]
            if patient_id not in patients:
                patients[patient_id] = []
            patients[patient_id].append(os.path.join(input_dir, img_filename))


    for patient_id, filepaths in tqdm(patients.items(), desc="Applying skull stripped masks to other modalities"):
        reference_img_path = next((fp for fp in filepaths if "0000" in fp), None)

        if reference_img_path:
            skull_stripped_img = nib.load(reference_img_path)
            for target_img_path in filepaths:
                if "0000" not in target_img_path:
                    target_img = nib.load(target_img_path)
                    masked_img = apply_mask(skull_stripped_img, target_img)
                    
                    output_filename = os.path.join(input_dir, os.path.basename(target_img_path))
                    nib.save(masked_img, output_filename)



input_dir = "PATH_TO_FOLDER CONTAINING TIMEPOINTS e.g preprocessed/images"

skullStrip(input_dir)
