## Flickr `date_taken` exif copy
This is simple script to solve a very specific problem. It takes the metadata
export you get from flickr and updates the create data/date taken metdata on your files.

It is expected that the export from flickr is in the form of 1 json file per image.
The `date_taken` field in these json files will be used to set the create date or `date_taken`
EXIF metadata if the file is a JPEG.

If you are on Windows, the creation date will also be updated on the file, which is useful for 
non-JPEG images and MP4s.

## Use
This process assumes you are on Windows, but will work on other OSs with python (just the file 
system create date will not be set.)

### Install miniconda
This simple script was written in python, so you need to have a functioning python env
on your computer. Download and install Miniconda3 Windows 64-bit4 with Python 3.8 from here: https://docs.conda.io/en/latest/miniconda.html

Once installed, you'll have an "Anaconda Prompt" available as an application.

### Download this code
You can git clone if you know how to do that. If now, [download the zip](https://github.com/dkleissa/flickr-exif-copy/archive/refs/heads/main.zip) from Github and
extract it somewhere.

### Setup the environment
Open the Anaconda terminal. You should change directories to the location where you unzipped
this repository doing something like:

```
cd ~/Downloads/flickr-exif-copy
```

Then install the dependencies by running:

```
pip install -r requirements.txt
```

### Run the script
Now you are ready to run the script. It will edit the files in place.

```
python3 exif_copy.py --img-dir ~/Documents/my_images --metadata-dir ~/Documents/my_metadata
```

