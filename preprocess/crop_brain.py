import os
import numpy as np
import nibabel as nib
from monai.transforms import CropForegroundd
import torch
from tqdm import tqdm
from monai.data import MetaTensor
import torchio as tio

def crop_foreground_(images_dir, masks_dir, num_modalities):
    """
    Crops the foreground of imaging modalities (this refers to the extracted timepoints) and their corresponding masks 
    by removing irrelevant regions and retaining only the brain region.

    Parameters:
    - images_dir: The directory containing the NIfTI images for the modalities.
    - masks_dir: The directory containing the NIfTI masks corresponding to the modalities. 
    - num_modalities: The number of modalities to process, used to generate modality keys (in our case 20, corresponding to the 20 extracted timepoints).

    Process:
    - Groups NIfTI images and masks by patient ID.
    - For each patient, verifies that all required modalities and masks are present.
    - Loads the images and masks into tensors.
    - Applies the `CropForegroundd` transformation to crop the relevant brain region from all modalities.
    - Saves the cropped images and masks back to their original paths.
    - Prints an error message if any modalities are missing or if there is an exception during processing.

    Notes:
    - The function expects the image filenames to follow the format "{DATASET_NAME}_{CASE_ID}_{XXXX}.nii.gz",
      where XXXX is the modality/channel identifier.
    - The mask is expected to follow the format "{DATASET_NAME}_{CASE_ID}.nii.gz".
    """
    modality_keys = [f"{i:04d}" for i in range(num_modalities)]
    modality_keys.append('mask')
    crop = CropForegroundd(
        keys=modality_keys,
        source_key='0000',
        allow_smaller=True,
        return_coords=True
    )

    patients = {}
    for img_filename in tqdm(os.listdir(images_dir), desc="Grouping imaging modalities by patients"):
        if img_filename.endswith('.nii.gz') or img_filename.endswith(".nii"):
            patient_id = img_filename.split('_')[1]
            if patient_id not in patients:
                patients[patient_id] = []
            patients[patient_id].append(os.path.join(images_dir, img_filename))

    for img_filename in tqdm(os.listdir(masks_dir), desc="Grouping Masks by patients"):
        if img_filename.endswith('.nii.gz') or img_filename.endswith(".nii"):
            patient_id = img_filename.split('_')[1][:3]
            if patient_id in patients:
                patients[patient_id].append(os.path.join(masks_dir, img_filename))

    for patient_id, filenames in tqdm(patients.items(), desc="Cropping foreground of imaging modalities"):
        modality_paths = {key: None for key in modality_keys}
        for index, filename in enumerate(filenames):
            if index == len(filenames) - 1:
                modality_name = 'mask'
            else:
                modality_name = filename.split('_')[-1].split('.')[0]

            if modality_name in modality_keys:
                modality_paths[modality_name] = filename

        if not all(modality_paths[key] is not None for key in modality_keys):
            print(f"Missing modalities for patient {patient_id}")
            continue
        try:
            modality_data = {}
            for key in modality_keys:
                modality_data[key] = nib.load(modality_paths[key]).get_fdata()

            data_tensors = {key: torch.tensor(modality_data[key], dtype=torch.float32).unsqueeze(0) for key in modality_keys}

            transformed = crop(data_tensors)
            cropped_data = {key: transformed[key].numpy() for key in modality_keys}

            affine = nib.load(modality_paths['0000']).affine 
            subject = tio.Subject(
                **{key: tio.ScalarImage(tensor=cropped_data[key], affine=affine) for key in modality_keys if key != 'mask'},
                mask=tio.LabelMap(tensor=cropped_data['mask'], affine=affine)
            )

            for key in modality_keys:
                subject[key].save(modality_paths[key])
        except Exception as e:
            print(f"Error processing patient {patient_id}: {e}")


images_directory = 'PATH_TO_FOLDER_CONTAINING_TIMEPOINTS e.g preprocessed/images'
masks_directory = 'PATH_TO_FOLDER_CONTAINING_MASKS e.g preprocessed/masks'
num_modalities = 20
crop_foreground_(images_directory, masks_directory, num_modalities)
