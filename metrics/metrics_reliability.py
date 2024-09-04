import os
import numpy as np
import pandas as pd

from metrics.SNR_metrics import calc_SNR


def metrics_reliability(
    images: list[np.ndarray], center: tuple[int, int], radius: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    metrics = []

    for image in images:
        snr, signal, noise = calc_SNR(image, center, radius, show_sample_position=False)
        metrics.append([snr, signal, noise])

    mean = np.mean(metrics, axis=0)
    std = np.std(metrics, axis=0)
    cv = std / mean

    return mean, std, cv


def save_metrics_csv(
    metrics: tuple[np.ndarray, np.ndarray, np.ndarray], output_path: str
) -> None:
    df = pd.DataFrame(
        metrics, columns=["SNR", "Signal", "Noise"], index=["mean", "std", "cv"]
    )
    df.to_csv(output_path)
