import os
from tqdm import tqdm
from PIL import Image
import numpy as np
import rawpy


def load_images_from_folder(folder: str, only_format: str = None) -> list:
    """Loads all images from a folder using PIL converts them to np arrays
    and returns them as a list.

    Args:
      folder: Path to the folder containing images.

    Returns:
      List of loaded images.
    """

    folder = normalize_path(folder)

    images = []
    filenames = []
    supported_formats = Image.registered_extensions().keys()
    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        format = "." + (filename.split(".")[-1]).lower()
        if format in supported_formats and (
            only_format is None or format == only_format or format[0:] == only_format
        ):
            image = Image.open(os.path.join(folder, filename))
            if image is None:
                print("Error: Image not loaded correctly")
            image = np.array(image)
            images.append(image)
            filenames.append(filename)

    print(f"Loaded {len(images)} images from {folder}")

    return images, filenames


def load_dngs_from_folder(folder: str) -> list:
    """Loads all dng files from a folder and returns them as a list.

    Args:
      folder: Path to the folder containing dng files.

    Returns:
      List of loaded dng files.
    """

    folder = normalize_path(folder)

    images = []
    filenames = []
    for filename in tqdm(os.listdir(folder), desc="Loading images"):
        if filename.endswith(".dng"):
            with rawpy.imread(os.path.join(folder, filename)) as raw:
                image = raw.postprocess()
                images.append(image)
                filenames.append(filename)

    print(f"Loaded {len(images)} images from {folder}")

    return images, filenames


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")
