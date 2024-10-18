import os
import rawpy
import numpy as np
import pandas as pd
import re

from scipy.ndimage import rotate

import matplotlib.pyplot as plt
from tqdm import tqdm

from helpers.helpers import normalize_path


input_dir = ""
input_dir = normalize_path(input_dir)

is_raw = True

data_file = ""
data_file = normalize_path(data_file)
df_data = pd.read_csv(data_file)

df_result = pd.DataFrame(columns=["filename", "row", "well", "signal", "noise", "SNR"])

plot_maske = False

weight = 0.9
output_dir = input_dir + "/ROF_denoised_" + str(weight).replace(".", "_")

for filename in tqdm(os.listdir(input_dir)):
    if filename.endswith(".dng"):
        image_name = filename.split(".")[0]

        # load image
        with rawpy.imread(os.path.join(input_dir, filename)) as raw:
            image = raw.postprocess()

        df_filename = df_data.loc[df_data["filename"] == filename]

        # rotate image
        rotation = re.search(r"\d+", df_filename["orientation"].iloc[0])
        if rotation:
            print("Old shape:", image.shape)
            print("Rotating image by", rotation.group(), "degrees")
            image = rotate(image, int(rotation.group()), reshape=True)
            print("New shape:", image.shape)

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
        noise = np.std(image[bg_mask])
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

        # print(df_result)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    # save metrics
    df_result.to_csv(output_dir + "/metrics.csv", index=False)
