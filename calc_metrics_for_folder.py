import click
import pandas as pd
from tqdm import tqdm

from metrics.SNR_metrics import calc_SNR
from helpers.helpers import load_images_from_folder
from helpers.CLI_options import (
    input_dir_option,
    format_option,
    center_x_option,
    center_y_option,
    radius_option,
)


def calc_metrics_for_folder(
    input_dir: str, format: str, center_x: int, center_y: int, radius: int
):
    """Calculate SNR metrics for all images in a folder and save them to a csv file."""

    # LOAD IMAGES
    images, _ = load_images_from_folder(input_dir, file_format=format, bit_depth=16)

    center = (center_x, center_y)

    metrics = []
    for image in tqdm(images, desc="Calculating metrics", total=len(images)):
        snr, signal, noise, _, _ = calc_SNR(
            image, center, radius, show_sample_position=False
        )
        metrics.append([snr, signal, noise])

    # save metrics to csv
    df = pd.DataFrame(metrics, columns=["SNR", "Signal", "Noise"])

    df.to_csv(input_dir + "/all_metrics.csv")

    return df


@click.command()
@input_dir_option
@format_option
@center_x_option
@center_y_option
@radius_option
def cli_calc_metrics_for_folder():
    calc_metrics_for_folder()


if __name__ == "__main__":
    cli_calc_metrics_for_folder()
