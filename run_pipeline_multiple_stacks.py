import os
import click

from tqdm import tqdm
from natsort import natsorted

from run_full_pipeline import full_pipeline
from helpers.CLI_options import (
    input_dir_option,
    format_option,
    center_x_option,
    center_y_option,
    radius_option,
    offset_option,
    crop_factor_option,
    channel_wise_save_option,
    kernel_option,
    kernel_size_option,
    accumulate_option,
    normalize_option,
    weight_option,
)


@click.command()
@input_dir_option
@crop_factor_option
@channel_wise_save_option
@format_option
@center_x_option
@center_y_option
@radius_option
@offset_option
@weight_option
@kernel_option
@kernel_size_option
@accumulate_option
@normalize_option
def run_pipeline_multiple_stacks(
    input_dir: str,
    crop_factor: int,
    channel_wise_save: bool,
    format: str,
    center_x: int,
    center_y: int,
    radius: int,
    offset: int,
    kernel: str,
    kernel_size: int,
    accumulate: bool,
    normalize: bool,
    weight: float,
):
    """
    Run the full pipeline on multiple series folders in a given input directory.
    Each series folder should contain the raw images for one series.
    """
    series_dirs = []

    for dirname in os.listdir(input_dir):
        dir_path = os.path.join(input_dir, dirname)
        if os.path.isdir(dir_path):
            series_dirs.append(dir_path)

    context = click.get_current_context()

    series_dirs = natsorted(series_dirs, key=lambda x: os.path.basename(x))

    for dirname in series_dirs:
        print(f"Contains: {dirname}")

    for dirname in tqdm(series_dirs, desc=f"Running NREA on series {dirname}"):

        context.invoke(
            full_pipeline,
            input_dir=dirname,
            crop_factor=crop_factor,
            channel_wise_save=channel_wise_save,
            format=format,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            offset=offset,
            kernel=kernel,
            kernel_size=kernel_size,
            accumulate=accumulate,
            normalize=normalize,
            weight=weight,
        )


if __name__ == "__main__":
    run_pipeline_multiple_stacks()
