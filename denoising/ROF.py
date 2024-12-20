from skimage.restoration import denoise_tv_chambolle
from skimage.util import img_as_uint, img_as_ubyte
import numpy as np


def ROF_denoising(image: np.ndarray, weight: float, is_raw: bool) -> np.ndarray:
    denoised_image = denoise_tv_chambolle(image, weight=weight, channel_axis=-1)

    if is_raw:
        denoised_image = img_as_uint(denoised_image)
    else:
        denoised_image = img_as_ubyte(denoised_image)

    return denoised_image
