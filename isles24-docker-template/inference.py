"""
The following is a simple example algorithm.

It is meant to run within a container.

To run it locally, you can call the following bash script:

  ./test_run.sh

This will start the inference and reads from ./test/input and outputs to ./test/output

To export the container and prep it for upload to Grand-Challenge.org you can call:

  docker save example-algorithm-preliminary-docker-evaluation | gzip -c > example-algorithm-preliminary-docker-evaluation.tar.gz

Any container that shows the same behavior will do, this is purely an example of how one COULD do it.

Happy programming!
"""

from pathlib import Path
from glob import glob
import SimpleITK
import os
import nibabel as nib
import numpy as np
import subprocess
from tqdm import tqdm
# from monai.transforms import CropForegroundd
# import torch

def run():
    INPUT_PATH = Path("/input")
    OUTPUT_PATH = Path("/output")

    CTP_NIFTII_INPUT_PATH = Path("/output/ctp_input/4d_data")
    CTP_NIFTII_OUTPUT_PATH = Path("/output/ctp_input/3d_timepoints")
    CTP_NIFTII_INPUT_PATH.mkdir(parents=True, exist_ok=True)
    CTP_NIFTII_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    image = load_image_file_as_simple_itk_image(
        location=INPUT_PATH / "images/preprocessed-perfusion-ct",
    )

    process_4D_ctp(image, CTP_NIFTII_OUTPUT_PATH)

    # crop_foreground_(CTP_NIFTII_OUTPUT_PATH, 20)

    os.environ['nnUNet_results'] = 'workspace/datasets/nnunet_data/nnUNet_results'
    os.environ['nnUNet_raw'] ='workspace/datasets/nnunet_data/nnUNet_raw'
    os.environ['nnUNet_preprocessed'] ='workspace/datasets/nnunet_data/nnUNet_preprocessed'
    input_dir = str(Path("/output/ctp_input/3d_timepoints/"))
    output_dir = str(OUTPUT_PATH / "images/stroke-lesion-segmentation/")

    command = [
        "nnUNetv2_predict",
        "-i", input_dir,
        "-o", output_dir,
        "-d", "100",
        "-c", "3d_fullres",
        "-f", "0",
        "-tr", "nnUNetTrainer",
        "-p", "nnUNetResEncUNetMPlans",
        "-chk", "checkpoint_latest.pth"
    ]
    subprocess.run(command, text=True)

    output_path = Path(output_dir)
    nii_file = next(output_path.glob("*.nii"), None) or next(output_path.glob("*.nii.gz"), None)
    stroke_lesion_segmentation = SimpleITK.ReadImage(nii_file)

    output_dir = OUTPUT_PATH / "images/stroke-lesion-segmentation/" 
    write_image_as_mha(
        location=output_dir,
        array=stroke_lesion_segmentation,
    )


def write_array_as_image_file(*, location, array):
    location.mkdir(parents=True, exist_ok=True)

    INPUT_PATH = Path("/input")
    output_filename = INPUT_PATH / "images/preprocessed-perfusion-ct"
    output_filename = glob(str(output_filename / "*.mha"))[0].split('/')[-1].split('.')[0]

    suffix = ".mha"
    image = SimpleITK.GetImageFromArray(array)
    SimpleITK.WriteImage(
        image,
        location / f"{output_filename}{suffix}",
        useCompression=True,
    )
    
def write_image_as_mha(*, location, array):
    location.mkdir(parents=True, exist_ok=True)

    INPUT_PATH = Path("/input")
    output_filename = INPUT_PATH / "images/preprocessed-perfusion-ct"
    output_filename = glob(str(output_filename / "*.mha"))[0].split('/')[-1].split('.')[0]

    suffix = ".mha"
    SimpleITK.WriteImage(
        array,
        location / f"{output_filename}{suffix}",
        useCompression=True,
    )

def load_image_file_as_simple_itk_image(*, location):
    input_files = glob(str(location / "*.mha"))
    result = SimpleITK.ReadImage(input_files[0])

    return result


def process_4D_ctp(original_image, output_dir):
    print("Scaling 4D CTP...")
    image = SimpleITK.GetArrayFromImage(original_image)
    direction_4d = original_image.GetDirection()
    direction_3d = (
        direction_4d[0], direction_4d[1], direction_4d[2],
        direction_4d[4], direction_4d[5], direction_4d[6],
        direction_4d[8], direction_4d[9], direction_4d[10]
    )

    reduced_id = 999
    prefix = "BRAIN"
    intensity_range = (0, 100)
    image = np.clip(image, *intensity_range)
    ctp_distribution = image.sum(axis=(1, 2, 3))
    peak_value = np.argmax(ctp_distribution)

    print("Done scaling 4D CTP...")

    start_timepoint = peak_value - 9
    end_timepoint = peak_value + 10

    if start_timepoint < 0:
        start_timepoint = 0
        end_timepoint = start_timepoint + 19
    elif end_timepoint > image.shape[0] - 1:
        end_timepoint = image.shape[0] - 1
        start_timepoint = end_timepoint - 19

    for i, timepoint in tqdm(enumerate(range(start_timepoint, end_timepoint + 1)), desc="Extracting 3D timepoints from 4D CT perfusion.."):
        timepoint_image = image[timepoint, :, :, :]

        nifti_image = SimpleITK.GetImageFromArray(timepoint_image)
        nifti_image.SetOrigin(original_image.GetOrigin()[:3])
        nifti_image.SetSpacing(original_image.GetSpacing()[:3])
        nifti_image.SetDirection(direction_3d)

        print("Shape of output: ", nifti_image.GetSize())

        timepoint_image_path = os.path.join(output_dir, f"{prefix}_{reduced_id}_{i:04d}.nii.gz")
        SimpleITK.WriteImage(nifti_image, timepoint_image_path, useCompression=False)
    
    print("Done extracting 3D timepoints...")



if __name__ == "__main__":
    raise SystemExit(run())
