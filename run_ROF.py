import os
from PIL import Image
from tqdm import tqdm
import click

from denoising.ROF import ROF_denoising
from metrics.metrics_reliability import metrics_reliability, save_metrics_csv
from helpers.helpers import load_images_from_folder, load_dngs_from_folder
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
    output_dir = input_dir + "/ROF_denoised_" + str(weight).replace(".", "_")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # LOAD IMAGES
    if is_raw:
        images, _ = load_dngs_from_folder(input_dir)
    else:
        images, _ = load_images_from_folder(input_dir)

    center = (center_x, center_y)

    denoised_images = []
    for i, image in tqdm(enumerate(images), desc="Denoising images", total=len(images)):
        denoised_image = ROF_denoising(image, weight=weight)

        denoised_images.append(denoised_image)

        # save image as tiff
        output_path = os.path.join(output_dir, f"denoised_{i + 1}.tiff")

        im = Image.fromarray(denoised_image)
        im.save(output_path)

    # metrics reliability
    mean, std, cv = metrics_reliability(denoised_images, center, radius)

    save_metrics_csv([mean, std, cv], output_dir + "/metrics.csv")


if __name__ == "__main__":
    run_ROF_denoising()
