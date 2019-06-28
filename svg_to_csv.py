from pathlib import Path
import xml.etree.ElementTree as ET

from pandas import DataFrame, Series
from svgpathtools import parse_path

io_dir = Path("filament_picking")

for f in io_dir.glob("*.svg"):
    tree = ET.parse(f)
    root = tree.getroot()
    paths = root.findall("./{http://www.w3.org/2000/svg}g[@id='layer18']/{http://www.w3.org/2000/svg}path")
    path_data = [p.attrib["d"] for p in paths]

    filament_nums = []
    xs = []
    ys = []

    for path_num, p in enumerate(path_data):
        coords = []
        segs = parse_path(p)

        filament_nums.append(path_num)
        xs.append(segs[0].start.real)
        ys.append(segs[0].start.imag)
        filament_nums.append(path_num)
        xs.append(segs[0].end.real)
        ys.append(segs[0].end.imag)
        for seg in segs[1:]:
            filament_nums.append(path_num)
            xs.append(seg.end.real)
            ys.append(seg.end.imag)

    df = DataFrame({"filament_num" : filament_nums, "x":xs, "y":ys})
    csv_path = io_dir / f"{f.stem}.csv"
    if not df.empty:
        df.to_csv(csv_path)
