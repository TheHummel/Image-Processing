"""
HELPER SCRIPT (Fig. 2c):
Script to read EXIF data from images and organize them based on ISO and exposure time.
Renames files to isoXexpoY_i format and copies them to organized folders.
"""

import shutil
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from collections import defaultdict
import exifread
from tqdm import tqdm


def get_exif_data(image_path):
    """Extract EXIF data from an image file."""
    exif = {}
    try:
        # try exifread first
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f)
            if tags:
                # extract ISO
                if "Image ISOSpeedRatings" in tags:
                    exif["ISO"] = int(str(tags["Image ISOSpeedRatings"]))
                elif "EXIF ISOSpeedRatings" in tags:
                    exif["ISO"] = int(str(tags["EXIF ISOSpeedRatings"]))

                # extract exposure time
                if "Image ExposureTime" in tags:
                    exif["ExposureTime"] = int(str(tags["Image ExposureTime"]))
                elif "EXIF ExposureTime" in tags:
                    exif["ExposureTime"] = int(str(tags["EXIF ExposureTime"]))

                if not exif or "ISO" not in exif or "ExposureTime" not in exif:
                    print(
                        f"Warning: Missing ISO or ExposureTime in EXIF data for {image_path}"
                    )
                    return None

                return exif
    except Exception as e:
        print(f"Error reading EXIF with exifread from {image_path}: {e}")

    # fallback to PIL for standard image formats
    try:
        if image_path.suffix.lower() not in [".dng", ".cr2", ".nef", ".arw"]:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data is not None:
                    exif = {
                        TAGS.get(key, key): value for key, value in exif_data.items()
                    }
                    return exif
    except Exception as e:
        print(f"Error reading EXIF with PIL from {image_path}: {e}")

    return None


def process_images(input_dir, output_dir):
    """Process all images in input directory and organize them."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # create output dir
    output_path.mkdir(parents=True, exist_ok=True)

    # dict to keep track of files for each ISO/exposure combination
    file_counters = defaultdict(int)

    # supported image extensions
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".cr2",
        ".nef",
        ".arw",
        ".dng",
    }

    # get all image files
    image_files = []
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)

    print(f"Found {len(image_files)} image files to process")

    processed_count = 0

    for image_file in tqdm(image_files):
        print(f"Processing: {image_file.name}")

        # get EXIF data
        exif_data = get_exif_data(image_file)

        if not exif_data or "ISO" not in exif_data or "ExposureTime" not in exif_data:
            print(
                f"  -> Skipping {image_file.name}: Missing ISO or ExposureTime in EXIF data"
            )
            continue
        iso = exif_data.get("ISO")
        exposure_time = exif_data.get("ExposureTime")

        # create folder name and path
        folder_name = f"iso{str(iso)}expo{str(exposure_time)}"
        folder_path = output_path / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # increment counter for this setting combination
        file_counters[folder_name] += 1
        counter = file_counters[folder_name]

        # create new filename
        file_extension = image_file.suffix.lower()
        new_filename = (
            f"iso{str(iso)}expo{str(exposure_time)}_{counter}{file_extension}"
        )
        new_file_path = folder_path / new_filename

        # copy the file
        try:
            shutil.copy2(image_file, new_file_path)
            print(f"  -> Copied to {folder_name}/{new_filename}")
            processed_count += 1
        except Exception as e:
            print(f"  -> Error copying {image_file.name}: {e}")

    print(f"\nProcessing complete! Processed {processed_count} images.")
    print(f"Created folders in: {output_path}")


if __name__ == "__main__":
    # input dir to app-level folder containing images
    input_dir = ""
    output_dir = input_dir + "/organized_images"

    process_images(input_dir, output_dir)
