import numpy as np
from skimage.metrics import structural_similarity as ssim

from SNR_enhancing.image_stacking import image_stacking
import cv2


def image_similarity(img1: np.array, img2: np.array):
    """
    Calculate the difference between two images.

    Parameters:
    img1 (np.array): The first image.
    img2 (np.array): The second image.

    Returns:
    np.array: The difference between the two images.
    """
    # calculate mse
    mse = np.mean((img1 - img2) ** 2)

    # calculate SSIM
    ssim_value = ssim(img1, img2, data_range=img2.max() - img2.min(), channel_axis=2)

    # calculate coefficient of variation
    mean1 = np.mean(img1)
    mean2 = np.mean(img2)
    std1 = np.std(img1)
    std2 = np.std(img2)
    cv1 = std1 / mean1
    cv2 = std2 / mean2
    # make a value out of it

    # calculate contrast to noise ratio
    cnr = (mean1 - mean2) / np.sqrt(std1**2 + std2**2)

    return mse, ssim_value, cv1, cv2, cnr


camera = "Xiaomi"
camera_setting = "iso1600expo15"
path1 = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/compare_native_to_custom/"
    + camera
    + "/custom/"
    + camera_setting
    + "/"
)
path2 = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/compare_native_to_custom/"
    + camera
    + "/native/"
    + camera_setting
    + "/"
)

mean_image1 = image_stacking(path1)
mean_image1 = np.rot90(mean_image1, 3)

mean_image2 = image_stacking(path2)

# blur both images
mean_image1 = cv2.GaussianBlur(mean_image1, (41, 41), 10.0)
mean_image2 = cv2.GaussianBlur(mean_image2, (41, 41), 10.0)

mse, ssim_value, cv1, cv2, cnr = image_similarity(mean_image1, mean_image2)

print(f"MSE: {mse}")
print(f"SSIM: {ssim_value}")
print(f"CV1: {cv1}")
print(f"CV2: {cv2}")
print(f"CNR: {cnr}")

# save metrics to txt file
output_path = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/compare_native_to_custom/"
    + camera
    + "_"
    + camera_setting
    + "_similarity_metrics.txt"
)
with open(output_path, "w") as f:
    f.write(f"MSE: {mse}\n")
    f.write(f"SSIM: {ssim_value}\n")
    f.write(f"CV1: {cv1}\n")
    f.write(f"CV2: {cv2}\n")
    f.write(f"CNR: {cnr}\n")
