import os
import shutil
import random
import shutil
import logging
from tqdm import tqdm

class DATASET_SPLITTER:

    """
        Splits a dataset into train and test sets.

        Args:
            images_dir (str): Directory containing the images.
            labels_dir (str): Directory containing the corresponding labels.
            output_dir (str): Directory to save the split dataset.
            train_ratio (float): Ratio of data to be allocated for training (default is 0.9).
            test_ratio (float): Ratio of data to be allocated for testing (default is 0.1).
    """
    
    def __init__(self, images_dir, labels_dir, output_dir, train_ratio=0.9, test_ratio=0.1):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.output_dir = output_dir
        self.train_ratio = train_ratio
        self.test_ratio = test_ratio
        self.setup_directories()

    def setup_directories(self):
        self.dirs = {
            'train': {'images': os.path.join(self.output_dir, 'imagesTr'),
                      'labels': os.path.join(self.output_dir, 'labelsTr')},
            'test': {'images': os.path.join(self.output_dir, 'imagesTs'),
                     'labels':os.path.join(self.output_dir, 'labelsTs')}
        }
        for d in self.dirs.values():
            for path in d.values():
                os.makedirs(path, exist_ok=True)

    def get_patient_ids(self):
        images = os.listdir(self.images_dir)
        patient_ids = sorted(set([img.split('_')[1] for img in images]))
        return patient_ids

    def split_data(self, patient_ids):
        random.shuffle(patient_ids)
        total = len(patient_ids)
        train_end = int(total * self.train_ratio)
        train_ids = patient_ids[:train_end]
        test_ids = patient_ids[train_end:]
        return {'train': train_ids, 'test': test_ids}

    def copy_files(self, split_data):
        for split, patient_ids in tqdm(split_data.items()):
            for patient_id in patient_ids:
                for file in os.listdir(self.images_dir):
                    if f"_{patient_id}_" in file:
                        shutil.copy(os.path.join(self.images_dir, file), self.dirs[split]['images'])
                        
                for file in os.listdir(self.labels_dir):
                    if f"_{patient_id}." in file:
                        shutil.copy(os.path.join(self.labels_dir, file), self.dirs[split]['labels'])
                logging.info(f'Copied files for patient {patient_id} to {split} set')

    def run(self):
        patient_ids = self.get_patient_ids()
        split_data = self.split_data(patient_ids)
        self.copy_files(split_data)


# Split the dataset into train, test set. (You can modify the code to include validation set)
images_dir = "Path to preprocessed/images folder"
labels_dir = "Path to preprocessed/masks folder"
output_dir = "Path to /workspace/datasets/nnunet_data/nnUNet_raw/Dataset100_BRAIN"


train_ratio = 0.9
test_ratio = 0.1


splitter = DATASET_SPLITTER(images_dir, labels_dir, output_dir, train_ratio, test_ratio)
splitter.run()
