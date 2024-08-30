#!/bin/bash

python process_4D_ctp.py
python grant_permission.py
bash skull_strip.sh
python skull_strip.py
python crop_brain.py
python split_dataset.py
