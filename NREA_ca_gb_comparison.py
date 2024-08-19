import os
import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from helpers import extract_values_from_SNR_outputs

colormap = cm.get_cmap("tab20c")


def save_plot_as_image(fig, filename):
    """Save the figure to a file."""
    fig.savefig(filename, bbox_inches="tight")


def plot_snr_comparison(
    class_x_data, class_y_data, class_x_name, class_y_name, output_dir
):
    r_values_x = [item[0] for item in class_x_data]
    snr_values_x = [item[1] for item in class_x_data]

    r_values_y = [item[0] for item in class_y_data]
    snr_values_y = [item[1] for item in class_y_data]

    plt.figure(figsize=(10, 6))
    plt.plot(
        r_values_x,
        snr_values_x,
        marker="o",
        color=colormap(0),
        label=f"{class_x_name}",
    )
    plt.plot(
        r_values_y,
        snr_values_y,
        marker="x",
        color=colormap(1),
        label=f"{class_y_name}",
    )
    plt.xlabel("kernel radius")
    plt.ylabel("SNR")
    # plt.title("SNR Comparison - Class X vs Class Y")
    plt.legend()
    # Set x-axis ticks to only the r values where data exists
    all_r_values = sorted(set(r_values_x + r_values_y))
    plt.xticks(all_r_values)

    # Save plot
    save_plot_as_image(plt.gcf(), os.path.join(output_dir, "SNR_Comparison.png"))
    plt.close()


def plot_class_comparison(class_data, class_name, output_dir):
    r_values = [item[0] for item in class_data]
    snr_values = [item[1] for item in class_data]
    signal_values = [item[2] for item in class_data]
    noise_values = [item[3] for item in class_data]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    class_shift = 0 if class_name == "Circular Averaging" else 1

    # Plot SNR on the primary y-axis
    ax1.plot(
        r_values, snr_values, marker="o", color=colormap(0 + class_shift), label=f"SNR"
    )
    ax1.set_xlabel("kernel radius")
    ax1.set_ylabel("SNR")
    ax1.tick_params(axis="y")

    # Create a secondary y-axis for Signal and Noise
    ax2 = ax1.twinx()
    ax2.plot(
        r_values,
        signal_values,
        marker="o",
        color=colormap(8 + class_shift),
        label=f"Signal",
    )
    ax2.plot(
        r_values,
        noise_values,
        marker="o",
        color=colormap(4 + class_shift),
        label=f"Noise",
    )
    ax2.set_ylabel("Signal, Noise")
    ax2.tick_params(axis="y")

    # Combine legends from both axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

    # plt.title(f"SNR, Signal, and Noise - {class_name}")
    # Set x-axis ticks to only the r values where data exists
    ax1.set_xticks(r_values)

    # Save plot
    save_plot_as_image(fig, os.path.join(output_dir, f"{class_name}_Comparison.png"))
    plt.close()


def main():
    path_dir = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/final/iso3200expo30/17D/NREA/SNR_outputs"
    output_dir = path_dir + "/plots"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    class_x_data = []
    class_y_data = []

    class_x_name = "Circular Averaging"
    class_y_name = "Gaussian Blurring"

    for filename in os.listdir(path_dir):
        if filename.endswith(".txt"):
            match = re.search(r"_(ca|gb)_(\d+)(?:\.|$)", filename)

            if match:
                class_type = match.group(1)
                r_value = int(match.group(2))

                # Extract SNR, Signal, and Noise from the file
                file_path = os.path.join(path_dir, filename)
                snr, signal, noise = extract_values_from_SNR_outputs(file_path)

                if class_type == "ca":
                    class_x_data.append((r_value, snr, signal, noise))
                elif class_type == "gb":
                    class_y_data.append((r_value, snr, signal, noise))

    # Sort data by r_value
    class_x_data.sort(key=lambda x: x[0])
    class_y_data.sort(key=lambda x: x[0]) if class_y_data else None

    plot_snr_comparison(
        class_x_data, class_y_data, class_x_name, class_y_name, output_dir
    )

    if class_x_data:
        plot_class_comparison(class_x_data, class_x_name, output_dir)
    if class_y_data:
        plot_class_comparison(class_y_data, class_y_name, output_dir)


if __name__ == "__main__":
    main()
