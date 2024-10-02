import os
import subprocess
from tqdm import tqdm

def grant_read_write_access(folder1, folder2):
    def change_permissions(folder):
        if not os.path.exists(folder):
            print(f"Folder {folder} does not exist.")
            return
        
        for root, dirs, files in tqdm(os.walk(folder), "Granting read and write permissions to all files..."):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    subprocess.run(['chmod', '666', file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to change permissions for {file_path}: {e}")

    change_permissions(folder1)
    change_permissions(folder2)

folder1 = ''
folder2 = ''
grant_read_write_access(folder1, folder2)
