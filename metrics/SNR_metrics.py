import os
import numpy as np

import matplotlib.pyplot as plt


def calc_SNR(
    img: np.ndarray,
    center: tuple[int, int],
    radius: int,
    offset_background: int = None,
    show_sample_position: bool = False,
) -> float:
    """
    Calculate the Signal-to-Noise Ratio (SNR) of an image.

    Parameters:
    img (np.ndarray): The input image.
    center ((int, int)): The center of the circular region of interest.
    radius (int): The radius of the circular region of interest.
    show_sample_position (bool): Whether to show position from where the signal and noise are sampled.

    Returns:
    float: The Signal-to-Noise Ratio (SNR) of the image.
    """
    img = img.astype(np.float64)

    # circular region of interest (ROI) for signal
    y, x = np.ogrid[: img.shape[0], : img.shape[1]]
    circle_mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
    circle = img[circle_mask]

    # outer ROI = inverse of circle + buffer
    offset_background = radius if offset_background is None else offset_background
    y, x = np.ogrid[: img.shape[0], : img.shape[1]]
    bg_mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= (
        radius + offset_background
    ) ** 2
    bg_mask = ~bg_mask
    bg = img[bg_mask]

    if show_sample_position:
        circle_mask = circle_mask.astype(np.float32)
        bg_mask = bg_mask.astype(np.float32)
        plt.imshow(img)
        plt.imshow(
            np.dstack(
                (np.zeros_like(circle_mask), circle_mask, np.zeros_like(circle_mask))
            ),
            alpha=0.3,
            cmap="Greens",
        )
        plt.imshow(
            np.dstack((bg_mask, np.zeros_like(bg_mask), np.zeros_like(bg_mask))),
            alpha=0.3,
            cmap="Reds",
        )
        plt.show()

    mean_roi = np.mean(circle)
    mean_bg = np.mean(bg)

    signal = mean_roi - mean_bg

    noise = np.std(img)

    snr = signal / noise

    return snr, signal, noise, mean_roi, mean_bg


def save_metrics(
    SNR: float,
    signal: float,
    std: float,
    std_bg: float,
    mean_bg: float,
    output_path: str,
) -> None:
    print(f"SNR: {SNR}")
    print(f"Signal: {signal}")
    print(f"Standard Deviation: {std}")
    print(f"Standard Deviation (Background): {std_bg}")
    print(f"Mean (Background): {mean_bg}")

    # save results to txt file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(f"SNR: {SNR}\n")
        f.write(f"Signal: {signal}\n")
        f.write(f"Standard Deviation: {std}\n")
        f.write(f"Standard Deviation (Background): {std_bg}\n")
        f.write(f"Mean (Background): {mean_bg}\n")


def save_metrics_csv(
    SNR: float,
    signal: float,
    noise: float,
    output_path: str,
) -> None:
    # save results to csv file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("SNR,Signal,Noise\n")
        f.write(f"{SNR}, {signal}, {noise}\n")
