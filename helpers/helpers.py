import os
import pandas as pd
import numpy as np
import re
import csv
import rawpy
from PIL import Image

import matplotlib.pyplot as plt

from tqdm import tqdm


def load_image(file_path: str, bit_depth: int = 8) -> np.ndarray:
    """
    Load a single image file with the specified bit depth.
    - bit_depth: 8 or 16
    """
    file_path = normalize_path(file_path)
    file_format = "." + (file_path.split(".")[-1]).lower()

    if file_format == ".dng":
        try:
            with rawpy.imread(file_path) as raw:
                if bit_depth == 16:
                    return raw.postprocess(
                        no_auto_bright=False,
                        use_auto_wb=False,
                        use_camera_wb=False,
                        gamma=(1, 1),
                        output_bps=16,
                    ).astype(np.uint16)
                else:
                    return raw.postprocess()
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {e}")

    else:
        try:
            image = Image.open(file_path)

            if bit_depth == 16 and image.mode not in ("I", "I;16"):
                image = image.convert("I")
                return np.array(image, dtype=np.uint16)
            else:
                return np.array(image)
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {e}")


def load_images_from_folder(
    folder: str, file_format: str = None, bit_depth: int = 8
) -> tuple[list, list]:
    """
    Load images from a folder with specified format and bit depth.
    - file_format: if file_format is set, only images with that format will be loaded
    - bit_depth: 8 or 16
    """
    folder = normalize_path(folder)
    images = []
    filenames = []

    if file_format and not file_format.startswith("."):
        file_format = "." + file_format.lower()

    supported_formats = set(Image.registered_extensions().keys())
    supported_formats.add(".dng")

    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        current_format = "." + (filename.split(".")[-1]).lower()

        if (
            file_format
            and current_format != file_format
            or current_format not in supported_formats
        ):
            continue

        file_path = os.path.join(folder, filename)
        image = load_image(file_path, bit_depth)

        images.append(image)
        filenames.append(filename)

    if len(images) == 0:
        print(f"No images of format {file_format} found in {folder}!")
    else:
        print(f"Loaded {len(images)} images from {folder}")

    return images, filenames


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def convert_txt_to_csv(txt_file: str, csv_file: str) -> None:
    """Converts a txt file with the given format to a csv file.

    Args:
      txt_file: Path to the input txt file.
      csv_file: Path to the output csv file.
    """

    data = []
    with open(txt_file, "r") as f:
        for line in f:
            key, value = line.strip().split(": ")
            data.append([key, float(value)])

    df = pd.DataFrame(data, columns=["Parameter", "Value"])
    df = df.set_index("Parameter").T
    df.to_csv(csv_file, index=False)


def convert_metrics_summary_to_csv(txt_file: str, csv_file: str) -> None:
    """Extracts mean and std from metrics summary & converts to a csv file.

    Args:
      txt_file: Path to the input txt file.
      csv_file: Path to the output csv file.
    """

    data = {}
    with open(txt_file, "r") as f:
        for line in f:
            match = re.match(r"(.*): (\d+\.\d+) \+/- (\d+\.\d+)", line.strip())
            if match:
                key, value, std = match.groups()
                data[key.strip()] = [float(value), float(std)]

    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False)


def convert_powermeter_output_to_csv(
    input_file_path: str, output_file_path: str
) -> None:
    data = []

    # Read the input file and extract the data
    with open(input_file_path, "r") as file:
        lines = file.readlines()
        # Skip the header lines (first two lines)
        for line in lines[2:]:
            parts = line.split()
            if len(parts) == 4:
                date = parts[0]
                time = parts[1]
                value = parts[2]
                unit = parts[3]
                # Append the extracted data to the list
                data.append([date, time, value, unit])

    # Write the extracted data to a CSV file
    with open(output_file_path, "w", newline="") as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Date", "Time", "Value", "Unit"])
        # Write the data rows
        writer.writerows(data)


def get_df_from_csv_folder(folder: str) -> pd.DataFrame:
    """Reads all csv files in a folder and returns a DataFrame.

    Args:
      folder: Path to the folder containing csv files.

    Returns:
      DataFrame containing the data from all csv files in the folder.
    """

    dfs = []
    for file in tqdm(os.listdir(folder)):
        if file.endswith(".csv"):
            csv_file = os.path.join(folder, file)
            df = pd.read_csv(csv_file)
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def extract_values_from_SNR_outputs(file_path: str) -> tuple:
    snr = None
    signal = None
    mean_background = None

    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("SNR:"):
                snr = float(line.split(":")[1].strip())
            elif line.startswith("Signal:"):
                signal = float(line.split(":")[1].strip())
            elif line.startswith("Mean (Background):"):
                mean_background = float(line.split(":")[1].strip())

    return snr, signal, mean_background
