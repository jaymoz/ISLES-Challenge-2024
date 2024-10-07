# Team Ninjas - MICCAI ISLES 24 Challenge (Top 3)

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

This repository contains the implementation used by Team Ninjas, ranked in the top 3 at the MICCAI ISLES 24 Challenge. We aim to fully exploit the rich temporal and spatial information within the 4D CTP data. Our approach involves capturing the dynamics of the contrast agent by extracting time points from the 4D CTP data with the highest concentration. This is crucial because these time points reflect the temporal progression of blood flow and tissue perfusion, which are vital for accurately segmenting ischemic stroke lesions. We leveraged the nnUNETv2 3d full resolution model for segmentation.

Our algorithm heavily relies on nnUNetv2. Please check out the documentation [here](https://github.com/MIC-DKFZ/nnUNet/tree/master/documentation).
## Table of Contents
1. [Installation](#installation)
2. [Data Preprocessing](#data-preprocessing)
3. [Model Training](#model-training)
4. [Inference](#inference)
5. [Team](#team)

## Installation

Clone the repository:
```bash
git clone https://github.com/jaymoz/ISLES-Challenge-2024.git
cd ISLES-Challenge-2024
```
You must first set up a few things on your local machine or a capable server such as the model that will be used(nnUNetv2). You need to set paths on your machine representing where you save raw data, preprocessed data, and trained models.
* nnUNet_raw: This is where you put your starting point data. It should follow the nnUNet datasets naming [convention](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format.md).
* nnUNet_preprocessed: Preprocessed data will be saved here. This folder will be used by nnUNet when you run the preprocessing command to save the preprocessed data.
* nnUNet_results: This is the folder where nnUNet will save the training artifacts, including model weights, configuration JSON files and debug output.

We recommend creating the following structure:

```
├── dataset/               # Directory for input data (not stored in the repo)
│   ├── ISLES_24_dataset/  # Replace this with the ISLES 24 dataset
│   ├── preprocessed/      # Temporary directory for holding preprocessed data
│       ├── images/
│       ├── masks/
├── models/                # Pre-trained models and checkpoints
│       ├── workspace/
│           ├── datasets/
|                ├── nnunet_data/
│                  ├── nnUNet_predictions/
│                  ├── nnUNet_preprocessed/
│                  ├── nnUNet_raw/
│                  ├── nnUNet_results/
├── preprocess/            # Directory containing all the preprocessing scripts
│   ├── process_4D_ctp.py
|      ...
│   └── split_dataset.py  
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── LICENSE                # License for the project
```

### nnUNET Setup
Before installing nnUNET, we recommend creating a virtual environment. You can install `nnUNETv2` using the following steps:

```bash
python3 -m venv nnunet-env
source nnunet-env/bin/activate
```
Install dependencies in the virual environment:
```bash
pip3 install -r requirements.txt
```

Install torch locally [here](https://pytorch.org/get-started/locally/).
Clone the official `nnUNET` repository:
```bash
cd models/workspace
git clone https://github.com/MIC-DKFZ/nnUNet.git
cd nnUNet
pip install -e .
```
(OPTIONAL) Install hiddenlayer. hiddenlayer enables nnU-net to generate plots of the network topologies it generates (see Model training). To install hiddenlayer, run the following command:
```bash
pip3 install --upgrade git+https://github.com/FabianIsensee/hiddenlayer.git
```

## Data Preprocessing

We use the preprocessed data provided by the ISLES 24 challenge. You can download the dataset [here](https://isles-24.grand-challenge.org/dataset/). Additional preprocessing steps were applied before feeding the data into our model. The goal of our preprocessing is to extract **20 time-points** (a sequence of 3D images) from each 4D CT Perfusion (CTP) scan. This will be fed as a 20-channel input to an nnUNetv2 3D full resolution model.

### Steps to Preprocess the Data

1. **Edit Path Variables**
   - Update the path variables in the `preprocess/process_4D_ctp.py` file to match your local directory structure.

2. **Run the Preprocessing Script**
   ```bash
   python3 preporcess/process_4D_ctp.py
   ```
   - Running this script will process each 4D CTP scan in the ISLES 24 dataset as follows:
     - **Clip voxel intensities**: 
       - All voxel values are clipped to a range of **0 to 100 Hounsfield Units (HU)**. This eliminates outliers and helps separate the brain from the skull.
     - **Identify the peak intensity time-point**: 
       - The script identifies the time-point where the concentration of the contrast agent is at its maximum, then extracts **20 time-points** centered around this peak.
     - **Save time-points in nnUNet format**:
       - The extracted time-points are saved using the following nnUNet dataset naming convention:
         ```
         {DATASET_NAME}_{CASE_ID}_{XXXX}.nii.gz
         ```
         where:
         - `DATASET_NAME` is a unique identifier for the dataset. We use `BRAIN` in this implementation.
         - `CASE_ID` refers to the last three digits of the patient's ID, uniquely identifying each patient.
         - `XXXX` is a 4-digit modality/channel identifier. In our case, it is a 4-digit zero-padded index representing the time-point position (e.g., `0000` for the first time-point, `0019` for the last).
   
         **Example for time-point images**:
         ```
         BRAIN_001_0000.nii.gz
         BRAIN_001_0001.nii.gz
         ...
         BRAIN_001_0019.nii.gz
         ```

     - **Save lesion masks**:
       - The corresponding lesion masks are saved with the following format:
         ```
         {DATASET_NAME}_{CASE_ID}.nii.gz
         ```

         **Example for mask**:
         ```
         BRAIN_001.nii.gz
         ```
4. **Skull Stripping**
      - Update the `INPUT_DIR` variable in the `preprocess/skull_strip.sh` script. This should be the path to the folder containing the extracted time-points.
      - The script uses the SynthStrip Docker image, so ensure that Docker is installed on your local machine.
      - Note: This script will only perform skull stripping on the first time-point for each patient to minimize processing time, as the Docker image may take too long to process all time-points.
      - Run the script using the following command:
        ```bash
        bash preprocess/skull_strip.sh
        ```
      - Next, execute the `skull_strip.py` script:
        ```bash
        python3 preprocess/skull_strip.py
        ```
        - This script will compute the mask from the first time-point of each patient and apply it to all subsequent time-points.
   
5. **Foreground Cropping**
      - We crop the foreground of all time-points to remove irrelevant information and retain only the brain region.
      - Edit the path variables in the `crop_brain.py` file to point to the folder containing the extracted time-points and masks.
      - Run the cropping script using the following command:
        ```bash
        python3 preprocess/crop_brain.py
        ```
        
## Model Training
Before we can begin training, we need to export some paths to the environment variables. These paths are: nnUNet_raw, nnUNet_preprocessed, nnUNet_results, nnUNet_predictions. You can set them
directly in the terminal where you’re going to run nnUNet commands from.  
On Linux:
```bash
export nnUNet_raw="PATH TO models/workspace/datasets/nnunet_data/nnUNet_raw"
export nnUNet_preprocessed="PATH TO models/workspace/datasets/nnunet_data/nnUNet_preprocessed"
export nnUNet_results="PATH TO models/workspace/datasets/nnunet_data/nnUNet_results"
export nnUNet_predictions="PATH TO models/workspace/datasets/nnunet_data/nnUNet_results"
```
On Windows:
```bash
set nnUNet_raw="PATH TO models\workspace\datasets\nnunet_data\nnUNet_raw"
set nnUNet_preprocessed="PATH TO models\workspace\datasets\nnunet_data\nnUNet_preprocessed"
set nnUNet_results="PATH TO models\workspace\datasets\nnunet_data\nnUNet_results"
set nnUNet_predictions="PATH TO models\workspace\datasets\nnunet_data\nnUNet_results"
```
Note: This only sets the environment variables temporarily. Meaning that if you close your terminal or you open another terminal window, then these variables will need to be set again.

If you want a more permanent solution, then you should add these commands in the .bashrc file if you’re on Linux or you could add them as environment variables in the “Edit system environment variables” panel on Windows.

Next, we split our dataset into train, validation and test sets. You can modify the preprocess/split_dataset.py file for your desired split ratio. In our case, we choose 90% for training and validation in a 5-fold cross validation setup, and 10% for testing. Ensure that the path variables are correct and updated. 

```bash
python3 preprocess/split_dataset.py
```
Copy the dataset.json file in `utils/` and place it inside nnUNet_raw/Dataset100_BRAIN/ folder. The structure should look like this:
```
├── models/
│       ├── workspace/
│           ├── datasets/
|                ├── nnunet_data/
│                  ├── nnUNet_predictions/
│                  ├── nnUNet_preprocessed/
│                  ├── nnUNet_raw/
|                      ├── Dataset100_BRAIN/
|                         ├── imagesTr/
|                         ├── imagesTs/
|                         ├── labelsTr/
|                         ├── dataset.json
│                  ├── nnUNet_results/
```
100 in Dataset100_BRAIN is a unique identifier for the dataset. This MUST follow the nnUNet format. We need this ID when running the `nnUNetve_plan_and_preprocess` command.
If you used different split ratios for training, validation, and test then adjust the `numTraining` parameters in the file (dataset.json) to reflect the number of training samples.
Next, run:

```bash
nnUNetv2_plan_and_preprocess -d 100 -pl nnUNetPlannerResEncM
```
nnUNetv2_plan_and_preprocess: This command initializes the planning and preprocessing steps for the nnUNetv2 framework. It sets up your dataset for training, including necessary configurations and transformations.

-d 100: A unique identifier for the dataset.

-pl nnUNetPlannerResEncM: This flag specifies the planner used during the preprocessing step. We use the residual encoder medium presets.

Once the planning and preprocessing is complete, you can begin training. We train a 3D full resolution model using a 5-fold cross validation setup. You can train each fold using the following command:
For the first fold:
```bash
nnUNetv2_train 100 3d_fullres 0 -p nnUNetResEncUNetMPlans
```
For the second fold:
```bash
nnUNetv2_train 100 3d_fullres 1 -p nnUNetResEncUNetMPlans
```
For the third fold:
```bash
nnUNetv2_train 100 3d_fullres 2 -p nnUNetResEncUNetMPlans
```
For the fourth fold:
```bash
nnUNetv2_train 100 3d_fullres 3 -p nnUNetResEncUNetMPlans
```
For the fifth fold:
```bash
nnUNetv2_train 100 3d_fullres 4 -p nnUNetResEncUNetMPlans
```

If you have multiple GPUs, you can train each fold on each GPU by specifying:
```bash
CUDA_VISIBLE_DEVICES=0 nnUNetv2_train 100 3d_fullres 0 -p nnUNetResEncUNetMPlans
```
This will train the first fold on the first GPU. Subsequently,
```bash
CUDA_VISIBLE_DEVICES=1 nnUNetv2_train 100 3d_fullres 1 -p nnUNetResEncUNetMPlans
```
will train the second fold on the second GPU. If you plan on training using multiple GPUs, you should wait for the dataset to finish unpacking and training to commence before running the command on other GPUs.

## Inference

To make predictions using nnUNetv2, you can use the following command structure:

```bash
nnUNetv2_predict -i <INPUT_IMAGES_DIRECTORY> -o <OUTPUT_PREDICTIONS_DIRECTORY> -d <DATASET_ID> -c <CONFIGURATION> -tr <TRAINER> -p <PLANS> -chk <CHECKPOINT_FILE>
```

- **`-i <INPUT_IMAGES_DIRECTORY>`**:  
  Path to the directory containing the input images for which predictions will be made.

- **`-o <OUTPUT_PREDICTIONS_DIRECTORY>`**:  
  Path to the directory where the predictions will be saved.

- **`-d <DATASET_ID>`**:  
  The ID of the dataset you are working with (e.g., `100` for your custom dataset).

- **`-c <CONFIGURATION>`**:  
  The configuration to use for the predictions (e.g., `3d_fullres`).

- **`-tr <TRAINER>`**:  
  The trainer type to use for making predictions (e.g., `nnUNetTrainer`).

- **`-p <PLANS>`**:  
  The planning strategy used for the specific model architecture (e.g., `nnUNetResEncUNetMPlans`).

- **`-chk <CHECKPOINT_FILE>`**:  
  The filename of the checkpoint from which to load the model weights for making predictions (e.g., `checkpoint_latest.pth`, `checkpoint_final`, `checkpoint_best`).
  An example is given below:

  ```bash
  nnUNetv2_predict -i /path/to/models/workspace/nnunet_data/nnUNet_raw/Dataset100_BRAIN/imagesTs -o /path/to/models/workspace/nnunet_data/nnUNet_predictions -d 100 -c 3d_fullres -tr nnUNetTrainer -p nnUNetResEncUNetMPlans -chk checkpoint_latest.pth
  ```

## Team

If you have questions, please contact [jacob.idoko@ucalgary.ca](mailto:jacob.idoko@ucalgary.ca). Our team members include:

- **Jacob Idoko**<sup>1</sup>
- **Salome Bosshart**<sup>1</sup>
- **Alexander Stebner**<sup>1</sup>
- **Johanna Ospel**<sup>1</sup>
- **Mayank Goyal**<sup>1</sup>
- **Nikita Malik**<sup>2</sup>
- **Atindra Jayakar**<sup>3</sup>
- **Roberto Souza**<sup>1</sup>
- **Mariana Bento**<sup>1</sup>
- **Gouri Ginde**<sup>1</sup>

<small>
<sup>1</sup>University of Calgary, Canada <br>
<sup>2</sup>Manipal Institute of Technology, India <br>
<sup>3</sup>Mukesh Patel School of Technology Management and Engineering, India
</small>
