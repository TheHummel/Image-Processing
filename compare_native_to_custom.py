import os
import pandas as pd
from pathlib import Path
import click
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

from tqdm import tqdm

from metrics.SNR_metrics import calc_SNR
from helpers.helpers import load_image
from helpers.CLI_options import input_dir_option, channel_wise_option, offset_option
from paperplots.helpers.plot import (
    create_figure,
    configure_axes,
    save_plot,
    CUSTOM_PALETTE,
)

from camera_configs import CENTERS_NCC, RADII_NCC


def plot_comparison(
    df: pd.DataFrame, camera: str, iso: int, expot: int, output_path: str
) -> None:
    df = df[(df["smartphone"] == camera) & (df["iso"] == iso) & (df["expot"] == expot)]

    custom_palette = [CUSTOM_PALETTE[1], CUSTOM_PALETTE[3]]

    fig, ax1 = create_figure()

    dodge = 0.5
    df_long = df.melt(
        id_vars=["smartphone", "app", "iso", "expot"],
        value_vars=["SNR", "Signal", "Noise"],
        var_name="metric",
        value_name="value",
    )

    dodge = 0.5

    sns.stripplot(
        data=df_long,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge,
        alpha=0.5,
        ax=ax1,
        palette=custom_palette,
        jitter=False,
    )

    sns.pointplot(
        data=df_long,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge - 0.1,
        join=False,
        ax=ax1,
        palette=custom_palette,
        markers=["_"] * df["app"].nunique(),
        scale=1.5,
    )

    configure_axes(ax1, xlabel="", ylabel="Value (-)")

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[2:], labels[2:], title="App", loc="upper left")
    # ax1.set_ylim(0, 70)

    save_plot(output_path)

    plt.show()


def plot_deviations(
    df: pd.DataFrame, camera: str, iso: int, expot: int, output_path: str
):
    df = df[(df["smartphone"] == camera) & (df["iso"] == iso) & (df["expot"] == expot)]

    custom_palette = [CUSTOM_PALETTE[1], CUSTOM_PALETTE[3]]

    fig, ax1 = create_figure()
    ax2 = ax1.twinx()

    # Create figure
    custom_palette = [CUSTOM_PALETTE[1], CUSTOM_PALETTE[3]]

    dodge = 0.5

    snr_df = df.copy()
    signal_noise_df = df.copy()

    # center around minimum means
    app_means = df.groupby("app")[["SNR", "Signal", "Noise"]].mean()
    min_means = app_means.min()
    for metric in ["SNR"]:
        min_value = min_means[metric]
        snr_df[metric] -= min_value

    for metric in ["Signal", "Noise"]:
        min_value = min_means[metric]
        signal_noise_df[metric] -= min_value

    # melt separately
    snr_data = pd.melt(
        snr_df,
        id_vars=["smartphone", "app", "iso", "expot"],
        value_vars=["SNR"],
        var_name="metric",
        value_name="value",
    )

    signal_noise_data = pd.melt(
        signal_noise_df,
        id_vars=["smartphone", "app", "iso", "expot"],
        value_vars=["Signal", "Noise"],
        var_name="metric",
        value_name="value",
    )

    # scale Signal/Noise data by 2^16
    signal_noise_data["value"] = signal_noise_data["value"] / (2**16)

    # plot Signal and Noise
    sns.stripplot(
        data=signal_noise_data,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge,
        alpha=0.5,
        ax=ax1,
        palette=custom_palette,
        jitter=False,
    )

    sns.pointplot(
        data=signal_noise_data,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge - 0.1,
        join=False,
        ax=ax1,
        palette=custom_palette,
        markers=["_"] * df["app"].nunique(),
        scale=1.5,
    )

    # plot SNR
    sns.stripplot(
        data=snr_data,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge,
        alpha=0.5,
        ax=ax2,
        palette=custom_palette,
        jitter=False,
    )

    sns.pointplot(
        data=snr_data,
        x="metric",
        y="value",
        hue="app",
        dodge=dodge - 0.1,
        join=False,
        ax=ax2,
        palette=custom_palette,
        markers=["_"] * df["app"].nunique(),
        scale=1.5,
    )

    configure_axes(
        ax1,
        xlabel="",
        ylabel="Signal/Noise (scaled to 2^16)",
    )
    ax2.set_ylabel("SNR (raw)")

    configure_axes(
        ax1,
        xlabel="",
        ylabel="Signal/Noise (scaled to 2^16)",
    )
    ax2.set_ylabel("SNR (raw)")

    # align zero lines
    ax1.axhline(y=0, color="gray", linestyle="--", alpha=0.7)
    line2 = ax2.axhline(y=0, color="gray", linestyle="--", alpha=0.7)
    line2.set_transform(
        transforms.blended_transform_factory(ax2.transData, ax1.transAxes)
    )

    # legend
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles[2:], labels[2:], title="App", loc="upper left")
    ax2.legend().remove()

    plt.tight_layout()

    # Save plot
    plt.savefig(output_path)
    plt.show()
    plt.close()


@click.command()
@input_dir_option
@channel_wise_option
@offset_option
def compare_native_to_custom(
    input_dir: str, channel_wise: bool, offset: int
) -> pd.DataFrame:
    """
    Calculate SNR metrics for all images in a set of ISO and exposure time settings for both custom and native camera apps.

    Images are expected in the following folder structure:
    - input_dir: Root folder for a specific smartphone.
    - custom: Subfolder containing images taken with the custom camera app.
    - native: Subfolder containing images taken with the native camera app.
        - Each of these subfolders (custom and native) contains subfolders named in the format isoXexpoY,
        where X represents the ISO value and Y represents the exposure time.
        - Each isoXexpoY subfolder contains the images taken at the corresponding ISO and exposure time setting.

    """
    if channel_wise:
        channel_data = []
        for channel in range(3):
            channel_data.append(
                pd.DataFrame(
                    columns=[
                        "smartphone",
                        "app",
                        "iso",
                        "expot",
                        "SNR",
                        "Signal",
                        "Noise",
                    ]
                )
            )
    else:
        data = pd.DataFrame(
            columns=["smartphone", "app", "iso", "expot", "SNR", "Signal", "Noise"]
        )

    iso_expot_pairs = set()

    for root, dirs, files in os.walk(input_dir):
        if not files:
            continue

        path_parts = Path(root).parts

        # extract info
        if len(path_parts) >= 4:
            smartphone = path_parts[-3]
            app = path_parts[-2]  # custom or native
            iso_expot = path_parts[-1]  # isoXexpoY

            # Extract X and Y from isoXexpoY (assuming format "isoXexpoY")
            iso = int(iso_expot.split("expo")[0][3:])
            expot = int(iso_expot.split("expo")[1])
            iso_expot_pairs.add((iso, expot))

            center = CENTERS_NCC[smartphone][app]
            radius = RADII_NCC[smartphone]

            for file in tqdm(
                files,
                desc=f"Processing {smartphone} {app} {iso_expot}",
                total=len(files),
            ):
                img_path = os.path.join(root, file)
                if not img_path.endswith(".dng"):
                    continue

                img = load_image(img_path, bit_depth=16)

                if channel_wise:
                    # iterate over channels
                    for channel in range(3):
                        img_channel = img[:, :, channel]

                        snr, signal, noise, _, _ = calc_SNR(
                            img_channel,
                            center,
                            radius,
                            offset_background=offset,
                            show_sample_position=False,
                        )

                        channel_data[channel] = pd.concat(
                            [
                                channel_data[channel],
                                pd.DataFrame(
                                    {
                                        "smartphone": [smartphone],
                                        "app": [app],
                                        "iso": [iso],
                                        "expot": [expot],
                                        "SNR": [snr],
                                        "Signal": [signal],
                                        "Noise": [noise],
                                    }
                                ),
                            ]
                        )

                else:
                    snr, signal, noise, _, _ = calc_SNR(
                        img, center, radius, show_sample_position=False
                    )

                    data = pd.concat(
                        [
                            data,
                            pd.DataFrame(
                                {
                                    "smartphone": [smartphone],
                                    "app": [app],
                                    "iso": [iso],
                                    "expot": [expot],
                                    "SNR": [snr],
                                    "Signal": [signal],
                                    "Noise": [noise],
                                }
                            ),
                        ]
                    )

    if (channel_wise and not any(channel_data[0].any())) or (
        not channel_wise and not any(data.any())
    ):
        print("No data collected, check input directory.")
        return

    if channel_wise:
        for channel in range(3):
            output_folder = f"{input_dir}/channel{channel}"
            os.makedirs(output_folder, exist_ok=True)

            output_path_csv = f"{output_folder}/SNR_data_16bit.csv"
            channel_data[channel].to_csv(output_path_csv, index=False)
            print(f"Saved csv to {output_path_csv}")

            # plot comparison
            plot_comparison_folder = f"{output_folder}/plot_comparison"
            os.makedirs(plot_comparison_folder, exist_ok=True)

            for iso, expot in iso_expot_pairs:
                output_path = (
                    plot_comparison_folder
                    + f"/custom_vs_native_{smartphone}_iso{iso}_expot{expot}_channel{channel}.pdf"
                )
                plot_comparison(
                    channel_data[channel], smartphone, iso, expot, output_path
                )

            # plot deviations
            plot_deviations_folder = f"{output_folder}/plot_deviations"
            os.makedirs(plot_deviations_folder, exist_ok=True)

            for iso, expot in iso_expot_pairs:
                output_path = (
                    plot_deviations_folder
                    + f"/deviations_custom_vs_native_{smartphone}_iso{iso}_expot{expot}_channel{channel}.pdf"
                )
                plot_deviations(
                    channel_data[channel], smartphone, iso, expot, output_path
                )

    else:
        output_path_csv = input_dir + "/SNR_data_16bit.csv"
        data.to_csv(output_path_csv, index=False)
        print(f"Saved csv to {output_path_csv}")

        # plot comparison
        for iso, expot in iso_expot_pairs:
            output_path = (
                input_dir + f"/custom_vs_native_{smartphone}_iso{iso}_expot{expot}.pdf"
            )
            plot_comparison(data, smartphone, iso, expot, output_path)


if __name__ == "__main__":
    compare_native_to_custom()
