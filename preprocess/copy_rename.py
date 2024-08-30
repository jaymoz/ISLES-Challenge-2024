import os
import shutil
import random
import shutil
import logging
from tqdm import tqdm

def copyRename(cbf_cbv_dir, ncct_dir, masks_root, images_dst, masks_dst, prefix):

    # Create a mapping for CT modalities
    ct_mapping = {
        "ctp" : "0000",
    }
    os.makedirs(images_dst, exist_ok=True)
    os.makedirs(masks_dst, exist_ok=True)

    #copy NCCT file
    # for patient_folder in tqdm(os.listdir(ncct_dir), desc="Copying and renaming NCCT images"):
    #     if patient_folder.startswith('sub-stroke'):
    #         patient_id = patient_folder.split('-')[-1]
    #         # Reduce the ID to a 3-digit identifier
    #         reduced_id = patient_id[-3:]

    #         # Define the session directories
    #         ses_01_dir = os.path.join(ncct_dir, patient_folder, 'ses-01')
            
    #         if not os.path.exists(ses_01_dir):
    #             continue
 
    #         for file in os.listdir(ses_01_dir):
    #             if file.endswith('.nii.gz') and 'ncct' in file:
    #                 src_file = os.path.join(ses_01_dir, file)
    #                 dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['ncct']}.nii.gz")
    #                 print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['ncct']}.nii.gz"))
    #                 shutil.copy(src_file, dst_file)


    # copy CTA and Perfusion maps
    for patient_folder in tqdm(os.listdir(cbf_cbv_dir), desc="Copying and renaming CT Perfusion Maps"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            # Reduce the ID to a 3-digit identifier
            reduced_id = patient_id[-3:]

            # Define the session directories
            ses_01_dir = os.path.join(cbf_cbv_dir, patient_folder, 'ses-01')
            perfusion_maps_dir = os.path.join(ses_01_dir, "perfusion-maps")
            
            if not os.path.exists(ses_01_dir):
                continue


            #copy cta file
            # for file in os.listdir(ses_01_dir):
            #     if file.endswith('.nii.gz') and 'ncct_cta' in file:
            #         src_file = os.path.join(ses_01_dir, file)
            #         dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['cta']}.nii.gz")
            #         print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['cta']}.nii.gz"))
            #         shutil.copy(src_file, dst_file)

            #copy ctp
            for file in os.listdir(ses_01_dir):
                if file.endswith('.nii.gz') and 'ncct_ctp' in file:
                    src_file = os.path.join(ses_01_dir, file)
                    dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['ctp']}.nii.gz")
                    print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['ctp']}.nii.gz"))
                    shutil.copy(src_file, dst_file)
                    
            # #copy cbf file  
            # for file in os.listdir(perfusion_maps_dir):
            #     if file.endswith('.nii.gz') and 'ncct_cbf' in file:
            #         src_file = os.path.join(perfusion_maps_dir, file)
            #         dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['cbf']}.nii.gz")
            #         print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['cbf']}.nii.gz"))
            #         shutil.copy(src_file, dst_file)

            # #copy cbv file
            # for file in os.listdir(perfusion_maps_dir):
            #     if file.endswith('.nii.gz') and 'ncct_cbv' in file:
            #         src_file = os.path.join(perfusion_maps_dir, file)
            #         dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['cbv']}.nii.gz")
            #         print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['cbv']}.nii.gz"))
            #         shutil.copy(src_file, dst_file)

            # #copy mtt file
            # for file in os.listdir(perfusion_maps_dir):
            #     if file.endswith('.nii.gz') and 'ncct_mtt' in file:
            #         src_file = os.path.join(perfusion_maps_dir, file)
            #         dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['mtt']}.nii.gz")
            #         print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['mtt']}.nii.gz"))
            #         shutil.copy(src_file, dst_file)

            # #copy tmax file
            # for file in os.listdir(perfusion_maps_dir):
            #     if file.endswith('.nii.gz') and 'ncct_tmax' in file:
            #         src_file = os.path.join(perfusion_maps_dir, file)
            #         dst_file = os.path.join(images_dst, f"{prefix}_{reduced_id}_{ct_mapping['tmax']}.nii.gz")
            #         print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['tmax']}.nii.gz"))
            #         shutil.copy(src_file, dst_file)

            
    # Copy and rename the lesion mask
    for patient_folder in tqdm(os.listdir(masks_root), desc="Copying and renaming lesion masks"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            # Reduce the ID to a 3-digit identifier
            reduced_id = patient_id[-3:]

            # Define the session directories
            ses_02_dir = os.path.join(masks_root, patient_folder, 'ses-02')
            
            # Ensure session directories exist
            if not os.path.exists(ses_02_dir):
                continue
            
            for file in os.listdir(ses_02_dir):
                if file.endswith('.nii.gz') and 'lesion' in file:
                    src_file = os.path.join(ses_02_dir, file)
                    dst_file = os.path.join(masks_dst, f"{prefix}_{reduced_id}.nii.gz")
                    print("{} ----> {}".format(file, f"{prefix}_{reduced_id}.nii.gz"))
                    shutil.copy(src_file, dst_file)


# Copy and rename the files according to the nnUNET format

cbf_cbv_dir = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\ISLES_24\derivatives'
ncct_dir = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\ISLES_24\raw_data'
masks_root = r'C:\Users\ai2lab\Desktop\ISLES_2024\dataset\ISLES_24\derivatives'
images_dst = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images\before"
masks_dst = r"C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\masks"

prefix = "BRAIN"

copyRename(cbf_cbv_dir, ncct_dir, masks_root, images_dst, masks_dst, prefix)