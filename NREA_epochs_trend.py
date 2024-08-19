import os
import random
from PIL import Image
import numpy as np
import matplotlib.cm as cm

from NREA import NREA
from calc_SNR import calc_SNR, save_metrics_csv
from helpers import load_dngs_from_folder, load_tiffs_from_folder


colormap = cm.get_cmap("tab20c")

path_dir = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D_final/images"
)
images = load_dngs_from_folder(path_dir)
# images = load_tiffs_from_folder(path_dir)

output_dir = path_dir + "/NREA_epochs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

center = (1540, 2070)  # Xiaomi 13 Pro
center = (1440, 2040)  # Huawei P20
# center = (670, 790)  # cropped Huawei P20
radius = 80

n = len(images)
kernel_radius = 100

# shuffle images
# random.shuffle(images)

metrics = np.zeros((n, 3))

for i in range(n):
    # do NREA with i images
    nrea = NREA(
        images[: i + 1],
        center,
        gaussian_blurring=False,
        kernel_radius=kernel_radius,
    )

    # save as tiff
    output_path = os.path.join(output_dir, f"nrea_{i + 1}.tiff")
    im = Image.fromarray(nrea)
    im.save(output_path)

    # calculate SNR
    snr, signal, noise = calc_SNR(nrea, center, radius=radius)

    # save metrics
    save_metrics_csv(
        snr,
        signal,
        noise,
        output_path.replace(".tiff", "_metrics.csv"),
    )

    metrics[i] = [snr, signal, noise]

# plot metrics
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot SNR on the primary y-axis
ax1.plot(range(1, n + 1), metrics[:, 0], marker="o", color=colormap(0), label="SNR")
ax1.set_xlabel("#images")
ax1.set_ylabel("SNR")
ax1.tick_params(axis="y")

ax1.set_ylim(bottom=0)

# Create a secondary y-axis for Signal and Noise
ax2 = ax1.twinx()
ax2.plot(range(1, n + 1), metrics[:, 1], marker="o", color=colormap(8), label="Signal")
ax2.plot(range(1, n + 1), metrics[:, 2], marker="o", color=colormap(4), label="Noise")
ax2.set_ylabel("Signal, Noise")
ax2.tick_params(axis="y")

# Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right")

output_path = os.path.join(output_dir, f"metrics_{kernel_radius}.png")
plt.savefig(output_path)

plt.show()

plt.close()
