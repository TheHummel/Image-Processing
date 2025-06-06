import os
from PIL import Image
from tqdm import tqdm
import click
import numpy as np

from denoising.ROF import ROF_denoising
from metrics.metrics_reliability import metrics_reliability, save_metrics_csv
from helpers.helpers import load_images_from_folder
from helpers.CLI_options import (
    input_dir_option,
    is_raw_option,
    center_x_option,
    center_y_option,
    radius_option,
    weight_option,
)


@click.command()
@input_dir_option
@is_raw_option
@center_x_option
@center_y_option
@radius_option
@weight_option
def run_ROF_denoising(
    input_dir: str,
    is_raw: bool,
    center_x: int,
    center_y: int,
    radius: int,
    weight: float,
):
    output_dir = input_dir + "/ROF_denoised_" + str(weight).replace(".", "_") + "_16bit"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # LOAD IMAGES
    file_format = "dng" if is_raw else "tiff"
    images, filenames = load_images_from_folder(
        input_dir, file_format=file_format, bit_depth=16
    )

    center = (center_x, center_y)

    denoised_images = []
    for i, image in tqdm(enumerate(images), desc="Denoising images", total=len(images)):
        denoised_image = ROF_denoising(image, weight=weight)

        denoised_images.append(denoised_image)

        # save image as tiff
        output_path = os.path.join(output_dir, filenames[i])

        im = Image.fromarray(denoised_image.astype(np.uint16), mode="I;16")
        im.save(output_path.replace("dng", "tiff"))

    # metrics reliability
    mean, std, cv = metrics_reliability(denoised_images, center, radius)

    save_metrics_csv([mean, std, cv], output_dir + "/metrics.csv")


if __name__ == "__main__":
    run_ROF_denoising()
