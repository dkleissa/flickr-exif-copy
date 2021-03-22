import json
from pathlib import Path, PureWindowsPath
import glob
import argparse
import sys
import re
import datetime
from tqdm import tqdm

from PIL import Image
import piexif

if "win" in sys.platform:
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

    if "win" in sys.platform:
        glob_path = str(Path(img_dir) / Path("*.jpg"))
    else:
        glob_path = str(PureWindowsPath(img_dir) / PureWindowsPath("*.jpg"))

    for i in tqdm(glob.glob(glob_path)):
        img = Path(i)
        result = id_re.findall(img.name)
        if len(result) == 1:
            id_map[result[0]] = img
        else:
            print(f"Failed to detect flickr ID: {img}")

    return id_map


def apply_exif(id_map: dict, metadata_dir: str, fields: list) -> None:
    """

    Args:
        id_map:
        metadata_dir:
        fields:

    Returns:

    """
    if "win" in sys.platform:
        glob_path = str(Path(metadata_dir) / Path("*.json"))
    else:
        glob_path = str(PureWindowsPath(metadata_dir) / PureWindowsPath("*.json"))

    for m in tqdm(glob.glob(glob_path)):
        with open(m, 'rt') as mf:
            metadata = json.load(mf)

        if id_map.get(metadata['id']):
            filename = id_map.get(metadata['id'])
            im = Image.open(filename)
            exif_dict = piexif.load(im.info["exif"])

            #exif_bytes = piexif.dump(exif_dict)
            #im.save(filename, exif=exif_bytes)

            # Date format is YYYY:MM:DD HH:MM:SS"
            #metadata_date = datetime.datetime.strptime(metadata['date_taken'], '%Y-%m-%d %H:%M:%S')
            #new_date = metadata_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict['0th'][piexif.ImageIFD.DateTime] = metadata['date_taken']
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = metadata['date_taken']
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = metadata['date_taken']
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(filename))

            if "win" in sys.platform:
                metadata_date = datetime.datetime.strptime(metadata['date_taken'], '%Y-%m-%d %H:%M:%S')
                setctime(str(filename), metadata_date.timestamp())


def update_images(img_dir: str, metadata_dir: str, fields: list):
    print("Extracting IDs from image dir...")
    id_map = build_id_map(img_dir)
    print("Applying exif update to image dir...")
    apply_exif(id_map, metadata_dir, fields)
    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img-dir', help='Image Directory', type=str)
    parser.add_argument('--metadata-dir', help='Metadata Directory', type=str)
    parser.add_argument('-f', '--field', nargs='+', help='<Required> Fields to try to copy', required=False)
    args = parser.parse_args()

    update_images(args.img_dir, args.metadata_dir, args.field)
