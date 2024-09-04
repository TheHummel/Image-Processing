import os
import pandas as pd
import numpy as np
import re
import csv
import rawpy
from PIL import Image

import matplotlib.pyplot as plt

from tqdm import tqdm


def load_images_from_folder(folder: str, only_format: str = None) -> list:
    """Loads all images from a folder using PIL converts them to np arrays
    and returns them as a list.

    Args:
      folder: Path to the folder containing images.

    Returns:
      List of loaded images.
    """

    folder = normalize_path(folder)

    images = []
    supported_formats = Image.registered_extensions().keys()
    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        format = "." + (filename.split(".")[-1]).lower()
        if format in supported_formats and (
            only_format is None or format == only_format or format[0:] == only_format
        ):
            image = Image.open(os.path.join(folder, filename))
            if image is None:
                print("Error: Image not loaded correctly")
            image = np.array(image)
            images.append(image)

    print(f"Loaded {len(images)} images from {folder}")

    return images


def load_dngs_from_folder(folder: str) -> list:
    """Loads all dng files from a folder and returns them as a list.

    Args:
      folder: Path to the folder containing dng files.

    Returns:
      List of loaded dng files.
    """

    folder = normalize_path(folder)

    images = []
    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        if filename.endswith(".dng"):
            with rawpy.imread(os.path.join(folder, filename)) as raw:
                image = raw.postprocess()
                images.append(image)

    print(f"Loaded {len(images)} images from {folder}")

    return images


def load_dng(path: str) -> np.ndarray:
    path = normalize_path(path)
    with rawpy.imread(path) as raw:
        image = raw.postprocess()

    return image


def load_tiffs_from_folder(folder: str) -> list:
    """Loads all tiff files from a folder and returns them as a list.

    Args:
      folder: Path to the folder containing tiff files.

    Returns:
      List of loaded tiff files.
    """

    folder = normalize_path(folder)

    images = []
    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        if filename.endswith(".tiff"):
            image = plt.imread(os.path.join(folder, filename))
            images.append(image)

    return images


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
