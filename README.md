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
Before you can use nnUNet, you must first set up a few things on your local machine or a capable server. You need to set paths on your machine representing where you save raw data, preprocessed data, and trained models.
* nnUNet_raw: This is where you put your starting point data. It should follow the nnUNet datasets naming [convention](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format.md).
* nnUNet_preprocessed: Preprocessed data will be saved here. This folder will be used by nnUNet when you run the preprocessing command (we will cover it below) in order to save the preprocessed data.
* nnUNet_results: this is the folder where nnUNet will save the training artifacts, including model weights, configuration JSON files and debug output.

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
│   ├── copy_rename.py
|      ...
│   └── split_dataset.py  
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── LICENSE                # License for the project
```

### nnUNET Setup
Before installing nnUNET, we recommend creating a virtual environment. You can install `nnUNETv2` using the following steps:
Create a virtual environment:
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
We use the preprocessed data provided in the ISLES 24 challenge. Additional data preprocessing was applied before being fed as input to a model. Our data preprocessing aims to extract 20 time-points (Sequence of 3D images) from each 4D CTP. 




