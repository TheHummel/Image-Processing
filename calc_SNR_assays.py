import os
import rawpy
import numpy as np
import pandas as pd
import re
from PIL import Image

from scipy.ndimage import rotate

import matplotlib.pyplot as plt
from tqdm import tqdm

from helpers.helpers import (
    normalize_path,
    load_dngs_from_folder,
    load_images_from_folder,
)

input_dir = ""
input_dir = normalize_path(input_dir)

is_raw = True

data_file = ""
data_file = normalize_path(data_file)
df_data = pd.read_csv(data_file)

df_result = pd.DataFrame(columns=["filename", "row", "well", "signal", "noise", "SNR"])

plot_maske = False

blue_channel = False

output_dir = input_dir + "/SNR_metrics"

if is_raw:
    images, filenames = load_dngs_from_folder(input_dir)
else:
    images, filenames = load_images_from_folder(input_dir)

for i, (image, filename) in tqdm(enumerate(zip(images, filenames)), total=len(images)):
    image_name = filename.split(".")[0]

    # get blue channel
    if blue_channel:
        image = image[:, :, 2]

    df_filename = df_data.loc[df_data["basename"] == image_name]

    # rotate image
    rotation = re.search(r"\d+", df_filename["orientation"].iloc[0])
    if rotation:
        image = rotate(image, int(rotation.group()), reshape=True)

    if df_filename.empty:
        print(f"No data found for {filename}")
        continue

    # create mask with detected wells and background
    height = df_filename["height"].iloc[0]
    width = df_filename["width"].iloc[0]
    mask = np.zeros((height, width), dtype=bool)

    for index, row in df_filename.iterrows():
        sensor_size = row["sensor_size"]
        center_x = row["center_x"]
        center_y = row["center_y"]
        center_well = (center_x, center_y)

        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_well[0]) ** 2 + (y - center_well[1]) ** 2)
        mask |= distance <= sensor_size / 2

        signal = np.mean(image[mask])

        df_result = pd.concat(
            [
                df_result,
                pd.DataFrame(
                    {
                        "filename": [filename],
                        "row": [row["row"]],
                        "well": [row["well"]],
                        "signal": [signal],
                    }
                ),
            ]
        )

    bg_mask = ~mask
    # noise = np.std(image[bg_mask])
    noise = np.std(image)
    df_result.loc[df_result["filename"] == filename, "noise"] = noise
    df_result.loc[df_result["filename"] == filename, "SNR"] = (
        df_result.loc[df_result["filename"] == filename, "signal"] / noise
    )

    if plot_maske:
        plt.imshow(image)
        bg_mask = bg_mask.astype(np.float32)
        plt.imshow(
            np.dstack((bg_mask, np.zeros_like(bg_mask), np.zeros_like(bg_mask))),
            alpha=0.3,
            cmap="Reds",
        )
        plt.show()

        print(bg_mask.shape)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
df_result.to_csv(
    output_dir + "/metrics" + ("_blue_channel" if blue_channel else "") + ".csv",
    index=False,
)
