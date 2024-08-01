import os
import rawpy
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from tqdm import tqdm

def image_stacking(path_dir: str):
    # LOAD IMAGES
    images = []

    for filename in tqdm(os.listdir(path_dir)):
        if filename.endswith(".dng"):
            with rawpy.imread(os.path.join(path_dir, filename)) as raw:
                image = raw.postprocess()
                images.append(image)

    # STACK IMAGES
    mean_image = np.sum(images, axis=0) / len(images)

    return mean_image


# path = "C:/Users/janni/Desktop/ETH/BT/Messungen/Xiaomi/iso3200_expo30_9DC_native_camera"
# mean_image = image_stacking(path)

# # Normalize the mean image to 0-255 and convert to uint8
# mean_image_normalized = (
#     (mean_image - mean_image.min()) / (mean_image.max() - mean_image.min()) * 255
# )
# mean_image_uint8 = mean_image_normalized.astype(np.uint8)

# # SAVE IMAGE AS TIFF
# output_dir = "C:/Users/janni/Desktop/ETH/BT/code/Image Processing/image_stacking"
# os.makedirs(output_dir, exist_ok=True)
# output_path = os.path.join(output_dir, "mean_image.tiff")
# im = Image.fromarray(mean_image_uint8)
# im.save(output_path)

# print(f"Mean image saved at: {output_path}")

# # DISPLAY IMAGE
# plt.imshow(mean_image_uint8)
# plt.show()
