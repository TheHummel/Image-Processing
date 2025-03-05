import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import pandas as pd
import click

from metrics.SNR_metrics import calc_SNR

from denoising.image_stacking import mean_stacking, median_stacking
from helpers.helpers import load_images_from_folder
from helpers.CLI_options import (
    input_dir_option,
    is_raw_option,
    center_x_option,
    center_y_option,
    radius_option,
)


@click.command()
@input_dir_option
@is_raw_option
@center_x_option
@center_y_option
@radius_option
def run_image_stacking(
    input_dir: str, is_raw: bool, center_x: int, center_y: int, radius: int
):
    # LOAD IMAGES
    file_format = "dng" if is_raw else "tiff"
    images, _ = load_images_from_folder(
        input_dir, file_format=file_format, bit_depth=16
    )

    output_dir = input_dir + "/image_stacking"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # STACKING
    arithmetic_mean = mean_stacking(images)
    median = median_stacking(images)

    # SNR
    center = (center_x, center_y)

    snr_arithmetic, signal_arithmetic, noise_arithmetic, _, _ = calc_SNR(
        arithmetic_mean, center, radius
    )
    snr_median, signal_median, noise_median, _, _ = calc_SNR(median, center, radius)

    # SAVE METRICS TO CSV
    output_path = os.path.join(output_dir, "SNR_metrics.csv")
    df = pd.DataFrame(
        {
            "SNR": [snr_arithmetic, snr_median],
            "Signal": [signal_arithmetic, signal_median],
            "Noise": [noise_arithmetic, noise_median],
        },
        index=["Arithmetic Mean", "Median"],
    )
    df.to_csv(output_path)

    # SAVE IMAGE AS TIFF
    output_path_arithmetic = os.path.join(output_dir, "arithmetic_mean.tiff")
    arithmetic_mean_uint8 = arithmetic_mean.astype(np.uint8)
    im = Image.fromarray(arithmetic_mean_uint8)
    im.save(output_path_arithmetic)

    output_path_median = os.path.join(output_dir, "median.tiff")
    median_uint8 = median.astype(np.uint8)
    im = Image.fromarray(median_uint8)
    im.save(output_path_median)

    # DISPLAY IMAGES
    plt.figure()
    plt.suptitle("Image Stacking")
    plt.subplot(121)
    plt.imshow(arithmetic_mean_uint8)
    plt.title("Arithmetic Mean")
    plt.subplot(122)
    plt.imshow(median_uint8)
    plt.title("Median")

    plt.show()


if __name__ == "__main__":
    run_image_stacking()
