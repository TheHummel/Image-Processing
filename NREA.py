import os
from typing import Tuple
import rawpy
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from plot.plot_cut import plot_cut


done = False


def NREA_transform(
    image: np.array,
    center: Tuple[int, int],
    gaussian_blurring: bool = False,
    kernel_radius: int = 50,
):
    global done

    # CONVERT TO GRAYSCALE
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if not done:
        plot_cut(gray, axis=0, coord=center[1])

    if not gaussian_blurring:
        # CIRCULAR AVERAGING
        kernel_size = 2 * kernel_radius + 1
        y, x = np.ogrid[:kernel_size, :kernel_size]
        kernel_center = (kernel_radius, kernel_radius)
        mask = (x - kernel_center[0]) ** 2 + (
            y - kernel_center[1]
        ) ** 2 <= kernel_radius**2

        lp_filtered = cv2.filter2D(gray, -1, mask.astype(np.float32) / mask.sum())

    else:
        # GAUSSIAN BLURRING
        kernel = (2 * kernel_radius + 1, 2 * kernel_radius + 1)
        sigma = kernel_radius / 3
        lp_filtered = cv2.GaussianBlur(gray, kernel, sigma)

    # plt.subplot(121)
    if not done:
        plt.subplot(121)
        plot_cut(lp_filtered, axis=0, coord=center[1], show=False)

    # NORMALIZATION
    # ca = cv2.normalize(lp_filtered, None, 0, 255, cv2.NORM_MINMAX)

    # COMPENSATION
    bg_mean = np.mean(lp_filtered)

    nrea = lp_filtered - bg_mean

    return nrea


def NREA(
    images: list[np.array],
    center: Tuple[int, int],
    gaussian_blurring: bool,
    kernel_radius: int,
):
    tranformed_images = []
    for image in tqdm(images, desc="Running NREA transform"):
        transformed_image = NREA_transform(
            image, center, gaussian_blurring, kernel_radius
        )
        tranformed_images.append(transformed_image)

    # ACCUMULATION
    accumulated_image = np.sum(tranformed_images, axis=0)

    # NORMALIZATION
    if accumulated_image.min() < 0:
        accumulated_image += abs(accumulated_image.min())

    # accumulated_image_normalized = (
    #     (accumulated_image - accumulated_image.min())
    #     / (accumulated_image.max() - accumulated_image.min())
    #     * 255
    # )
    # accumulated_image_normalized = accumulated_image_normalized.astype(np.uint8)

    # plt.subplot(122)
    plot_cut(accumulated_image, axis=0, coord=center[1])

    return accumulated_image


# # CALCULATE NREA FOR A FOLDER OF IMAGES
# path_dir = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/final/iso3200expo30/17D"

# print("Loading images...")
# images = []
# for filename in tqdm(os.listdir(path_dir)):
#     if filename.endswith(".dng"):
#         with rawpy.imread(path_dir + "/" + filename) as raw:
#             image = raw.postprocess()
#             images.append(image)

# # settings
# center = (1540, 2070)
# center = (1410, 2070)
# center = (1440, 2040)  # Huawei P20

# gaussian_blurring = True
# kernel_radii = [10, 25, 50, 100, 150, 200]

# for kernel_radius in kernel_radii:
#     nrea_ca = NREA(images, center, not gaussian_blurring, kernel_radius)
#     nrea_gb = NREA(images, center, gaussian_blurring, kernel_radius)

#     # PLOT
#     plt.figure
#     plt.suptitle("NREA with kernel radius " + str(kernel_radius))
#     plt.subplot(121)
#     plt.imshow(nrea_ca, cmap="gray")
#     plt.title("Circular Averaging")
#     plt.subplot(122)
#     plt.imshow(nrea_gb, cmap="gray")
#     plt.title("Gaussian Blurring")
#     plt.show()

#     # SAVE NREA AS TIFF
#     output_dir = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P60 Pro/final/12D/NREA"
#     output_dir = (
#         "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/9D/images/NREA"
#     )
#     output_dir = path_dir + "/NREA"
#     os.makedirs(output_dir, exist_ok=True)
#     output_path = os.path.join(output_dir, "nrea_ca_" + str(kernel_radius) + ".tiff")
#     im = Image.fromarray(nrea_ca)
#     im.save(output_path)
#     output_path = os.path.join(output_dir, "nrea_gb_" + str(kernel_radius) + ".tiff")
#     im = Image.fromarray(nrea_gb)
#     im.save(output_path)
