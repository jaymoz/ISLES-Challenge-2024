import os
import nibabel as nib
import numpy as np
import torchio as tio
from tqdm import tqdm


def scale_images(image_path: str, output_folder: str, special_ids=None):
    if special_ids is None:
        special_ids = []

    # Load the image
    image = tio.ScalarImage(image_path)

    # Check if the ID is in the file name
    image_basename = os.path.basename(image_path)
    intensity_range = None

    for special_id in special_ids:
        if special_id in image_basename:
            # Scale intensity from 0 to the maximum value in the image
            intensity_range = (0, image.data.max())
            break

    if intensity_range is None:
        intensity_range = (0, 80)

    # Normalize CT scan intensity
    image_intensity = image.data
    image_intensity = np.clip(image_intensity, *intensity_range)

    min_intensity, max_intensity = intensity_range
    image_intensity = (image_intensity - min_intensity) / (max_intensity - min_intensity)
    image.set_data(image_intensity)

    # Save the scaled image
    os.makedirs(output_folder, exist_ok=True)
    image.save(os.path.join(output_folder, image_basename))


image_dir = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\before"
output_dir = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\after"

# Collect all image paths
image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.nii.gz')]

# Define special IDs for different scaling
special_ids = ['0000', '0003']

for image_path in tqdm(image_paths, desc="Scaling intensity..."):
    scale_images(image_path, output_dir, special_ids)

# def scale_images(image_path: str, output_folder: str):
#     # Load the image and mask
#     image = tio.ScalarImage(image_path)

#     # Normalize CT scan intensity to [0, 80]
#     image_intensity = image.data
#     image_intensity = np.clip(image_intensity, 0, 80)
#     # image_intensity = (image_intensity - 0) / (150 - 0)
#     image.set_data(image_intensity)

#     # Define the target voxel size (1x1x1 mm³)
#     # target_voxel_size = (1, 1, 1)

#     # Resample the image and mask
#     # resampler = tio.Resample(target_voxel_size)
#     # resampled_image = resampler(image)
#     # resampled_mask = resampler(mask)


#     # Save the resampled image
#     os.makedirs(output_folder, exist_ok=True)
#     image_basename = os.path.basename(image_path)
#     image.save(os.path.join(output_folder, image_basename))


# image_dir = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\before"
# output_dir = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\after"

# #Collect all image paths
# image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.nii.gz')]

# for image_path in tqdm(image_paths, desc="Scaling intensity..."):
#     scale_images(image_path, output_dir)