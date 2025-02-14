import os
from PIL import Image
from tqdm import tqdm
import click
import numpy as np

from helpers.helpers import load_images_from_folder, load_dngs_from_folder_16bit
from helpers.CLI_options import input_dir_option, is_raw_option, crop_factor_option


@click.command()
@input_dir_option
@is_raw_option
@crop_factor_option
def crop(input_dir: str, is_raw: bool, crop_factor: int):
    output_path = input_dir + "/cropped" + str(crop_factor)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if is_raw:
        images, _ = load_dngs_from_folder_16bit(input_dir)
    else:
        images, _ = load_images_from_folder(input_dir)

    for i, image in tqdm(enumerate(images), desc="Cropping images", total=len(images)):
        if image.dtype != np.uint16:
            image = image.astype(np.uint16)
        square_size = int(min(image.shape[0], image.shape[1]) / crop_factor)
        start_x = image.shape[1] // 2 - square_size // 2
        start_y = image.shape[0] // 2 - square_size // 2
        image = image[start_y : start_y + square_size, start_x : start_x + square_size]
        if is_raw:
            im = Image.fromarray(
                image[:, :, 2].astype(np.uint16), mode="I;16"
            )  # only uses blue channel
        else:
            im = Image.fromarray(image, mode="I;16")

        im.save(output_path + f"/cropped_{i + 1}.tiff", format="TIFF")


if __name__ == "__main__":
    crop()
