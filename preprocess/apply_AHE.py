import os
import numpy as np
import torch
from tqdm import tqdm
import torchio as tio
import cv2 as cv

def adaptiveHistogramEqualization(image_path, clip_limit=2.0, tile_grid_size=(8, 8)):
    image = tio.ScalarImage(image_path)
    
    image_intensity = image.data.numpy()
    
    # Convert the intensity values to [0, 255] for CLAHE processing
    image_intensity_scaled = (image_intensity * 255 / 100).astype(np.uint8)

    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    # Apply CLAHE to each slice of the 3D image
    equalized_array = np.zeros_like(image_intensity_scaled)
    for i in range(image_intensity_scaled.shape[1]):  # Assuming shape is (1, Z, Y, X)
        equalized_array[0, i] = clahe.apply(image_intensity_scaled[0, i])

    # Convert the equalized data back to the original scale [0, 100]
    equalized_array = equalized_array.astype(np.float32) * 100 / 255
    
    image.set_data(torch.from_numpy(equalized_array))
    image.save(image_path)


folder_path = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\after'

for filename in tqdm(os.listdir(folder_path), desc="Applying Adaptive Histogram Equalization to 3D CT scans..."):
    image_path = os.path.join(folder_path,filename)
    if filename.endswith('.nii.gz'):
        adaptiveHistogramEqualization(image_path)
