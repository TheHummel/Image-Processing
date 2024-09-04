import numpy as np


def mean_stacking(images: list[np.ndarray]) -> np.ndarray:
    mean_image = np.sum(images, axis=0) / len(images)

    return mean_image


def median_stacking(images: list[np.ndarray]) -> np.ndarray:
    median_image = np.median(images, axis=0)

    return median_image
