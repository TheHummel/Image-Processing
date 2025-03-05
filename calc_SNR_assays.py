import os
import numpy as np
import pandas as pd
import re

from scipy.ndimage import rotate

import matplotlib.pyplot as plt
from tqdm import tqdm

from helpers.helpers import (
    normalize_path,
    load_images_from_folder,
)

input_dir = ""
input_dir = normalize_path(input_dir)

is_raw = True

data_file = ""
data_file = normalize_path(data_file)
df_data = pd.read_csv(data_file)

df_result = pd.DataFrame(columns=["filename", "row", "well", "signal", "noise", "SNR"])

plot_single_well_mask = False
plot_mask = False

blue_channel = False

output_dir = input_dir + "/SNR_metrics"

file_format = "dng" if is_raw else "tiff"
images, filenames = load_images_from_folder(
    input_dir, file_format=file_format, bit_depth=16
)

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

        single_well_mask = distance <= sensor_size / 2
        mask |= single_well_mask

        mean_roi = np.mean(image[single_well_mask])

        df_result = pd.concat(
            [
                df_result,
                pd.DataFrame(
                    {
                        "filename": [filename],
                        "row": [row["row"]],
                        "well": [row["well"]],
                        "mean_roi": [mean_roi],
                    }
                ),
            ]
        )

        if plot_single_well_mask:
            plt.imshow(image)
            mask_show = single_well_mask.astype(np.float32)
            plt.imshow(
                np.dstack(
                    (mask_show, np.zeros_like(mask_show), np.zeros_like(mask_show))
                ),
                cmap="Reds",
            )
            plt.show()

    bg_mask = ~mask
    # noise = np.std(image[bg_mask])
    mean_bg = np.mean(image[bg_mask])
    noise = np.std(image)
    df_result.loc[df_result["filename"] == filename, "signal"] = (
        df_result.loc[df_result["filename"] == filename, "mean_roi"] - mean_bg
    )
    df_result.loc[df_result["filename"] == filename, "noise"] = noise
    df_result.loc[df_result["filename"] == filename, "SNR"] = (
        df_result.loc[df_result["filename"] == filename, "signal"] / noise
    )

    if plot_mask:
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
