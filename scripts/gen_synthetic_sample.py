"""
Used to generate a synthetic sample given a mixture of reference spectra.
"""
import glob
import os
import numpy as np

from src.spectrum import Spectrum
import config

composition = {
    "CO2": 0.65,
    "H2O": 0.18,
    "CO":  0.07,
    "CH4": 0.04,
    "C2H6": 0.02,
    "N2O": 0.02,
    "O3":  0.02,
}

ref_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", config.ref_path))
ref_files = glob.glob(os.path.join(ref_path, "*.jdx"))

ref_data = [Spectrum.from_jdx(f) for f in ref_files]
for d in ref_data:
    print(d.molform)

# Build lookup table by molform (gas name)
lookup = {s.molform: s for s in ref_data}

#  Determine common X-axis
firstxs = [lookup[g].firstx for g in composition]
lastxs  = [lookup[g].lastx  for g in composition]
dxs     = [lookup[g].deltax for g in composition]

common_firstx = max(firstxs)
common_lastx  = min(lastxs)
common_dx     = min(dxs)

common_x = np.arange(common_firstx, common_lastx + common_dx, common_dx)

# Helper to interpolate a spectrum onto the common grid ----
def interp(spec: Spectrum) -> np.ndarray:
    x_old = np.array(spec.x, dtype=float)
    y_old = np.array(spec.get_y_absorbance(), dtype=float)
    return np.interp(common_x, x_old, y_old, left=0.0, right=0.0)

mix = np.zeros_like(common_x)

for gas, coeff in composition.items():
    mix += coeff * interp(lookup[gas])

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.sample_path, "synthetic_sample.csv")

with open(out_path, "w", encoding="utf-8") as f:
    f.write("wavenumber,absorbance\n")
    for x, y in zip(common_x, mix):
        f.write(f"{x},{y}\n")

print(f"Synthetic sample written to: {out_path}")
