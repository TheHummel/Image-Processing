import os
import rawpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from tqdm import tqdm
import pandas as pd
import numpy as np
import re

from metrics.SNR_metrics import calc_SNR


def extract_iso_expo(filename):
    iso_match = re.search(r"iso(\d+)", filename)
    expo_match = re.search(r"expo(\d+)", filename)

    iso = int(iso_match.group(1)) if iso_match else None
    expo = int(expo_match.group(1)) if expo_match else None

    return iso, expo


def plot_metric_vs_settings(
    df_images: pd.DataFrame, metric: str, setting: str = "exposure_time", show_plot: bool = False
) -> None:
    if metric not in df_images.columns:
        raise ValueError(f"Metric {metric} not in dataframe")
    
    if setting not in ["exposure_time", "iso"]:
        raise ValueError(f"Setting {setting} not valid. Choose 'exposure_time' or 'iso'")

    setting_label = "exposure_time" if setting == "iso" else "iso"
    x_label, class_label = ("ISO", "Exposure time (s)") if setting == "iso" else ("Exposure time (s)", "ISO")

    unique_setting_label = df_images.sort_values(setting_label)[setting_label].unique()
    colormap = cm.get_cmap("Blues", len(unique_setting_label))

    for i, sett in enumerate(unique_setting_label):
        df_setting_label = df_images[df_images[setting_label] == sett]
        df_setting_label = df_setting_label.sort_values(setting)
        plt.plot(
            df_setting_label[setting],
            df_setting_label[metric],
            label=f"{class_label} = {sett}",
            color=colormap(i),
        )
    plt.xlabel(x_label, fontsize=18)
    plt.ylabel(metric, fontsize=18)

    if show_plot:
        plt.show()


input_path = ""
phone_name = "Huawei P20"
output_pgf = input_path + "/" + phone_name + "_metrics_complete2.pgf"
output_png = input_path + "/" + phone_name + "_metrics_complete2.png"

df_images = pd.DataFrame(columns=["iso", "exposure_time"])

center = (1450, 2030)   # Huawei P20
# center =(1540, 2080)    # Xiaomi
radius = 80

images = []
for filename in tqdm(os.listdir(input_path), desc="Loading images"):
    if filename.endswith(".dng"):
        with rawpy.imread(os.path.join(input_path, filename)) as raw:
            image = raw.postprocess()
            image = np.rot90(image, 3)
            images.append(image)

    elif filename.endswith(".tiff"):
        image = plt.imread(os.path.join(input_path, filename))
        images.append(image)

    else:
        continue

    iso, expo = extract_iso_expo(filename)

    snr, signal, noise = calc_SNR(image, center, radius, show_sample_position=False)

    df_images = pd.concat(
        [
            df_images,
            pd.DataFrame(
                {
                    "iso": [iso],
                    "exposure_time": [expo],
                    "SNR": [snr],
                    "Signal": [signal],
                    "Noise": [noise],
                }
            ),
        ]
    )

fig = plt.figure(figsize=(15, 10))
fig.suptitle(phone_name, fontsize=24)

setting = "iso"
plt.subplot(231)
plot_metric_vs_settings(df_images, "SNR", setting)
plt.subplot(232)
plot_metric_vs_settings(df_images, "Signal", setting)
plt.subplot(233)
plot_metric_vs_settings(df_images, "Noise", setting)
plt.legend(loc="upper right")

setting = "exposure_time"
plt.subplot(234)
plot_metric_vs_settings(df_images, "SNR", setting)
plt.subplot(235)
plot_metric_vs_settings(df_images, "Signal", setting)
plt.subplot(236)
plot_metric_vs_settings(df_images, "Noise", setting)
plt.legend(loc="upper right")

plt.tight_layout()

plt.savefig(output_pgf)
plt.savefig(output_png)

plt.show()
