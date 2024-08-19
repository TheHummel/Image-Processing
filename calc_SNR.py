import os
from typing import Tuple
import numpy as np
import rawpy
from PIL import Image
from tqdm import tqdm

import matplotlib.pyplot as plt


def calc_SNR(img: np.array, center: Tuple[int, int], radius: int) -> float:
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
    square_top_left_y = center[1] + radius + 300
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

    noise = np.mean(bg_square)

    snr = signal / noise

    return snr, signal, noise  # , std, std_bg


def save_metrics(
    SNR: float,
    signal: float,
    std: float,
    std_bg: float,
    mean_bg: float,
    output_path: str,
) -> None:
    print(f"SNR: {SNR}")
    print(f"Signal: {signal}")
    print(f"Standard Deviation: {std}")
    print(f"Standard Deviation (Background): {std_bg}")
    print(f"Mean (Background): {mean_bg}")

    # save results to txt file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(f"SNR: {SNR}\n")
        f.write(f"Signal: {signal}\n")
        f.write(f"Standard Deviation: {std}\n")
        f.write(f"Standard Deviation (Background): {std_bg}\n")
        f.write(f"Mean (Background): {mean_bg}\n")


def save_metrics_csv(
    SNR: float,
    signal: float,
    noise: float,
    output_path: str,
) -> None:
    # save results to csv file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("SNR, Signal, Noise\n")
        f.write(f"{SNR}, {signal}, {noise}\n")


# # calculating AVERAGE metrics for a folder of single captures
# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/iso12800expo30_8DC_native_camera"
# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D/images"
# output_path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D/metrics_single_captures_avg.txt"
# center = (1577, 2069)
# center = (1440, 2040)  # Huawei P20
# radius = 80

# snr_values = []
# signal_values = []
# std_values = []
# std_bg_values = []
# mean_bg_values = []
# print("Loading images...")
# for filename in tqdm(os.listdir(path)):
#     if filename.endswith(".dng"):
#         with rawpy.imread(path + "/" + filename) as raw:
#             image = raw.postprocess()
#             snr, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)
#             snr_values.append(snr)
#             signal_values.append(signal)
#             std_values.append(std)
#             std_bg_values.append(std_bg)
#             mean_bg_values.append(mean_bg)

# SNR = np.mean(snr_values)
# signal = np.mean(signal_values)
# std = np.mean(std_values)
# std_bg = np.mean(std_bg_values)
# mean_bg = np.mean(mean_bg_values)

# save_metrics(SNR, signal, std, std_bg, mean_bg, output_path)

# # calculating metrics for a folder of single captures
# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/12D"
# output_path = (
#     "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/12D/SNR_outputs"
# )

# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/final/iso3200expo30/17D/NREA"
# output_path = path + "/SNR_outputs"

# center = (1440, 2070)
# center = (1410, 2050)  # Huawei P60 Pro 9D
# # center = (1450, 1080)  # Huawei P60 Pro 8DC
# center = (1540, 2070)  # Xiaomi 13 Pro
# radius = 80

# SNR_values = []
# signal_values = []
# std_values = []
# std_bg_values = []
# mean_bg_values = []
# for filename in tqdm(os.listdir(path)):
#     if filename.endswith(".dng"):
#         with rawpy.imread(path + "/" + filename) as raw:
#             image = raw.postprocess()
#             # image = np.rot90(image, 3)
#             snr, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)
#             save_metrics(
#                 snr, signal, std, std_bg, mean_bg, output_path + "/" + filename + ".txt"
#             )

#             SNR_values.append(snr)
#             signal_values.append(signal)
#             std_values.append(std)
#             std_bg_values.append(std_bg)
#             mean_bg_values.append(mean_bg)

#     elif filename.endswith(".tiff"):
#         image = Image.open(path + "/" + filename)
#         image = np.array(image)
#         snr, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)
#         save_metrics(
#             snr, signal, std, std_bg, mean_bg, output_path + "/" + filename + ".txt"
#         )

#         SNR_values.append(snr)
#         signal_values.append(signal)
#         std_values.append(std)
#         std_bg_values.append(std_bg)
#         mean_bg_values.append(mean_bg)


# # SNR = np.mean(SNR_values)
# # SNR_std = np.std(SNR_values)
# # signal = np.mean(signal_values)
# # signal_std = np.std(signal_values)
# # std = np.mean(std_values)
# # std_std = np.std(std_values)
# # std_bg = np.mean(std_bg_values)
# # std_bg_std = np.std(std_bg_values)
# # mean_bg = np.mean(mean_bg_values)
# # mean_bg_std = np.std(mean_bg_values)

# # os.makedirs(output_path, exist_ok=True)

# # with open(output_path + "/metrics_summary.txt", "w") as f:
# #     f.write(f"SNR: {SNR} +/- {SNR_std}\n")
# #     f.write(f"Signal: {signal} +/- {signal_std}\n")
# #     f.write(f"Standard Deviation: {std} +/- {std_std}\n")
# #     f.write(f"Standard Deviation (Background): {std_bg} +/- {std_bg_std}\n")
# #     f.write(f"Mean (Background): {mean_bg} +/- {mean_bg_std}\n")


# # # calculating metrics single capture (tiff)
# setting = "ca_r5"
# output_path = "NREA/metrics/metrics_" + setting + ".txt"
# path = "NREA/images/nrea_with_" + setting + ".tiff"
# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/9D/images/image_stacking/mean_image.tiff"
# output_path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/9D/images/image_stacking/metrics.txt"
# image = Image.open(path)
# image = np.array(image)

# center = (1400, 2060)
# center = (1440, 2040)  # Huawei P20
# radius = 80
# SNR, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)

# save_metrics(SNR, signal, std, std_bg, mean_bg, output_path)

# # calclulating metrics for single capture (dng)
# path = "images/test.dng"
# output_path = "metrics/test.txt"

# os.makedirs(os.path.dirname(output_path), exist_ok=True)

# center = (1440, 2060)  # Huawei P60 Pro
# center = (1440, 2040)  # Huawei P20
# radius = 80

# with rawpy.imread(path) as raw:
#     image = raw.postprocess()
#     SNR, signal, std, std_bg, mean_bg = calc_SNR(image, center, radius)
#     save_metrics(SNR, signal, std, std_bg, mean_bg, output_path)
