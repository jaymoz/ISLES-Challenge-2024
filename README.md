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


