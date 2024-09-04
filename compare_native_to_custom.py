import os
import numpy as np
import pandas as pd
from pathlib import Path

from tqdm import tqdm

from metrics.SNR_metrics import calc_SNR
from helpers.helpers import load_dng


def get_data(
    root_dir: str, centers: dict, radii: dict[str, int]
) -> pd.DataFrame:
    data = pd.DataFrame(
        columns=["smartphone", "app", "iso", "expo", "snr", "signal", "noise"]
    )

    for root, dirs, files in os.walk(root_dir):
        if not files:
            continue

        path_parts = Path(root).parts

        # extract info
        if len(path_parts) >= 4:
            smartphone = path_parts[-3]
            app = path_parts[-2]  # custom or native
            iso_expo = path_parts[-1]  # isoXexpoY


            # Extract X and Y from isoXexpoY (assuming format "isoXexpoY")
            iso = int(iso_expo.split("expo")[0][3:])
            expo = int(iso_expo.split("expo")[1])

            for file in tqdm(files, desc=f"Processing {smartphone} {app} {iso_expo}", total=len(files)):
                img_path = os.path.join(root, file)
                img = load_dng(img_path)
                center = centers[smartphone][app]
                radius = radii[smartphone]
                snr, signal, noise = calc_SNR(img, center, radius, show_sample_position=False)

                data = pd.concat(
                    [
                        data,
                        pd.DataFrame(
                            {
                                "smartphone": [smartphone],
                                "app": [app],
                                "iso": [iso],
                                "expo": [expo],
                                "snr": [snr],
                                "signal": [signal],
                                "noise": [noise],
                            }
                        ),
                    ]
                )

    return data


input_dir = ""

df = get_data(
    input_dir,
    centers={"Xiaomi": {"native": (1540, 2100), "custom": (2090, 1530)}, "Huawei P20 Pro": {"native": (1450, 1990), "custom": (1980, 1560)}},
    radii={"Xiaomi": 80, "Huawei P20 Pro": 80},
)

print(df)

output_path = input_dir + "/SNR_data.csv"

df.to_csv(output_path, index=False)
print(f"Saved data to {output_path}")
