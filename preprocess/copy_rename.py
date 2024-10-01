import os
import shutil
import shutil
from tqdm import tqdm

def copyRename(source_dir: str, images_dst_dir : str, masks_dst_dir: str, prefix: str):
    """
    Copies and renames CT perfusion maps and lesion masks (following the nnUNet datasets naming convention) from the source directory to specified destination directories.

    Parameters:
    - source_dir (str): Path to the source directory containing patient folders.
    - images_dst_dir (str): Path to the destination directory for CT perfusion maps.
    - masks_dst_dir (str): Path to the destination directory for lesion masks.
    - prefix (str): Prefix for the renamed files.

    """
    ct_mapping = {
        "ctp" : "0000",
    }
    os.makedirs(images_dst_dir, exist_ok=True)
    os.makedirs(masks_dst_dir, exist_ok=True)

    # copy CTP
    for patient_folder in tqdm(os.listdir(source_dir), desc="Copying and renaming 4D CTP"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            # Reduce the ID to a 3-digit identifier
            reduced_id = patient_id[-3:]
            ses_01_dir = os.path.join(source_dir, patient_folder, 'ses-01')
            
            if not os.path.exists(ses_01_dir):
                continue

            for file in os.listdir(ses_01_dir):
                if file.endswith('.nii.gz') and 'ncct_ctp' in file:
                    src_file = os.path.join(ses_01_dir, file)
                    dst_file = os.path.join(images_dst_dir, f"{prefix}_{reduced_id}_{ct_mapping['ctp']}.nii.gz")
                    print("{} ----> {}".format(file, f"{prefix}_{reduced_id}_{ct_mapping['ctp']}.nii.gz"))
                    shutil.copy(src_file, dst_file)
            
    # Copy and rename the lesion mask
    for patient_folder in tqdm(os.listdir(source_dir), desc="Copying and renaming lesion masks"):
        if patient_folder.startswith('sub-stroke'):
            patient_id = patient_folder.split('-')[-1]
            # Reduce the ID to a 3-digit identifier
            reduced_id = patient_id[-3:]

            ses_02_dir = os.path.join(source_dir, patient_folder, 'ses-02')

            if not os.path.exists(ses_02_dir):
                continue
            
            for file in os.listdir(ses_02_dir):
                if file.endswith('.nii.gz') and 'lesion' in file:
                    src_file = os.path.join(ses_02_dir, file)
                    dst_file = os.path.join(masks_dst_dir, f"{prefix}_{reduced_id}.nii.gz")
                    print("{} ----> {}".format(file, f"{prefix}_{reduced_id}.nii.gz"))
                    shutil.copy(src_file, dst_file)


source_dir = 'Path to the source directory containing patient folders'
images_dst_dir = 'Path to the destination directory for CT perfusion maps'
masks_dst_dir = 'Path to the destination directory for lesion masks.'

prefix = "BRAIN"

copyRename(source_dir, images_dst_dir, masks_dst_dir, prefix)
