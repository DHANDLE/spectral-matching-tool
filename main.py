"""
Entry point for the spectral-matching tool.

Behaviour:
    - No arguments:
        Analyze all samples according to the config file.
    - analyze <files>:
        Analyze the specified sample(s).
    - plot <files>:
        Plot one or more spectra.
    - list-refs:
        List all available reference spectra.
"""

from src.utils import *

def main():
    # INIT
    argv = sys.argv
    argc = len(argv)

    # Run full program, analyzing all samples in the specified folder (default ./data/sample)
    if argc == 1:
        analyze_spectrum(get_samples())


    elif argv[1] == "list-refs":
        if not argc == 2:
            sys.exit("list-refs does not take additional arguments")

        ref = get_references()

        for d in ref:
            print(d.molform)

        return

    # Plot 1 or more specified files.
    elif argv[1] == "plot":
        if argc == 2:
            sys.exit("Please specify the file to plot")

        else:
            file_paths = argv[2:]
            spectra: list[Spectrum] = []
            for f in file_paths:
                if f.endswith(".csv") or f.endswith(".CSV"):
                    spectra.append(Spectrum.from_csv(f))
                elif f.endswith(".jdx") or f.endswith(".JDX"):
                    spectra.append(Spectrum.from_jdx(f))
                else:
                    sys.exit(f"Unable to plot {f}. Refer to README for supported filetypes")

            for s in spectra:
                s.plot()

            return

    # Analyze a specific sample using all supplied references
    # According to config file
    elif argv[1] == "analyze":
        if argc == 2:
            sys.exit("Please specify the file to plot")

        else:
            file_paths = argv[2:]

            samples: list[Spectrum] = []
            for f in file_paths:
                if f.endswith(".csv") or f.endswith(".CSV"):
                    samples.append(Spectrum.from_csv(f))
                elif f.endswith(".jdx") or f.endswith(".JDX"):
                    samples.append(Spectrum.from_jdx(f))
                else:
                    sys.exit(f"Unable to analyze {f}. Refer to README for supported filetypes")

            analyze_spectrum(samples)


    else:
        sys.exit("Unknown command supplied")


if __name__ == "__main__":
    main()