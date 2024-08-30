import os
import nibabel as nib
import numpy as np
from tqdm import tqdm
import shutil
import torchio as tio

def process_4D_ctp(ctp_dir, masks_root, images_dst, masks_dst, prefix):

    os.makedirs(images_dst, exist_ok=True)
    os.makedirs(masks_dst, exist_ok=True)

    for patient_folder in tqdm(os.listdir(ctp_dir), desc="Copying and renaming CT Perfusion Maps..."):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            reduced_id = patient_id[-3:]

            ses_01_dir = os.path.join(ctp_dir, patient_folder, 'ses-01')
            
            if not os.path.exists(ses_01_dir):
                continue

            for file in os.listdir(ses_01_dir):
                if file.endswith('.nii.gz') and 'ncct_ctp' in file:
                    file_path = os.path.join(ses_01_dir, file)
                    image = tio.ScalarImage(file_path)
                    intensity_range = (0, 100)
                    image_intensity = image.data
                    image_intensity = np.clip(image_intensity, *intensity_range)
                    image.set_data(image_intensity)
                    image_array = np.asarray(image)
                    ctp_distribution = image_array.sum(axis = (1,2,3))
                    peak_value = np.argmax(ctp_distribution)

                    start_timepoint = peak_value - 9
                    end_timepoint = peak_value + 10

                    if start_timepoint < 0:
                        start_timepoint = 0
                        end_timepoint = start_timepoint + 19
                    elif end_timepoint > image_array.shape[0] - 1:
                        end_timepoint = image_array.shape[0] - 1
                        start_timepoint = end_timepoint - 19

                    affine = image.affine

                    for i, timepoint in enumerate(range(start_timepoint, end_timepoint + 1)):
                        timepoint_image = image_array[timepoint, :, :, :]
                        timepoint_image_path = os.path.join(images_dst, f"{prefix}_{reduced_id}_{i:04d}.nii.gz")

                        nifti_image = nib.Nifti1Image(timepoint_image, affine)
                        timepoint_image_path = os.path.join(images_dst, f"{prefix}_{reduced_id}_{i:04d}.nii.gz")
                        nib.save(nifti_image, timepoint_image_path)


    for patient_folder in tqdm(os.listdir(masks_root), desc="Copying and renaming lesion masks"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            reduced_id = patient_id[-3:]
            ses_02_dir = os.path.join(masks_root, patient_folder, 'ses-02')
            
            if not os.path.exists(ses_02_dir):
                continue
            
            for file in os.listdir(ses_02_dir):
                if file.endswith('.nii.gz') and 'lesion' in file:
                    src_file = os.path.join(ses_02_dir, file)
                    dst_file = os.path.join(masks_dst, f"{prefix}_{reduced_id}.nii.gz")
                    shutil.copy(src_file, dst_file)

ctp_dir = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\ISLES_24\derivatives'
masks_root = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\ISLES_24\derivatives'
images_dst = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images'
masks_dst = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\masks"

prefix = "BRAIN"

process_4D_ctp(ctp_dir, masks_root, images_dst, masks_dst, prefix)