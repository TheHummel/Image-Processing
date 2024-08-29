import os
import rawpy
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from tqdm import tqdm

from helpers import load_images_from_folder, load_dngs_from_folder


def arithmetic_stacking(images: list[np.ndarray]) -> np.ndarray:
    # STACK IMAGES
    mean_image = np.sum(images, axis=0) / len(images)

    mean_image_normalized = (
        (mean_image - mean_image.min()) / (mean_image.max() - mean_image.min()) * 255
    )
    mean_image_uint8 = mean_image_normalized.astype(np.uint8)

    return mean_image


def median_stacking(images: list[np.ndarray]) -> np.ndarray:
    # STACK IMAGES
    median_image = np.median(images, axis=0)

    return median_image


path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/final/iso3200expo30/17D"
path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/iso3200expo30_8DC"
input_path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/9D/images"
input_path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D_final/images"

# images = load_images_from_folder(input_path)
images = load_dngs_from_folder(path)


arithmetic_mean = arithmetic_stacking(images)
median = median_stacking(images)


# SAVE IMAGE AS TIFF
output_dir = path + "/image_stacking"
os.makedirs(output_dir, exist_ok=True)

output_path_arithmetic = os.path.join(output_dir, "arithmetic_mean.tiff")
im = Image.fromarray(arithmetic_mean)
im.save(output_path_arithmetic)

output_path_median = os.path.join(output_dir, "median.tiff")
im = Image.fromarray(median)
im.save(output_path_median)

# DISPLAY IMAGES
plt.figure()
plt.suptitle("Image Stacking")
plt.subplot(121)
plt.imshow(arithmetic_mean)
plt.title("Arithmetic Mean")
plt.subplot(122)
plt.imshow(median)
plt.title("Median")
