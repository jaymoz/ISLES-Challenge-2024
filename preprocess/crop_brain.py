import os
import numpy as np
import nibabel as nib
from monai.transforms import CropForegroundd
import torch
from tqdm import tqdm
from monai.data import MetaTensor
import torchio as tio

def crop_foreground_(images_dir, masks_dir, num_modalities):
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
                modality_name = filename.split('_')[3].split('.')[0]

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


images_directory = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images'
masks_directory = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\masks'
num_modalities = 20
crop_foreground_(images_directory, masks_directory, num_modalities)


# def crop_foreground_(images_dir, masks_dir):
#     crop = CropForegroundd(
#         keys=['ctp', 'cbf', 'cbv', 'ncct', 'mask'],
#         source_key='ncct',
#         allow_smaller=True,
#         return_coords=True
#     )

#     patients = {}
#     for img_filename in tqdm(os.listdir(images_dir), desc="Grouping imaging modalities by patients"):
#         if img_filename.endswith('.nii.gz') or img_filename.endswith(".nii"):
#             patient_id = img_filename.split('_')[1]
#             if patient_id not in patients:
#                 patients[patient_id] = []
#             patients[patient_id].append(os.path.join(images_dir, img_filename))

#     for img_filename in tqdm(os.listdir(masks_dir), desc="Grouping Masks by patients"):
#         if img_filename.endswith('.nii.gz') or img_filename.endswith(".nii"):
#             patient_id = img_filename.split('_')[1][:3]
#             patients[patient_id].append(os.path.join(masks_dir, img_filename))

#     for patient_id, filenames in tqdm(patients.items(), desc="Cropping foreground of imaging modalities"):
#         cbf_path = filenames[0]
#         cbv_path = filenames[1]
#         ctp_path = filenames[2]
#         ncct_path = filenames[3]
#         mask_path = filenames[4]

#         try:
#             cbf_data_nib = nib.load(cbf_path)
#             cbv_data_nib = nib.load(cbv_path)
#             ctp_data_nib = nib.load(ctp_path)
#             ncct_data_nib = nib.load(ncct_path)
#             mask_data_nib = nib.load(mask_path)

#             cbf_fdata = cbf_data_nib.get_fdata()
#             cbv_fdata = cbv_data_nib.get_fdata()
#             ctp_fdata = ctp_data_nib.get_fdata()
#             ncct_fdata = ncct_data_nib.get_fdata()
#             mask_fdata = mask_data_nib.get_fdata()

#             # Ensure the input tensors are 4D by adding a channel dimension
#             cbf_data = torch.tensor(cbf_fdata, dtype=torch.float32).unsqueeze(0)  # Add channel dimension
#             cbv_data = torch.tensor(cbv_fdata, dtype=torch.float32).unsqueeze(0)  # Add channel dimension
#             ctp_data = torch.tensor(ctp_fdata, dtype=torch.float32).unsqueeze(0)  # Add channel dimension
#             ncct_data = torch.tensor(ncct_fdata, dtype=torch.float32).unsqueeze(0)  # Add channel dimension
#             mask_data = torch.tensor(mask_fdata, dtype=torch.float32).unsqueeze(0)  # Add channel dimension

#             data = {'ctp':ctp_data, 'cbf':cbf_data, 'cbv':cbv_data, 'ncct':ncct_data, 'mask':mask_data}

#             transformed = crop(data)
#             cropped_cbf = transformed['cbf'].numpy()
#             cropped_cbv = transformed['cbv'].numpy()
#             cropped_ctp = transformed['ctp'].numpy()
#             cropped_ncct = transformed['ncct'].numpy()
#             cropped_mask = transformed['mask'].numpy()

#             assert cropped_cbf.shape == cropped_cbv.shape == cropped_ctp.shape == cropped_ncct.shape == cropped_mask.shape, "Shapes do not match after cropping"


#             # Use TorchIO to update the affine matrix
#             subject = tio.Subject(
#                 cbf=tio.ScalarImage(tensor=cropped_cbf, affine=ncct_data_nib.affine),
#                 cbv=tio.ScalarImage(tensor=cropped_cbv, affine=ncct_data_nib.affine),
#                 ctp=tio.ScalarImage(tensor=cropped_ctp, affine=ncct_data_nib.affine),
#                 ncct=tio.ScalarImage(tensor=cropped_ncct, affine=ncct_data_nib.affine),
#                 mask=tio.LabelMap(tensor=cropped_mask, affine=ncct_data_nib.affine)
#             )

#             # Save the transformed images
#             subject.cbf.save(cbf_path)
#             subject.cbv.save(cbv_path)
#             subject.ctp.save(ctp_path)
#             subject.ncct.save(ncct_path)
#             subject.mask.save(mask_path)

#         except Exception as e:
#             print(f"Error processing patient {patient_id}: {e}")


# images_directory = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\after'
# masks_directory = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\masks'
# crop_foreground_(images_directory, masks_directory)