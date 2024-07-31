import os
from typing import Tuple
import rawpy
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from helpers import plot_cut


done = False


def NREA_transform(
    image: np.array, center: Tuple[int, int], gaussian_blurring: bool = False
):
    global done

    # CONVERT TO GRAYSCALE
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # plot_cut(gray, axis=0, coord=center[1])

    if not gaussian_blurring:
        # CIRCULAR AVERAGING
        kernel_radius = 100
        kernel_size = 2 * kernel_radius + 1
        y, x = np.ogrid[:kernel_size, :kernel_size]
        kernel_center = (kernel_radius, kernel_radius)
        mask = (x - kernel_center[0]) ** 2 + (
            y - kernel_center[1]
        ) ** 2 <= kernel_radius**2

        ca = cv2.filter2D(gray, -1, mask.astype(np.float32) / mask.sum())

    else:
        # GAUSSIAN BLURRING
        kernel = (121, 121)
        sigma = 15.0
        blurred = cv2.GaussianBlur(gray, kernel, sigma)

    plt.subplot(121)
    if not done:
        plot_cut(ca, axis=0, coord=center[1], show=False)
        done = True

    # NORMALIZATION
    # ca = cv2.normalize(ca, None, 0, 255, cv2.NORM_MINMAX)

    # COMPENSATION
    bg_mean = np.mean(ca)

    nrea = (ca - bg_mean) if not gaussian_blurring else (blurred - bg_mean)

    return nrea


def NREA(path_dir, center):
    # LOAD IMAGES
    images = []
    tranformed_images = []
    print("Loading images...")
    for filename in tqdm(os.listdir(path_dir)):
        if filename.endswith(".dng"):
            with rawpy.imread(path_dir + "/" + filename) as raw:
                image = raw.postprocess()
                images.append(image)

    print("Transforming images...")
    for image in tqdm(images):
        # center, radius = find_circle(image)  # TODO: implement find_circle
        transformed_image = NREA_transform(image, center)
        tranformed_images.append(transformed_image)

    # ACCUMULATION
    accumulated_image = np.sum(tranformed_images, axis=0)

    # NORMALIZATION
    if accumulated_image.min() < 0:
        accumulated_image += abs(accumulated_image.min())

    accumulated_image_normalized = (
        (accumulated_image - accumulated_image.min())
        / (accumulated_image.max() - accumulated_image.min())
        * 255
    )
    accumulated_image_normalized = accumulated_image_normalized.astype(np.uint8)

    plt.subplot(122)
    plot_cut(accumulated_image_normalized, axis=0, coord=center[1])

    return accumulated_image_normalized


# calculate NREA for directory of images
path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/iso12800expo30_8DC_native_camera"

center = (1577, 2069)
radius = 102
nrea = NREA(path, center)

# PLOT
plt.figure(figsize=(12, 6))
plt.imshow(nrea)
plt.title("NREA")
plt.show()


# SAVE NREA AS TIFF
output_dir = "C:/Users/janni/Desktop/ETH/BT/code/Image Processing/NREA"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "nrea_with_ca_r100.tiff")
im = Image.fromarray(nrea)
im.save(output_path)
