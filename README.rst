Cryo EM data set
================

Images
------

Starting from a directory or MRC file called ``raw``::

   python convert_tiff.py

outputs TIFF files in ``input`` and PNG files into ``filament_picking``.

Filament picking
----------------

To create image maks for segmentation, run::

   create_svg.sh

which will then create and SVG file for each PNG with a layer called ``filaments``.
Draw paths in black in that layer using Inkscape and then run::

   export_masks.sh

which will write PNG masks into ``masks``.

If you want just the x/y coorginates of the paths in CSV format, run::

   svg_to_csv.py

which will write them into ``filament_picking``.

Manual protein picking
----------------------

Given a directory of `star` files called ``manual_pick``, run::

   parse_positions.py

which will write CSV files of the coordinates into ``manual_pick``.

Sub-sampling masks
------------------

The linear nature of filaments and the low density at which they appear in
micrographs can cause issues with machine learning due the to unbalanced
nature of the two data classes. While we want our network to accurately predict
the presence of filaments, the majority class is the background. This means
that it's possible to obtain a high accuracy (number of correctly predicted
pixels divided by total number of pixels) by simply predicting that the
micrograph is empty.

To help with this issue, a script is provided to sub-sample micrograph regions
to re-balance the data classes, so that the network is trained on samples that
contain images with a closer match of filament and non-filament pixels. Run::

    python subsample_masks.py -h

to see how to use the script.

Note that the script assumes that masks are in a directory called ``masks``
and the raw PNG files are in ``filament_picking``, as used for the other
scripts above. Output will be written to ``sub_samples/image`` and
``sub_samples/label``, which can then be used for training.
