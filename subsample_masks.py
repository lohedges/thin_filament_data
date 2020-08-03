from glob import glob
from random import random, randint
from skimage.transform import resize
from skimage.util import img_as_ubyte

import argparse
import glob
import imageio
import numpy as np
import os
import shutil

# Helper function to check for valid 'width' argument.
def check_width(value):
    ivalue = int(value)
    if ivalue < 100 or ivalue > 1000:
        raise argparse.ArgumentTypeError("'width' must be in range 100-1000")
    return ivalue

# Helper function to check for valid 'samples' argument.
def check_samples(value):
    ivalue = int(value)
    if ivalue < 100:
        raise argparse.ArgumentTypeError("'samples' must be in >= 100")
    return ivalue

# Helper function to check for valid 'trials' argument.
def check_trials(value):
    ivalue = int(value)
    if ivalue < 10:
        raise argparse.ArgumentTypeError("'trials' must be in >= 10")
    return ivalue

# Helper function to check for valid 'relative-difference' argument.
def check_rel(value):
    ivalue = float(value)
    if ivalue <=0 or ivalue >= 1:
        raise argparse.ArgumentTypeError("'relative-difference' must be in range 0-1")
    return ivalue

# Helper function to determine whether a sub-region is 'balanced'.
def is_balanced(sub_region, tol):
    # Work out the area of the sub-region.
    area = sub_region.shape[0]**2

    # Compute the sum of the sub-region.
    sub_sum = np.sum(sub_region)

    # If the sum is greater than the area, then divide by 255.
    if sub_sum > area:
        sub_sum /= 255

    # Work out the relative difference between black/white pixels.
    diff = abs(0.5 - (sub_sum/area))

    # Check whether the relative difference in black/white pixels is < tol.
    if diff < tol:
        return True
    else:
        return False

# Helper function to handle boolean command-line flags.
def str2bool(v):
    """Convert an argument string to a boolean value."""
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

# Create the command-line argument parser.
parser = argparse.ArgumentParser(
    description="Sub-sample micrographs to balance data classes.")

# Add the arguments.
parser.add_argument("-mw", "--min-width", type=check_width, default=256,
    help="The minimum width of sub-sampled region in pixels (100-1000).")
parser.add_argument("-Mw", "--max-width", type=check_width, default=256,
    help="The minimum width of sub-sampled region in pixels (100-1000).")
parser.add_argument("-s", "--samples", type=check_samples, default=500,
    help="The number of sub-samples to generate.")
parser.add_argument("-t", "--trials", type=check_trials, default=500,
    help="The number of trials per micrograph.")
parser.add_argument("-r", "--relative-difference", type=check_rel, default=0.2,
    help="The maximum relative difference in data classes.")
parser.add_argument("-rw", "--reweight", type=str2bool, nargs='?', const=True,
                    default=False, help="Reweight sample widths and brightnesses.")

# Parse the arguments.
args = parser.parse_args()

# Make sure min width is less than or equal to max width.
if args.min_width > args.max_width:
    raise argparse.ArgumentTypeError("'min-width' must be <= to 'max-width'")

if args.min_width != args.max_width:
    is_variable_width = True
else:
    is_variable_width = False

print("Sub-sampling...")
print(f"  samples             : {args.samples:d}")
print(f"  min width           : {args.min_width:d}")
print(f"  max width           : {args.max_width:d}")
print(f"  trials              : {args.trials:d}")
print(f"  relative-difference : {args.relative_difference:.2f}")
print()

# Create the required output directories.
try:
    # Remove the existing directory tree.
    shutil.rmtree("sub_samples")
except:
    pass
os.makedirs("sub_samples/image")
os.makedirs("sub_samples/label")

# Intialise the sample and trial counters.
num_samples = 0
num_trials = 0

# Loop over all masks to generate a lookup of their "brightness".
mask_brightness = {}
for mask in glob.glob("masks/*png"):
    img = imageio.imread(mask)
    mask_brightness[mask] = float(np.sum(img))

min_brightness = float(min(mask_brightness.values()))
max_brightness = float(max(mask_brightness.values()))

# Keep looping until we reach the required number of samples.
while num_samples < args.samples:

    # Loop over all masks. We choose to analyse masks rather than micrographs
    # since there might not be a mask for every micrograph.
    for mask in glob.glob("masks/*png"):
        # Reconstruct the original micrograph file name.
        filename = (mask.split("_mask")[0] + ".png").split("masks/")[1]

        print(f"Processing micrograph: {filename}")

        # Load the micrograph.
        image = imageio.imread(f"filament_picking/{filename}")

        # Get the brightness.
        brightness = mask_brightness[mask]

        # Load the mask.
        mask = imageio.imread(mask)

        # Resize the micrograph so that it matches the mask.
        image = resize(image, (mask.shape[0], mask.shape[1]), anti_aliasing=True)

        # Convert to uint8.
        image = img_as_ubyte(image)

        # Get the width and height of the mask.
        width, height = mask.shape

        # Attempt args.trials sub-samples per-mask.
        for x in range(0, args.trials):

            # Increment the total number of trials.
            num_trials += 1

            # Generate a random sub-sample width.
            sub_width = randint(args.min_width, args.max_width)

            # Generate random (x,y) coordinates for the sub-sample box.
            x = randint(0, width-sub_width)
            y = randint(0, height-sub_width)

            # Extract the 2D sub-sampled region from the mask.
            sub_mask = mask[x:x+sub_width, y:y+sub_width]

            # Check that sub-region is within balancing tolerance.
            if is_balanced(sub_mask, args.relative_difference):

                # Whether to accept the sample.
                is_accept = True

                # Sample sub-widths linearly.
                if args.weight:
                    if is_variable_width:
                        prob = 1 + (sub_width - args.max_width) / (args.max_width - args.min_width)
                        if random() > prob:
                            is_accept = False

                # Sample mask "brightness" linearly.
                if is_accept:
                    if args.weight:
                        prob = 1 + (brightness - max_brightness) / (max_brightness - min_brightness)
                        if random() > prob:
                            is_accept = False

                    # Accept the sample.
                    if is_accept:
                        # Increment the number of samples.
                        num_samples += 1

                        # Extract the same sub-region from the micrograph.
                        sub_image = image[x:x+sub_width, y:y+sub_width]

                        # Create the file name.
                        file_name = f"{num_samples:05d}"

                        # Write the sub-regions to disk.
                        imageio.imwrite("sub_samples/image/" + file_name + ".png", sub_image)
                        imageio.imwrite("sub_samples/label/" + file_name + ".png", sub_mask)

                        # Compute the sample frequency.
                        freq = num_samples / num_trials

                        # Compute the fractional brightness.
                        brightness = (brightness - min_brightness) / (max_brightness - min_brightness)

                        print(f"  Generated sample {num_samples}, width = {sub_width}, brightness = {brightness:.2f}, frequency = {freq:.2f}")

                        # Early exit.
                        if num_samples == args.samples:
                            break

        # Early exit.
        if num_samples == args.samples:
            break
