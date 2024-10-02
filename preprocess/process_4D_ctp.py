import SimpleITK as sitk
import os
import numpy as np
import shutil
from tqdm import tqdm

def processCTP(input_dir: str, images_dst: str, masks_dst: str, prefix: str):
    """
    Processes 4D CT perfusion (CTP) maps and lesion masks, clips image intensities, extracts relevant
    timepoints around the peak perfusion, and saves the resulting images and masks following the nnUNet dataset naming convention.

    Parameters:
    - input_dir (str): 
        The root directory containing 4D CT perfusion image files. For the ISLES 24 dataset, it is the path to the derivates folder.
    - images_dst (str): 
        The destination directory where the processed 4D CT perfusion timepoint images will be saved.
    - masks_dst (str): 
        The destination directory where the lesion masks will be copied to.
    - prefix (str): 
        A prefix to be added to the saved image and mask filenames, helping to uniquely identify each processed file.
    """

    os.makedirs(images_dst, exist_ok=True)
    os.makedirs(masks_dst, exist_ok=True)

    for patient_folder in tqdm(os.listdir(input_dir), desc="Copying and renaming CT Perfusion Maps..."):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            reduced_id = patient_id[-3:]

            ses_01_dir = os.path.join(input_dir, patient_folder, 'ses-01')
            
            if not os.path.exists(ses_01_dir):
                continue

            for file in os.listdir(ses_01_dir):
                if file.endswith('.nii.gz') and 'ncct_ctp' in file:
                    file_path = os.path.join(ses_01_dir, file)
                    
                    # Read the NIfTI image using SimpleITK
                    image = sitk.ReadImage(file_path)
                    direction_4d = image.GetDirection()
                    direction_3d = (
                        direction_4d[0], direction_4d[1], direction_4d[2],
                        direction_4d[4], direction_4d[5], direction_4d[6],
                        direction_4d[8], direction_4d[9], direction_4d[10]
                    )
                    
                    # Convert to a numpy array for processing
                    image_array = sitk.GetArrayFromImage(image)  # Shape: (T, Z, Y, X)

                    # Clip intensity values between 0 and 100
                    intensity_range = (0, 100)
                    image_array = np.clip(image_array, *intensity_range)
                    
                    # Calculate the distribution of intensities over time
                    ctp_distribution = image_array.sum(axis=(1, 2, 3))
                    peak_value = np.argmax(ctp_distribution)

                    # Define time window around the peak value
                    start_timepoint = peak_value - 9
                    end_timepoint = peak_value + 10

                    # Ensure start and end points are within bounds
                    if start_timepoint < 0:
                        start_timepoint = 0
                        end_timepoint = start_timepoint + 19
                    elif end_timepoint > image_array.shape[0] - 1:
                        end_timepoint = image_array.shape[0] - 1
                        start_timepoint = end_timepoint - 19

                    # Process and save each timepoint image
                    for i, timepoint in enumerate(range(start_timepoint, end_timepoint + 1)):
                        timepoint_image = image_array[timepoint, :, :, :]
                        
                        # Convert back to SimpleITK image
                        timepoint_image_sitk = sitk.GetImageFromArray(timepoint_image)
                        
                        # Set the 3D metadata (origin, spacing, direction)
                        timepoint_image_sitk.SetOrigin(image.GetOrigin()[:3])
                        timepoint_image_sitk.SetSpacing(image.GetSpacing()[:3])
                        timepoint_image_sitk.SetDirection(direction_3d)

                        # Save the image to the destination folder
                        timepoint_image_path = os.path.join(images_dst, f"{prefix}_{reduced_id}_{i:04d}.nii.gz")
                        sitk.WriteImage(timepoint_image_sitk, timepoint_image_path)

    # Process the lesion masks
    for patient_folder in tqdm(os.listdir(input_dir), desc="Copying and renaming lesion masks"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            reduced_id = patient_id[-3:]
            ses_02_dir = os.path.join(input_dir, patient_folder, 'ses-02')
            
            if not os.path.exists(ses_02_dir):
                continue
            
            for file in os.listdir(ses_02_dir):
                if file.endswith('.nii.gz') and 'lesion' in file:
                    src_file = os.path.join(ses_02_dir, file)
                    dst_file = os.path.join(masks_dst, f"{prefix}_{reduced_id}.nii.gz")
                    
                    # Copy the lesion mask to the destination folder
                    shutil.copy(src_file, dst_file)

input_dir = 'PATH_TO_DERIVATIVES_FOLDER'
images_dst = 'Path to the preprocessed/images folder'
masks_dst = 'path to preprocessed/masks folder'

prefix = "BRAIN"

processCTP(input_dir, images_dst, masks_dst, prefix)
