import pandas as pd
from tqdm import tqdm

from helpers.helpers import load_images_from_folder_16bit
from metrics.SNR_metrics import calc_SNR

from settings import *

input_dir = ""

images, filenames = load_images_from_folder_16bit(input_dir)

center = CENTERS["Xiaomi 13 Pro"]["cropped4"]
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
                    "smartphone": ["Xiaomi 13 Pro"],
                    "image": [filenames[i]],
                    "ROI": [mean_roi],
                    "BG": [mean_bg],
                }
            ),
        ]
    )

output_path = input_dir + "/ROI_BG_data.csv"

df.to_csv(output_path, index=False)
