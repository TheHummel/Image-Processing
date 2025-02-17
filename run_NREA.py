import os
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import click

from denoising.NREA import NREA
from metrics.SNR_metrics import calc_SNR
from helpers.helpers import (
    load_images_from_folder_16bit,
    load_dngs_from_folder_16bit,
)
from helpers.CLI_options import (
    input_dir_option,
    is_raw_option,
    center_x_option,
    center_y_option,
    radius_option,
    kernel_option,
    kernel_size_option,
    accumulate_option,
    normalize_option,
)

colormap = cm.get_cmap("tab10")


@click.command()
@input_dir_option
@is_raw_option
@center_x_option
@center_y_option
@radius_option
@kernel_option
@kernel_size_option
@accumulate_option
@normalize_option
def run_NREA(
    input_dir: str,
    is_raw: bool,
    center_x: int,
    center_y: int,
    radius: int,
    kernel: str,
    kernel_size: int,
    accumulate: bool = True,  # true: images 0:i are used, false: only image i is used for i-th iteration
    normalize: bool = True,
):
    # LOAD IMAGES
    center = (center_x, center_y)
    if is_raw:
        images, filenames = load_dngs_from_folder_16bit(input_dir)
    else:
        images, filenames = load_images_from_folder_16bit(input_dir)

    output_dir = (
        input_dir
        + "/NREA"
        + f"_{kernel}_{kernel_size}"
        + ("_accumulated" if accumulate else "_single")
    )
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    n = len(images)
    metrics = np.zeros((n, 3))

    for i in range(n):
        # do NREA with i images
        nrea = NREA(
            images[: i + 1] if accumulate else [images[i]],
            gaussian_blurring=(kernel == "GB"),
            kernel_radius=kernel_size,
        )

        # save as tiff
        output_path = os.path.join(
            output_dir,
            filenames[i].split(".")[0] + ("_normalized" if normalize else "") + ".tiff",
        )
        nrea_normalized = (
            (nrea - np.min(nrea)) / (np.max(nrea) - np.min(nrea))
        ) * 2**16
        nrea = nrea_normalized if normalize else nrea
        im = Image.fromarray(nrea.astype(np.uint16), mode="I;16")
        im.save(output_path)

        # calculate SNR
        snr, signal, noise, _, _ = calc_SNR(
            nrea, center, radius=radius, show_sample_position=False
        )

        metrics[i] = [snr, signal, noise]

    # save metrics
    df_metrics = pd.DataFrame(
        metrics, columns=["SNR", "Signal", "Noise"], index=range(1, n + 1)
    )
    df_metrics.index.name = "#epochs"
    df_metrics.to_csv(
        os.path.join(
            output_dir,
            (
                f"metrics_{kernel}_{kernel_size}"
                + ("_normalized" if normalize else "")
                + ".csv"
            ),
        )
    )

    # plot metrics
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot SNR on the primary y-axis
    ax1.plot(range(1, n + 1), metrics[:, 0], marker="", color=colormap(0), label="SNR")
    ax1.set_xlabel("#images" if accumulate else "image", fontsize=18)
    ax1.set_ylabel("SNR", fontsize=18)
    ax1.tick_params(axis="y")

    ax1.set_ylim(bottom=0)

    # Create a secondary y-axis for Signal and Noise
    ax2 = ax1.twinx()
    ax2.plot(
        range(1, n + 1), metrics[:, 1], marker="", color=colormap(2), label="Signal"
    )
    ax2.plot(
        range(1, n + 1), metrics[:, 2], marker="", color=colormap(3), label="Noise"
    )
    ax2.set_ylabel("Signal, Noise", fontsize=18)
    ax2.tick_params(axis="y")

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="center left")

    output_path = os.path.join(
        output_dir,
        f"metrics_{kernel}_{kernel_size}"
        + ("_normalized" if normalize else "")
        + ".png",
    )
    plt.savefig(output_path)

    # output_path = os.path.join(output_dir, f"metrics_{kernel_radius}.pgf")
    # plt.savefig(output_path)

    plt.show()

    plt.close()


if __name__ == "__main__":
    run_NREA()
