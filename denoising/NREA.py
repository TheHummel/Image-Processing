import cv2
import numpy as np
from tqdm import tqdm


def NREA_transform(
    image: np.ndarray,
    gaussian_blurring: bool = False,
    kernel_radius: int = 50,
) -> np.ndarray:
    global done

    # CONVERT TO GRAYSCALE
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if not gaussian_blurring:
        # CIRCULAR AVERAGING
        kernel_size = 2 * kernel_radius + 1
        y, x = np.ogrid[:kernel_size, :kernel_size]
        kernel_center = (kernel_radius, kernel_radius)
        mask = (x - kernel_center[0]) ** 2 + (
            y - kernel_center[1]
        ) ** 2 <= kernel_radius**2

        lp_filtered = cv2.filter2D(image, -1, mask.astype(np.float32) / mask.sum())

    else:
        # GAUSSIAN BLURRING
        kernel = (2 * kernel_radius + 1, 2 * kernel_radius + 1)
        sigma = kernel_radius / 3
        lp_filtered = cv2.GaussianBlur(image, kernel, sigma)

    # COMPENSATION
    mean = np.mean(lp_filtered)

    nrea = lp_filtered - mean

    return nrea


def NREA(
    images: list[np.ndarray],
    gaussian_blurring: bool,
    kernel_radius: int,
):
    tranformed_images = []
    for image in tqdm(images, desc="Running NREA transform"):
        transformed_image = NREA_transform(image, gaussian_blurring, kernel_radius)
        tranformed_images.append(transformed_image)

    # ACCUMULATION
    accumulated_image = np.sum(tranformed_images, axis=0)

    # NORMALIZATION
    if accumulated_image.min() < 0:
        accumulated_image += abs(accumulated_image.min())

    # accumulated_image = accumulated_image.astype(np.uint16)
    accumulated_image = accumulated_image.astype(np.uint8)

    accumulated_image_normalized = (
        (accumulated_image - accumulated_image.min())
        / (accumulated_image.max() - accumulated_image.min())
        * 255
    )
    accumulated_image_normalized = accumulated_image_normalized.astype(np.uint8)

    return accumulated_image
