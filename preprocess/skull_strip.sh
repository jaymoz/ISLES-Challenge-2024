# !/bin/bash

convert_to_unix_path() {
    local path=$1
    # Replace backslashes with forward slashes
    path=${path//\\//}
    echo "$path"
}

convert_to_windows() {
    local path=$1
    # Replace forward slashes with backslashes
    path=${path//\//\\}
    echo "$path"
}

INPUT_DIR=$(convert_to_windows "C:\Users\ai2lab\Desktop\ISLES_2024\dataset\preprocessed\images")

# for input_file in "$INPUT_DIR"/*0002*.nii.gz; do
for input_file in "$INPUT_DIR"/*0000*.nii.gz; do
    filename=$(basename "$input_file")

    #Run the Docker command
    docker run --gpus all --mount type=bind,source=$(convert_to_unix_path $input_file),target=/$filename \
               freesurfer/synthstrip:1.6 -i $filename -o $filename

done