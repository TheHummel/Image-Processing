import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import click
from PIL import Image

from denoising.NREA import NREA
from metrics.SNR_metrics import calc_SNR, save_metrics_csv
from helpers.helpers import load_images_from_folder, load_dngs_from_folder
from helpers.CLI_options import (
    input_dir_option,
    is_raw_option,
    center_x_option,
    center_y_option,
    radius_option,
)

colormap = cm.get_cmap("tab20")


def plot_snr_comparison(class_x_data, class_y_data, output_dir):
    r_values_x = [item[0] for item in class_x_data]
    snr_values_x = [item[1] for item in class_x_data]

    r_values_y = [item[0] for item in class_y_data]
    snr_values_y = [item[1] for item in class_y_data]

    plt.figure(figsize=(10, 6))
    plt.plot(
        r_values_x,
        snr_values_x,
        marker="",
        color=colormap(0),
        label=f"Circular Averaging",
    )
    plt.plot(
        r_values_y,
        snr_values_y,
        marker="",
        color=colormap(1),
        label=f"Gaussian Blurring",
    )
    plt.xlabel("kernel radius", fontsize=18)
    plt.ylabel("SNR", fontsize=18)
    plt.legend()
    all_r_values = sorted(set(r_values_x + r_values_y))
    plt.xticks(all_r_values)

    # Save plot
    fig = plt.gcf()
    filename = os.path.join(output_dir, "SNR_Comparison.png")
    fig.savefig(filename, bbox_inches="tight")
    plt.close()


def plot_class_comparison(class_data, class_name, output_dir):
    r_values = [item[0] for item in class_data]
    snr_values = [item[1] for item in class_data]
    signal_values = [item[2] for item in class_data]
    noise_values = [item[3] for item in class_data]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot SNR on the primary y-axis
    ax1.plot(r_values, snr_values, marker="", color=colormap(0), label=f"SNR")
    ax1.set_xlabel("kernel radius", fontsize=18)
    ax1.set_ylabel("SNR", fontsize=18)
    ax1.tick_params(axis="y")

    # secondary y-axis for Signal and Noise
    ax2 = ax1.twinx()
    ax2.plot(
        r_values,
        signal_values,
        marker="",
        color=colormap(4),
        label=f"Signal",
    )
    ax2.plot(
        r_values,
        noise_values,
        marker="",
        color=colormap(6),
        label=f"Noise",
    )
    ax2.set_ylabel("Signal, Noise", fontsize=18)
    ax2.tick_params(axis="y")

    # Combine legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

    ax1.set_xticks(r_values)

    # Save plot
    filename = os.path.join(output_dir, f"{class_name}_Comparison.png")
    fig.savefig(filename, bbox_inches="tight")
    plt.close()


@click.command()
@input_dir_option
@is_raw_option
@center_x_option
@center_y_option
@radius_option
def run_NREA_filter_comparison(
    input_dir: str, is_raw: bool, center_x: int, center_y: int, radius: int
):
    output_dir = input_dir + "/NREA_filter_comparison"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load images
    if is_raw:
        images = load_dngs_from_folder(input_dir)
    else:
        images = load_images_from_folder(input_dir)

    # run NREA for different filters
    kernel_radii = [10, 25, 50, 75, 100, 150, 200]

    center = (center_x, center_y)

    ca_data = []
    gb_data = []

    for kernel_radius in kernel_radii:
        nrea_ca = NREA(images, gaussian_blurring=False, kernel_radius=kernel_radius)
        nrea_gb = NREA(images, gaussian_blurring=True, kernel_radius=kernel_radius)

        snr, signal, noise, _, _ = calc_SNR(nrea_ca, center, radius)
        output_path = os.path.join(
            output_dir, "SNR_metrics_ca_" + str(kernel_radius) + ".csv"
        )
        save_metrics_csv(snr, signal, noise, output_path)
        ca_data.append((kernel_radius, snr, signal, noise))

        snr, signal, noise, _, _ = calc_SNR(nrea_gb, center, radius)
        output_path = os.path.join(
            output_dir, "SNR_metrics_gb_" + str(kernel_radius) + ".csv"
        )
        save_metrics_csv(snr, signal, noise, output_path)
        gb_data.append((kernel_radius, snr, signal, noise))

        # PLOT
        plt.figure
        plt.suptitle("NREA with kernel radius " + str(kernel_radius))
        plt.subplot(121)
        plt.imshow(nrea_ca, cmap="gray")
        plt.title("Circular Averaging")
        plt.subplot(122)
        plt.imshow(nrea_gb, cmap="gray")
        plt.title("Gaussian Blurring")
        plt.show()

        # SAVE NREA AS TIFF
        output_path = os.path.join(
            output_dir, "nrea_ca_" + str(kernel_radius) + ".tiff"
        )
        im = Image.fromarray(nrea_ca)
        im.save(output_path)
        output_path = os.path.join(
            output_dir, "nrea_gb_" + str(kernel_radius) + ".tiff"
        )
        im = Image.fromarray(nrea_gb)
        im.save(output_path)

    # Sort data by r_value
    ca_data.sort(key=lambda x: x[0])
    gb_data.sort(key=lambda x: x[0])

    plot_snr_comparison(ca_data, gb_data, output_dir)

    plot_class_comparison(ca_data, "Circular Averaging", output_dir)

    plot_class_comparison(gb_data, "Gaussian Blurring", output_dir)


if __name__ == "__main__":
    run_NREA_filter_comparison()
