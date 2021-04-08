import json
from pathlib import Path, PureWindowsPath
import glob
import argparse
import sys
import re
import os
import datetime
from tqdm import tqdm

from PIL import Image
import piexif

SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.mp4']
EXIF_EXTENSIONS = ['.jpg', '.jpeg']

if "win32" in sys.platform:
    print("Running on windows.")
    # if on windows, let's try to set the file create time too
    from win32_setctime import setctime


def build_id_map(img_dir: str) -> dict:
    """Function to build a dict mapping ID to image file

    Args:
        img_dir:

    Returns:

    """
    id_map = dict()

    pattern = r"(\d{11})"

    id_re = re.compile(pattern)

    for extension in SUPPORTED_EXTENSIONS:
        if "win32" in sys.platform:
            glob_path = str(PureWindowsPath(img_dir) / PureWindowsPath(f"*{extension}"))
        else:
            glob_path = str(Path(img_dir) / Path(f"*{extension}"))

        for i in tqdm(glob.glob(glob_path)):
            img = Path(i)
            result = id_re.findall(img.name)
            if len(result) == 1:
                id_map[result[0]] = img
            else:
                print(f"Failed to detect flickr ID: {img}")

    return id_map


def apply_exif(id_map: dict, metadata_dir: str) -> None:
    """Function to update create date metadata

    Args:
        id_map:
        metadata_dir:

    Returns:

    """
    if "win32" in sys.platform:
        glob_path = str(PureWindowsPath(metadata_dir) / PureWindowsPath("*.json"))
    else:
        glob_path = str(Path(metadata_dir) / Path("*.json"))

    for m in tqdm(glob.glob(glob_path)):
        with open(m, 'rt') as mf:
            metadata = json.load(mf)

        if id_map.get(metadata['id']):
            filename = id_map.get(metadata['id'])
            _, ext = os.path.splitext(filename)
            if ext in EXIF_EXTENSIONS:
                im = Image.open(filename)
                exif_dict = piexif.load(im.info["exif"])

                # Date format is YYYY:MM:DD HH:MM:SS"
                exif_dict['0th'][piexif.ImageIFD.DateTime] = metadata['date_taken']
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = metadata['date_taken']
                exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = metadata['date_taken']
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, str(filename))

            if "win32" in sys.platform:
                metadata_date = datetime.datetime.strptime(metadata['date_taken'], '%Y-%m-%d %H:%M:%S')
                setctime(str(filename), metadata_date.timestamp())


def update_images(img_dir: str, metadata_dir: str):
    if "win32" in sys.platform:
        print("Starting with Windows features enabled.")
    else:
        print("Starting with Windows features disabled.")

    print("Extracting IDs from image dir...")
    id_map = build_id_map(img_dir)
    print()
    print("Applying exif update to image dir...")
    apply_exif(id_map, metadata_dir)
    print()
    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img-dir', help='Image Directory', type=str)
    parser.add_argument('--metadata-dir', help='Metadata Directory', type=str)
    args = parser.parse_args()

    update_images(args.img_dir, args.metadata_dir)
