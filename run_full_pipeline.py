import os
import click
import pandas as pd

from cropping import crop
from calc_metrics_for_folder import calc_metrics_for_folder
from run_ROF import run_ROF_denoising
from run_NREA import run_NREA

from helpers.CLI_options import (
    input_dir_option,
    format_option,
    center_x_option,
    center_y_option,
    radius_option,
    crop_factor_option,
    kernel_option,
    kernel_size_option,
    accumulate_option,
    normalize_option,
    weight_option,
)


@click.command()
@input_dir_option
@crop_factor_option
@format_option
@center_x_option
@center_y_option
@radius_option
@weight_option
@kernel_option
@kernel_size_option
@accumulate_option
@normalize_option
def full_pipeline(
    input_dir: str,
    crop_factor: int,
    format: str,
    center_x: int,
    center_y: int,
    radius: int,
    kernel: str,
    kernel_size: int,
    accumulate: bool,
    normalize: bool,
    weight: float,
):
    """
    Full pipeline for:
    - crop raw images into squares for each channel
    - for each channel:
        - calc SNR metrics for each image
        - run ROF
        - run NREA for directories / and /ROF
    """

    context = click.get_current_context()

    filenames = crop(
        input_dir=input_dir, is_raw=(format.lower() == "dng"), crop_factor=crop_factor
    )
    cropped_dir = input_dir + "/cropped" + str(crop_factor)

    # list of channels
    channels = [
        f
        for f in os.listdir(cropped_dir)
        if os.path.isdir(os.path.join(cropped_dir, f))
    ]

    # run pipeline for each channel
    for channel in channels:
        channel_dir = os.path.join(cropped_dir, channel)
        rof_dir = channel_dir + f"/ROF_denoised_{str(weight).replace(".", "_")}_16bit"
        nrea_dir_name = (
            "/NREA"
            + f"_{kernel}_{kernel_size}"
            + ("_accumulated" if accumulate else "_single")
        )
        context.invoke(
            run_ROF_denoising,
            input_dir=channel_dir,
            is_raw=False,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            weight=0.9,
        )
        context.invoke(
            run_NREA,
            input_dir=channel_dir,
            is_raw=False,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            kernel=kernel,
            kernel_size=kernel_size,
            accumulate=accumulate,
            normalize=normalize,
        )
        context.invoke(
            run_NREA,
            input_dir=rof_dir,
            is_raw=False,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            kernel=kernel,
            kernel_size=kernel_size,
            accumulate=accumulate,
            normalize=normalize,
        )

        paths = [
            channel_dir,
            rof_dir,
            channel_dir + nrea_dir_name,
            rof_dir + nrea_dir_name,
        ]
        df_col_prefixes = ["RAW_", "ROF_", "NREA_", "NREA_ROF_"]
        df_channel = pd.DataFrame()
        df_channel["image"] = filenames
        for i, path in enumerate(paths):
            df = calc_metrics_for_folder(
                input_dir=path,
                format="tiff",
                center_x=center_x,
                center_y=center_y,
                radius=radius,
            )
            df.columns = [df_col_prefixes[i] + col for col in df.columns]
            df_channel = pd.concat([df_channel, df], axis=1)
        df_channel.to_csv(channel_dir + "/metrics_overview.csv")


if __name__ == "__main__":
    full_pipeline()
