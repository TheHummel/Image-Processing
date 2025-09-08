"""
HELPER SCRIPT (Fig. 2f):
Given a directory with all .dng files, move them into subfolders named series_X where X is the second to last number in the filename
"""

import os
import shutil
from tqdm import tqdm

# input dir containing all .dng files
input_dir = ""
output_base_dir = input_dir

created_folders = set()

for file in tqdm(sorted(os.listdir(input_dir)), desc="Processing images"):
    if not file.endswith(".dng"):
        continue

    try:
        # parse filename e.g. 20250625235400082_CAPP_2Diff_17_09ND_b10_1_15_6.dng
        file_parts = file.split(".")[0].split("_")

        series_number = int(file_parts[-2])

        series_folder_name = f"series_{series_number}"
        series_folder_path = os.path.join(output_base_dir, series_folder_name)

        if series_folder_name not in created_folders:
            os.makedirs(series_folder_path, exist_ok=True)
            created_folders.add(series_folder_name)
            print(f"Created folder: {series_folder_path}")

        # copy the file to the series folder
        source_path = os.path.join(input_dir, file)
        destination_path = os.path.join(series_folder_path, file)

        shutil.copy2(source_path, destination_path)

    except Exception as e:
        print(f"Error processing file {file}: {e}")

print(f"Finished copying files to series folders in: {output_base_dir}")
