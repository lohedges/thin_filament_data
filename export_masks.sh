#! /bin/bash

SVG_DIR=filament_picking
MASK_DIR=masks

selected=$(ls ${SVG_DIR}/*.svg)

mkdir -p ${MASK_DIR}

for f in ${selected}
do
    filename=$(basename -- "$f")
    stem=${filename:0:-4}
    inkscape --without-gui --export-png=masks/${stem}_mask.png --export-area-page --export-background=white --export-background-opacity=1.0 --export-id=layer18 --export-id-only ${f}
done

