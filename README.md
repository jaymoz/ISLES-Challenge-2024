# Team Ninjas - MICCAI ISLES 24 Challenge (Top 3)

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

This repository contains the implementation used by Team Ninjas, ranked in the top 3 at the MICCAI ISLES 24 Challenge. We aim to fully exploit the rich temporal and spatial information within the 4D CTP data. Our approach involves capturing the dynamics of the contrast agent by extracting time points from the 4D CTP data with the highest concentration. This is crucial because these time points reflect the temporal progression of blood flow and tissue perfusion, which are vital for accurately segmenting ischemic stroke lesions. We leveraged the nnUNETv2 3d full resolution model for segmentation.

## Table of Contents
1. [Installation](#installation)
2. [Data Preprocessing](#data-preprocessing)
3. [Model Training](#model-training)
4. [Inference](#inference)
5. [Citation](#citation)
6. [License](#license)

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
      - Update the `INPUT_DIR` variable in the `skull_strip.sh` script. This should be the path to the folder containing the extracted time-points.
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

## Inference


