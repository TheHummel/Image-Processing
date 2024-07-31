import os
import numpy as np
import rawpy
from PIL import Image
from tqdm import tqdm

import matplotlib.pyplot as plt


def calc_SNR(img: np.array, center: (int, int), radius: int) -> float:
    """
    Calculate the Signal-to-Noise Ratio (SNR) of an image.

    Parameters:
    img (np.array): The input image.
    center ((int, int)): The center of the circular region of interest.
    radius (int): The radius of the circular region of interest.

    Returns:
    float: The Signal-to-Noise Ratio (SNR) of the image.
    """
    # Extract the circular region of interest
    y, x = np.ogrid[: img.shape[0], : img.shape[1]]
    mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
    circle = img[mask]

    # plt.imshow(mask)
    # plt.show()

    signal = np.mean(circle)
    # TODO: use small square inside circle to calculate signal

    diameter = 2 * radius
    square_top_left_y = center[1] + radius + 100
    square_top_left_x = center[0] - radius
    square_mask = np.zeros_like(img, dtype=bool)
    square_mask[
        square_top_left_y : square_top_left_y + diameter,
        square_top_left_x : square_top_left_x + diameter,
    ] = True
    bg_square = img[square_mask]

    # plt.imshow(square_mask)
    # plt.show()

    std = np.std(img)
    std_bg = np.std(bg_square)
    mean_bg = np.mean(bg_square)

    snr = signal / mean_bg

    return snr, signal, std, std_bg, mean_bg


# calculating average metrics for single captures
path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/iso12800expo30_8DC_native_camera"
output_path = "NREA/metrics/metrics_single_captures_avg.txt"
center = (1577, 2069)
radius = 102

snr_values = []
signal_values = []
std_values = []
std_bg_values = []
mean_bg_values = []
for filename in tqdm(os.listdir(path)):
    if filename.endswith(".dng"):
        with rawpy.imread(path + "/" + filename) as raw:
            image = raw.postprocess()
            snr, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)
            snr_values.append(snr)
            signal_values.append(signal)
            std_values.append(std)
            std_bg_values.append(std_bg)
            mean_bg_values.append(mean_bg)

SNR = np.mean(snr_values)
signal = np.mean(signal_values)
std = np.mean(std_values)
std_bg = np.mean(std_bg_values)
mean_bg = np.mean(mean_bg_values)

# calculating metrics for NREA output
# setting = "ca_r5"
# output_path = "NREA/metrics/metrics_" + setting + ".txt"
# path = "NREA/images/nrea_with_" + setting + ".tiff"
# image = Image.open(path)
# image = np.array(image)

# SNR, signal, std, std_bg, mean_bg = calc_SNR(image, (1577, 2069), 102)

print(f"SNR: {SNR}")
print(f"Signal: {signal}")
print(f"Standard Deviation: {std}")
print(f"Standard Deviation (Background): {std_bg}")
print(f"Mean (Background): {mean_bg}")

# save results to txt file
with open(output_path, "w") as f:
    f.write(f"SNR: {SNR}\n")
    f.write(f"Signal: {signal}\n")
    f.write(f"Standard Deviation: {std}\n")
    f.write(f"Standard Deviation (Background): {std_bg}\n")
    f.write(f"Mean (Background): {mean_bg}\n")
