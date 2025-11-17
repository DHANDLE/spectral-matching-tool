"""
This file defines the Spectrum Class and its methods.
"""
import math
import os
from dataclasses import field, dataclass
from typing import Optional, List, get_type_hints, Any

import numpy
from matplotlib import pyplot as plt
import numpy as np
from numpy import ndarray, dtype

import config

@dataclass
class Spectrum:
    """
    Not all fields loaded are used but may be useful in further development.
    """
    title: Optional[str] = None
    data_type: Optional[str] = None
    cas_registry_no: Optional[str] = None
    molform: Optional[str] = None
    state: Optional[str] = None
    xunits: Optional[str] = None
    yunits: Optional[str] = None
    xfactor: Optional[float] = None
    yfactor: Optional[float] = None
    deltax: Optional[float] = None
    firstx: Optional[float] = None
    lastx: Optional[float] = None
    firsty: Optional[float] = None
    maxx: Optional[float] = None
    minx: Optional[float] = None
    maxy: Optional[float] = None
    miny: Optional[float] = None
    npoints: Optional[int] = None

    x: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    y: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))

    # This method assumed the file format in JCAMP-DX format files from NIST.
    @classmethod
    def from_jdx(cls, path: str) -> "Spectrum":
        s = cls()
        y_vals = []
        required = config.required_fields_in_jdx
        # Maps .jdx naming convention to results naming convention
        keymap = {
            "TITLE": "title",
            "DATA TYPE": "data_type",
            "CAS REGISTRY NO": "cas_registry_no",
            "MOLFORM": "molform",
            "STATE": "state",
            "XUNITS": "xunits",
            "YUNITS": "yunits",
            "XFACTOR": "xfactor",
            "YFACTOR": "yfactor",
            "DELTAX": "deltax",
            "FIRSTX": "firstx",
            "LASTX": "lastx",
            "FIRSTY": "firsty",
            "MAXX": "maxx",
            "MINX": "minx",
            "MAXY": "maxy",
            "MINY": "miny",
            "NPOINTS": "npoints",
        }
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                # Header fields
                if line.startswith("##") and "=" in line:
                    label, val = line[2:].split("=", 1)
                    label = label.strip().upper()
                    val = val.strip()

                    if label in keymap:
                        if get_type_hints(cls)[keymap[label]] == Optional[float]:
                            setattr(s, keymap[label], float(val))
                        elif get_type_hints(cls)[keymap[label]] == Optional[int]:
                            setattr(s, keymap[label], int(val))
                        else:
                            setattr(s,keymap[label], val)

                # Data lines
                if line and line[0].isdigit():
                    parts = line.split()
                    ys = [float(v) for v in parts[1:]]
                    for y in ys:
                        y_vals.append(y)


        s.y = np.array(y_vals, float)

        # Throw error if a required field could not be parsed
        for key in required:
            if not getattr(s, key):
                 raise ValueError(f"Could not parse {key} in {path}")

        # Remove empty spaces in molform
        s.molform = s.molform.replace(" ", "")

        # generate x from the meta data
        s.x = np.arange(s.npoints, dtype=float) * s.deltax + s.firstx

        if s.x.size == 0:
            raise ValueError(f"Missing array field 'x' in {path}")
        if s.y.size == 0:
            raise ValueError(f"Missing array field 'y' in {path}")
        if not len(s.x) == len(s.y):
            raise ValueError(f"The number of x-values and y-values in {s.title} does not match.")

        # apply the yfactor to properly scale y values
        if s.yfactor is not None and s.yfactor != 1.0:
            s.y = s.y * s.yfactor

        return s

    # This method assumes CSV spectrum where each row contains:
    # #   wavenumber (cm⁻¹), absorbance
    # The first `header_size` lines are treated as metadata and skipped.
    @classmethod
    def from_csv(cls, path: str, name: str = None, molform: str = None, header_size: int = config.header_size_in_csv) -> "Spectrum":
        s = cls()

        x_vals = []
        y_vals = []

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            # Skip header/metadata lines
            for _ in range(header_size):
                next(f, None)

            # Read data rows
            for line in f:
                line = line.strip()
                if not line:
                    continue  # skip blank lines

                parts = line.split(",")
                if len(parts) < 2:
                    raise ValueError(f"Invalid CSV row (expected 2 columns): {line}")

                try:
                    x = float(parts[0])
                    y = float(parts[1])
                except ValueError:
                    raise ValueError(f"Non-numeric value in row: {line}")

                x_vals.append(x)
                y_vals.append(y)

        # Assign fields
        s.x = np.array(x_vals, dtype=float)
        s.y = np.array(y_vals, dtype=float)
        # Populates metadata, some are currently unused
        if name:
            s.title = name
        else:
            s.title = os.path.splitext(os.path.basename(f.name))[0]

        if molform:
            s.molform = molform

        s.maxx = max(x_vals)
        s.minx = min(x_vals)
        s.maxy = max(y_vals)
        s.miny = min(y_vals)
        s.firstx = x_vals[0]
        s.lastx = x_vals[-1]
        s.firsty = y_vals[1]
        s.npoints = len(s.x)
        s.xunits = "1/cm"
        s.yunits = "ABSORBANCE"

        return s

    def get_y_absorbance(self) -> np.ndarray:
        """
        Returns y-values in absorbance units.
        Just returns y-values if already in absorbance
        The enables getting just the y values in absorbance without having to explicitly convert.
        """
        if self.yunits is None:
            raise ValueError(f"yunits is not set in {self.title}")

        if self.yunits.strip().upper() == "ABSORBANCE":
            return self.y  # return a copy

        # If transmittance, convert
        if self.yunits.strip().upper() == "TRANSMITTANCE":
            # Using the formula A = -log10(T)
            epsilon = 1e-12  # avoid log10(0)
            return -np.log10(np.maximum(self.y, epsilon))

        # Unknown units
        raise ValueError(f"Unsupported Y unit type: {self.yunits} in {self.title}")

    def plot(self) -> None:
        plt.figure(figsize=config.figsize, dpi=config.plot_dpi)
        plt.plot(self.x, self.y, linewidth=config.main_linewidth)
        #plt.ylim(bottom=0)
        plt.xlim((self.lastx, self.firstx))
        plt.xlabel(self.xunits)
        plt.ylabel(self.yunits)
        plt.title(f"IR spectrum of {self.title}")

        plt.show()

    def correct_linear_baseline(self, baseline_correction_fraction: float = config.baseline_correction_fraction) -> None:
        self.convert_to_absorbance() # ensures spectrum is in absorbance.
        points = max(int(baseline_correction_fraction * self.npoints), config.baseline_correction_minpoints)
        x1, x2 = self.x[0], self.x[-1]
        y1, y2 = np.mean(self.get_y_absorbance()[:points]), np.mean(self.get_y_absorbance()[-points:])
        grad = (y2 - y1) / (x2 - x1)
        intercept = y1 - grad * x1
        self.y -= grad * self.x + intercept

    # Converts the spectrum to absorbance. If already so does nothing.
    def convert_to_absorbance(self) -> None:
        if self.yunits is None:
            raise ValueError(f"yunits is not set in {self.title}")

        if self.yunits.strip().upper() == "ABSORBANCE":
            return

        # If transmittance, convert
        if self.yunits.strip().upper() == "TRANSMITTANCE":
            # Using the formula A = -log10(T)
            epsilon = 1e-12  # avoid log10(0)
            self.y = -np.log10(np.maximum(self.y, epsilon))
            self.yunits = "ABSORBANCE"
            return
