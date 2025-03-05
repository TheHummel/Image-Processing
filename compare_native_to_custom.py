import os
import pandas as pd
from pathlib import Path
import click
import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm

from metrics.SNR_metrics import calc_SNR
from helpers.helpers import load_image
from helpers.CLI_options import input_dir_option
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
    df = df[(df["smartphone"] == camera) & (df["iso"] == iso) & (df["expo"] == expot)]

    custom_palette = [CUSTOM_PALETTE[1], CUSTOM_PALETTE[3]]

    fig, ax1 = create_figure()

    dodge = 0.5
    df_long = df.melt(
        id_vars=["smartphone", "app", "iso", "expo"],
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


@click.command()
@input_dir_option
def compare_native_to_custom(input_dir: str) -> pd.DataFrame:
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
    data = pd.DataFrame(
        columns=["smartphone", "app", "iso", "expo", "SNR", "Signal", "Noise"]
    )

    for root, dirs, files in os.walk(input_dir):
        if not files:
            continue

        path_parts = Path(root).parts

        # extract info
        if len(path_parts) >= 4:
            smartphone = path_parts[-3]
            app = path_parts[-2]  # custom or native
            iso_expo = path_parts[-1]  # isoXexpoY

            # Extract X and Y from isoXexpoY (assuming format "isoXexpoY")
            iso = int(iso_expo.split("expo")[0][3:])
            expo = int(iso_expo.split("expo")[1])

            for file in tqdm(
                files,
                desc=f"Processing {smartphone} {app} {iso_expo}",
                total=len(files),
            ):
                img_path = os.path.join(root, file)
                if not img_path.endswith(".dng"):
                    continue

                img = load_image(img_path, bit_depth=16)
                center = CENTERS_NCC[smartphone][app]
                radius = RADII_NCC[smartphone]
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
                                "expo": [expo],
                                "SNR": [snr],
                                "Signal": [signal],
                                "Noise": [noise],
                            }
                        ),
                    ]
                )

    output_path_csv = input_dir + "/SNR_data_16bit.csv"

    data.to_csv(output_path_csv, index=False)

    print(f"Saved csv to {output_path_csv}")

    # plot comparison
    iso = 1600
    expot = 15
    output_path = input_dir + f"custom_vs_native_{smartphone}_iso{iso}_expot{expot}.pdf"
    plot_comparison(data, smartphone, iso, expot, output_path)


if __name__ == "__main__":
    compare_native_to_custom()
