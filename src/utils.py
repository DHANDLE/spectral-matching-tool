"""
Utility functions for spectrum handling and analysis.

This module provides utility functions,
including `analyze_spectrum`, as well as helpers for loading,
processing, and interpolating spectra.
"""
import glob
import os
import sys
import numpy as np
from typing import List

from matplotlib import pyplot as plt

from src.spectrum import Spectrum
import config

# Loads and returns all saved references.
def get_references() -> List[Spectrum]:
    ref_path = config.ref_path
    ref_files = glob.glob(os.path.join(ref_path, "*.jdx"))
    if not ref_files:
        sys.exit("No references available. Please refer to README")
    ref_data = []
    for f in ref_files:
        ref_data.append(Spectrum.from_jdx(f))
    return ref_data

# Loads and returns all saved samples.
def get_samples() -> List[Spectrum]:
    sample_path = config.sample_path
    sample_files = glob.glob(os.path.join(sample_path, "*.csv"))
    if not sample_files:
        sys.exit("No samples available. Please refer to README")
    sample_data = []
    for s in sample_files:
        sample_data.append(Spectrum.from_csv(s))
    return sample_data

# Interpolates references to fit the grid of the sample
# Returns y absorbance values that fit the sample grid
def interpolate_to(sample_x: np.ndarray, ref: Spectrum) -> np.ndarray:
    return np.interp(
        sample_x,
        ref.x,
        ref.get_y_absorbance(),
        left=0.0,
        right=0.0
    )


def analyze_spectrum(samples: list[Spectrum]) -> None:
    selected_ref_names = config.selected_ref_names
    ref_multiplier = config.ref_multiplier
    ref_data = get_references()

    if ref_multiplier:
        if not config.selected_ref_names:
            raise ValueError(
                "selected_ref_names must be provided when ref_multiplier is used."
            )

        if len(ref_multiplier) != len(selected_ref_names):
            raise ValueError(
                "selected_ref_names must have the same length as ref_multiplier, "
                "specifying which reference spectrum each multiplier corresponds to."
            )

    if selected_ref_names:
        ref_data = [r for r in ref_data if r.molform in config.selected_ref_names]

    for s in samples:
        if config.baseline_correction_use:
            s.correct_linear_baseline()  # implicitly converts s to absorbance.
        ref_multiplier = config.ref_multiplier # Needs to be reset before running the loop again.
        r2 = None
        if ref_multiplier is None:
            # Stack all reference y-data column-wise
            A = np.column_stack([interpolate_to(s.x, ref) for ref in ref_data])
            # Least squares solution: finds ref_mult_list to minimise ||A * m - y_sample||
            ref_multiplier, residuals, _, _ = np.linalg.lstsq(A, s.get_y_absorbance(), rcond=None)

            # Clamp negative values if configured
            if config.clamp_negative_multipliers:
                ref_multiplier = np.clip(ref_multiplier, 0, None)

            ss_res = residuals[0] if residuals.size > 0 else np.sum((s.get_y_absorbance() - A @ ref_multiplier) ** 2)
            ss_tot = np.sum((s.get_y_absorbance() - np.mean(s.get_y_absorbance())) ** 2)
            r2 = 1 - ss_res / ss_tot

        fig, ax = plt.subplots(figsize=config.figsize, dpi=config.plot_dpi)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        # If plot_residuals: don't show the sample
        sample_alpha = 0 if config.plot_residuals else 1

        # Plot sample
        ax.plot(s.x, s.get_y_absorbance(),
                label=f"Sample: {s.title}",
                color='k', alpha=sample_alpha, lw=config.sample_linewidth)

        combined = np.zeros_like(s.get_y_absorbance())

        ref_pairs = list(zip(ref_data, ref_multiplier))
        ref_pairs.sort(key=lambda p: p[1], reverse=True)
        for ref, ref_mult in ref_pairs:
            x_ref, y_ref = s.x, interpolate_to(s.x, ref)
            color = "r" if len(ref_data) == 1 else None
            alpha = 0.7 if (config.show_constituent_fits and not config.plot_residuals) else 0
            # Plot constituents
            ax.plot(x_ref, y_ref * ref_mult,
                    label=f"Reference: {ref.molform}\nMultiplier: {ref_mult:.2f}",
                    alpha=alpha, c=color, lw=config.constituent_linewidth)
            combined += y_ref * ref_mult

        # Plot combined fit
        if not config.plot_residuals:
            label = "Combined fit"
            if r2:
                label += f"\n$R^2$ = {r2:.3f}"
            ax.plot(s.x, combined, label=label, color='r', lw=config.fit_linewidth)

        # Plot residuals
        if config.plot_residuals:
            y_residuals = s.get_y_absorbance() - combined
            ax.plot(s.x, y_residuals, label="Residuals", color='r', lw=config.sample_linewidth)

        ax.set_xlim(s.maxx, s.minx)
        ax.set_xlabel("Wavenumber (cm$^{-1}$)")
        ax.set_ylabel("Absorbance")
        ax.legend(loc="upper left")
        if config.plot_residuals:
            ax.set_title("Residuals of IR spectrum comparison of {s.title}")
        else:
            ax.set_title(f"IR spectrum comparison of {s.title}")

        plt.tight_layout()
        plt.show()
        plt.close('all')
