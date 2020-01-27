#! /bin/bash

SVG_DIR=filament_picking
MASK_DIR=masks

selected=$(ls ${SVG_DIR}/*.svg)

mkdir -p ${MASK_DIR}

for f in ${selected}
do
    filename=$(basename -- "$f")
    stem=${filename:0:-4}
    output_filename=masks/${stem}_mask.png
    inkscape --without-gui --export-png=${output_filename} --export-area-page --export-background=white --export-background-opacity=1.0 --export-id=layer18 --export-id-only ${f}
    mogrify -colorspace Gray ${output_filename}
done

