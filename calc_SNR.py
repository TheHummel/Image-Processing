import numpy as np
import rawpy
from PIL import Image

import matplotlib.pyplot as plt


def calc_SNR(img: np.array, center: (int, int), radius: int) -> float:
    """
    Calculate the Signal-to-Noise Ratio (SNR) of an image.

    Parameters:
    img (np.array): The input image.
    center ((int, int)): The center of the circular region of interest.
    radius (int): The radius of the circular region of interest.

    Returns:
    float: The Signal-to-Noise Ratio (SNR) of the image.
    """
    # Extract the circular region of interest
    y, x = np.ogrid[: img.shape[0], : img.shape[1]]
    mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
    circle = img[mask]

    plt.imshow(mask)
    plt.show()

    # TODO: use small square inside circle to calculate signal
    signal = np.mean(circle)

    bg = img[~mask]
    std = np.std(img)
    std_bg = np.std(bg)
    mean_bg = np.mean(bg)

    noise = std_bg

    snr = signal / noise

    return snr, signal, std, std_bg, mean_bg


path = "images/xiaomi_max_single.dng"
with rawpy.imread(path) as raw:
    # Convert the raw data to a NumPy array (RGB)
    image = raw.postprocess()
    # image = np.rot90(image, 3)


# path = "image_stacking/xiaomi_max_mean.tiff"
# image = Image.open(path)
# image = np.array(image)

SNR, signal, std, std_bg, mean_bg = calc_SNR(image, (1577, 2069), 102)

print(f"SNR: {SNR}")
print(f"Signal: {signal}")
print(f"Standard Deviation: {std}")
print(f"Standard Deviation (Background): {std_bg}")
print(f"Mean (Background): {mean_bg}")

# save results to txt file
with open("SNR_results.txt", "w") as f:
    f.write(f"SNR: {SNR}\n")
    f.write(f"Signal: {signal}\n")
    f.write(f"Standard Deviation: {std}\n")
    f.write(f"Standard Deviation (Background): {std_bg}\n")
    f.write(f"Mean (Background): {mean_bg}\n")
