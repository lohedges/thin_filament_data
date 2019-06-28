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
