"""
Central configuration file for the spectral-matching tool.

All adjustable parameters—file paths, analysis settings,
fitting behaviour, plotting options, and baseline-correction
settings—are defined here to keep the rest of the codebase clean
and consistent.
"""

# ---- BASELINE CORRECTION SETTINGS ----
# Baseline correction is applied only to sample spectra (not references).
#
# The algorithm:
#   1) Takes a specified fraction of points at the beginning and end of the spectrum.
#   2) Computes the mean absorbance in each region.
#   3) Fits a straight line between these two mean values.
#   4) Subtracts this line from the sample to remove baseline drift.

baseline_correction_use = True         # Enable or disable baseline correction
baseline_correction_fraction = 0.20     # Fraction of points used at each edge
baseline_correction_minpoints = 50      # Minimum points used at each ed

# ---- REFERENCE FITTING SETTINGS ----
# You can either:
#   (1) Let the program compute the optimal least-squares multipliers for all available references, or
#   (2) Manually specify multipliers for a selected subset of references.
#
# If ref_multiplier is None:
#       → the program computes the best least-squares fit.
#
# If ref_multiplier is a list of floats:
#       → the program uses these values directly.
#         In this case, selected_ref_names must be a list of equal length
#         specifying which reference spectra the multipliers belong to.
#
# For a list of available reference names, run:
#       python main.py list-refs

ref_multiplier = None       # e.g. [0.65, 0.18]
selected_ref_names = None   # e.g. ["CO2", "H2O"]

# ---- FITTING SETTINGS ----
# Least-squares fitting may occasionally produce negative multipliers for
# individual reference spectra. These occur when the fit attempts to
# counteract noise or imperfect baseline correction rather than representing
# a physically meaningful negative abundance.
#
# If enabled, negative multipliers are clipped to zero after fitting.

clamp_negative_multipliers = True


# ---- RESIDUALS SETTINGS ----
# When enabled, the plotted output shows the residual spectrum:
# the difference between the sample and the fitted combination of
# reference spectra. Residuals ideally contain only noise but may
# reveal additional features not captured by the fit.

plot_residuals = False

# ---- CONSTITUENT FIT SETTINGS ----
# When enabled, each individual reference spectrum used in the fit is
# additionally plotted individually. This visualizes the contribution of each
# constituent to the overall fitted spectrum.

show_constituent_fits = False

# ---- DATA SETTINGS ----
# Fields that *must* be present in a .jdx file for it to be considered valid.
# If any of these fields cannot be parsed, the loader will raise an error.
#
# Notes:
#   - "x" and "y" are not listed here because they are always checked separately
#     and are inherently required.
#   - This list should only need modification if the code is extended or if certain
#     .jdx files are known to omit fields that your workflow does not rely on.

required_fields_in_jdx = [
    "title",
    "molform",
    "yunits",
    "firstx",
    "deltax",
    "npoints",
]

# Default header size for CSV sample files.
# Used when Spectrum.from_csv() is called without an explicit header size.
header_size_in_csv = 1

# ---- PATHS ----
sample_path = "data/sample/"
ref_path = "data/reference/"


# ---- PLOT SETTINGS ----
plot_dpi = 400
figsize = (12, 6)
sample_linewidth = 0.5
fit_linewidth = 0.2
constituent_linewidth = 0.2
