import os
import click

from metrics.metrics_reliability import metrics_reliability, save_metrics_csv
from helpers.helpers import load_images_from_folder, load_dngs_from_folder
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
def calc_metrics_reliability(
    input_dir: str, is_raw: bool, center_x: int, center_y: int, radius: int
):
    output_dir = input_dir + "/metrics_reliability"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # LOAD IMAGES
    if is_raw:
        images, _ = load_dngs_from_folder(input_dir)
    else:
        images, _ = load_images_from_folder(input_dir)

    center = (center_x, center_y)

    # metrics reliability
    mean, std, cv = metrics_reliability(images, center, radius)

    save_metrics_csv([mean, std, cv], output_dir + "/metrics_reliability.csv")


if __name__ == "__main__":
    calc_metrics_reliability()
