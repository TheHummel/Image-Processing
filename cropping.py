import os
from PIL import Image
from tqdm import tqdm
import click
import numpy as np

from helpers.helpers import load_images_from_folder
from helpers.CLI_options import input_dir_option, is_raw_option, crop_factor_option


def crop(input_dir: str, is_raw: bool, crop_factor: int) -> list[str]:
    output_path = input_dir + "/cropped" + str(crop_factor)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_format = "dng" if is_raw else "tiff"
    images, filenames = load_images_from_folder(
        input_dir, file_format=file_format, bit_depth=16
    )

    for i, image in tqdm(enumerate(images), desc="Cropping images", total=len(images)):
        if image.dtype != np.uint16:
            image = image.astype(np.uint16)
        square_size = int(min(image.shape[0], image.shape[1]) / crop_factor)
        start_x = image.shape[1] // 2 - square_size // 2
        start_y = image.shape[0] // 2 - square_size // 2
        image = image[start_y : start_y + square_size, start_x : start_x + square_size]

        if is_raw:
            # iterate over channels and save them separately
            for channel in range(3):
                os.makedirs(output_path + f"/channel_{channel}", exist_ok=True)
                im_channel = image[:, :, channel]
                im = Image.fromarray(im_channel.astype(np.uint16), mode="I;16")
                im.save(
                    output_path + f"/channel_{channel}/cropped_{i + 1}.tiff",
                    format="TIFF",
                )
        else:
            im = Image.fromarray(image, mode="I;16")
            im.save(output_path + f"/cropped_{i + 1}.tiff", format="TIFF")

    return filenames


@click.command()
@input_dir_option
@is_raw_option
@crop_factor_option
def cli_crop(input_dir: str, is_raw: bool, crop_factor: int):
    crop(input_dir, is_raw, crop_factor)


if __name__ == "__main__":
    crop()
