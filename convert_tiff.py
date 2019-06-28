import argparse
from pathlib import Path

import mrcfile
from skimage import exposure
import skimage
import skimage.io
import tifffile


parser = argparse.ArgumentParser(description="Convert MRC files")
parser.add_argument("--raw", default="raw", help="The input location of the raw MRC files")
parser.add_argument("--tif", default="input", help="The output location of the TIFF files")
parser.add_argument("--png", default="filament_picking", help="The output location of the PNG files")
args = parser.parse_args()

input_files = list(Path(args.raw).glob("*.mrc"))

for i, f in enumerate(input_files):
    print(f"{i/len(input_files)*100:3.0f}% Reading {f}")
    with mrcfile.open(f, permissive=True) as mrc:
        h = mrc.header
        d = mrc.data

    d = exposure.equalize_hist(d)

    tif_output_filename = Path(args.tif) / f"{f.stem}.tif"
    tifffile.imsave(tif_output_filename, d)

    normalised = skimage.img_as_ubyte(d)
    png_output_filename = Path(args.png) / f"{f.stem}.png"
    skimage.io.imsave(png_output_filename, normalised)
