from pathlib import Path

import pandas as pd

for star_filename in Path(".").glob("manual_pick/*.star"):
    df = pd.read_csv(star_filename, delim_whitespace=True, skiprows=10, names=["x", "y", "class_number", "angle_psi", "fom"], usecols=[0, 1])

    csv_filename = Path("manual_pick") / f"{star_filename.stem}.csv"

    df.to_csv(csv_filename)
