# !/bin/bash

INPUT_DIR="PATH_TO_DIRECTORY_CONTAINING_TIMEPOINTS"

# for input_file in "$INPUT_DIR"/*0002*.nii.gz; do
for input_file in "$INPUT_DIR"/*0000*.nii.gz; do
    filename=$(basename "$input_file")

    #Run the Docker command
    docker run --gpus all --mount type=bind,source=$($input_file),target=/$filename \
               freesurfer/synthstrip:1.6 -i $filename -o $filename

done
