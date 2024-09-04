from skimage.restoration import denoise_tv_chambolle
from skimage import img_as_ubyte
import numpy as np


def ROF_denoising(image: np.ndarray, weight: float) -> np.ndarray:
    denoised_image = denoise_tv_chambolle(image, weight=weight, channel_axis=-1)

    denoised_image = img_as_ubyte(denoised_image)

    return denoised_image
