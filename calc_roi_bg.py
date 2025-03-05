import pandas as pd
from tqdm import tqdm

from helpers.helpers import load_images_from_folder
from metrics.SNR_metrics import calc_SNR

from camera_configs import *

input_dir = ""

file_format = "tiff"
images, filenames = load_images_from_folder(
    input_dir, file_format=file_format, bit_depth=16
)

phone = "Huawei P20"
center = CENTERS[phone]["cropped2"]
radius = RADII["Smartphone"]

df = pd.DataFrame(columns=["smartphone", "image", "ROI", "BG"])

for i, image in tqdm(enumerate(images), total=len(images)):
    _, _, _, mean_roi, mean_bg = calc_SNR(
        image, center, radius, show_sample_position=False
    )

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                {
                    "smartphone": [phone],
                    "image": [filenames[i]],
                    "ROI": [mean_roi],
                    "BG": [mean_bg],
                }
            ),
        ]
    )

output_path = input_dir + "/ROI_BG_data.csv"

df.to_csv(output_path, index=False)
