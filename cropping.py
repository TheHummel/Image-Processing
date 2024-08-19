import os
import rawpy
from PIL import Image

input_dir = "C:/Users/janni/Desktop/ETH/BT/Messungen/Huawei P20/lowest/8D_final/images"

output_path = input_dir + "/cropped"
if not os.path.exists(output_path):
    os.makedirs(output_path)

for filename in os.listdir(input_dir):
    if filename.endswith(".dng"):
        with rawpy.imread(input_dir + "/" + filename) as raw:
            image = raw.postprocess()
            square_size = int(image.shape[1] / 2)
            start_x = image.shape[1] // 2 - square_size // 2
            start_y = image.shape[0] // 2 - square_size // 2
            image = image[start_y : start_y + square_size, start_x : start_x + square_size]
            im = Image.fromarray(image)
            im.save(output_path + "/" + filename.replace(".dng", ".tiff"))
