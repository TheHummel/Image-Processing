import os
import numpy as np
import matplotlib.pyplot as plt
from skimage.restoration import denoise_tv_chambolle, denoise_bilateral, denoise_wavelet
from PIL import Image
import rawpy
from tqdm import tqdm
from skimage import img_as_ubyte

from calc_SNR import calc_SNR
from helpers import load_images_from_folder, load_dngs_from_folder

input_folder = (
    "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D_final/images"
)
input_folder = "C:/Users/janni/Desktop/ETH/BT/Messungen/Arducam 3MP final/4D/cropped3"
output_folder = input_folder + "/ROF_denoised"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# images = load_dngs_from_folder(input_folder)
images = load_images_from_folder(input_folder)

print(len(images))

for i, image in tqdm(enumerate(images)):
    denoised_image = denoise_tv_chambolle(image, weight=0.5)

    denoised_image = img_as_ubyte(denoised_image)

    # save image as tiff
    output_path = os.path.join(output_folder, f"denoised_{i + 1}.tiff")

    im = Image.fromarray(denoised_image)
    im.save(output_path)

    print(f"Image saved at: {output_path}")


# # Apply ROF denoising (Total Variation denoising)
# for weight in [0.5]:
#     denoised_image = denoise_tv_chambolle(image, weight=weight)

#     # denoised_image_2 = denoise_bilateral(image, sigma_color=0.05, sigma_spatial=15)

#     # denoised_image_3 = denoise_wavelet(image, multichannel=True)

#     snr0, signal0, noise0 = calc_SNR(image, (1440, 2040), radius=80)
#     snr, signal, noise = calc_SNR(denoised_image, (1440, 2040), radius=80)

#     print("SNR (Original Image):", snr0)
#     print("SNR (Denoised Image):", snr)
#     print("Signal (Original Image):", signal0)
#     print("Signal (Denoised Image):", signal*255)
#     print("Noise (Original Image):", noise0)
#     print("Noise (Denoised Image):", noise*255)

# # Plot the images for comparison
# fig, axes = plt.subplots(1, 3, figsize=(15, 5))
# axes[0].imshow(image, cmap="gray")
# axes[0].set_title("Original Image")
# axes[2].imshow(denoised_image, cmap="gray")
# axes[2].set_title("Denoised Image")

# for ax in axes:
#     ax.axis("off")

# plt.show()
