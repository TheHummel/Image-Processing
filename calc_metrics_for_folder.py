import click
import pandas as pd
from tqdm import tqdm

from metrics.SNR_metrics import calc_SNR
from helpers.helpers import load_images_from_folder_16bit, load_dngs_from_folder_16bit
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
    # LOAD IMAGES
    if is_raw:
        images, _ = load_dngs_from_folder_16bit(input_dir)
    else:
        images, _ = load_images_from_folder_16bit(input_dir)

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


if __name__ == "__main__":
    calc_metrics_reliability()
