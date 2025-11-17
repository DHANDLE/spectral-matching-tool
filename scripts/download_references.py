"""
This script downloads publicly available infrared reference spectra
from the NIST Chemistry WebBook (https://webbook.nist.gov/).

The data is not redistributed in this repository. Instead, this script
retrieves the original files directly from NIST for personal,
educational, and non-commercial use, in accordance with their usage
policy.

References downloaded:
    - NH3 (called H3N in its metadata)
    - H2O
    - CO
    - N2O
    - O3
    - C2H6
    - CH4
    - CO2

Notes:
    - NIST includes copyright and usage information directly inside
      the downloaded JCAMP-DX files. This metadata is stored in clear
      text at the top of each file and should be reviewed by users.
    - These URLs point directly to the current NIST JCAMP-DX files.
      Since NIST occasionally reorganises their servers, the links
      may stop working in the future.
    - This project is not affiliated with or endorsed by NIST.

If any link fails, visit the NIST Chemistry WebBook manually and
download the relevant spectrum.
"""

import os
import sys
import time
import requests

import config

NIST_URLS = {
    "NH3":  "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C7664417&Index=0&Type=IR",
    "H2O":  "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C7732185&Index=0&Type=IR",
    "CO":   "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C630080&Index=0&Type=IR",
    "N2O":  "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C10024972&Index=0&Type=IR",
    "O3":   "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C10028156&Index=0&Type=IR",
    "C2H6": "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C74840&Index=0&Type=IR",
    "CH4":  "https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C74828&Index=0&Type=IR",
    "CO2":  "https://webbook.nist.gov/cgi/inchi?JCAMP=C124389&Index=0&Type=IR",
}


def download_file(url: str, out_path: str, *, retries: int = 3):
    headers = {
        "User-Agent": "spectral-matching-tool"
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()

            with open(out_path, "wb") as f:
                f.write(r.content)

            print(f"✓ Downloaded: {out_path}")
            return True

        except requests.exceptions.SSLError as e:
            print(f"SSL error fetching {url}: {e} (attempt {attempt}/{retries})")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error {r.status_code} for {url} (attempt {attempt}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e} (attempt {attempt}/{retries})")

        time.sleep(1)

    print(f"✗ Failed to download after {retries} attempts: {url}")
    return False

def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.ref_path)


    print(f"Downloading NIST JCAMP spectra to: {out_dir}\n")

    for gas, url in NIST_URLS.items():
        out_path = os.path.join(out_dir, f"{gas}.jdx")
        download_file(url, out_path)

    print("\nDone.")
    print("If any downloads failed, please visit the NIST WebBook manually.")

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()