#! /bin/bash

SVG_DIR=filament_picking

for f in ${SVG_DIR}/*.png
do
    echo "Creating SVG for: $f"
    sed "s#IMAGE_NAME#${f}#g" svg_template > ${f:0:-4}.svg
done
