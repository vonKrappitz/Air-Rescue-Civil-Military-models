# Air-rescue civil-military integration models

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20734497.svg)](https://doi.org/10.5281/zenodo.20734497)

**Version 2.0.0**

Computational supplement to:

> Kasperek, M. M. (2026). *A Public–Private Mobilisation Reserve for Air Medical
> Evacuation: Institutional Design and Economic Appraisal.*

Author: **Maciej M. Kasperek**, ORCID [0009-0008-7419-0851](https://orcid.org/0009-0008-7419-0851).

Code licensed under Apache 2.0 (`LICENSE`).
Boundary data from **geoBoundaries** (<https://www.geoboundaries.org>), used under CC BY 4.0. See `NOTICE.md`.

This package reproduces every number, table and figure in the article from source.

The Polish-language version of this README is in `README.pl.md`.

## Contents

- `economic_model.py` — financial and fiscal model (hypotheses H1 and H2). Run `python economic_model.py` to print the base-case results.
- `reserve_placement.py` — spatial reach and availability model (hypothesis H3). Run `python reserve_placement.py` to print base placement and coverage.
- `figure_zones.py` — generates Figure 1, the viability matrix (`figure_zones.png`).
- `figure_a2_1.py` — generates Figure 2, the two-pillar reach map (`figure_A2_1.png`).
- `tables.py` — generates every numeric table from the models (`tables.md`).
- `poland_boundary.geojson`, `poland_voivodeships.geojson` — national (ADM0) and voivodeship (ADM1) boundaries of Poland from the geoBoundaries open database, redistributed unmodified under CC BY 4.0. See `NOTICE.md`.
- `tests/` — 37 unit tests that lock every headline value.
- `requirements.txt` — Python dependencies.
- `LICENSE`, `NOTICE.md` — full Apache 2.0 licence text and attribution and attribution for the redistributed boundary data.
- `.gitattributes` — keeps line endings stable so the checksums in `MD5SUMS.txt` verify on every platform.
- `.gitignore` — keeps local caches (`__pycache__`, `.pytest_cache`) and generated output out of the repository.

## Reproduce

    pip install -r requirements.txt
    python -m pytest -q          # 37 tests, all headline numbers
    python economic_model.py     # base-case economic results
    python reserve_placement.py  # spatial coverage results
    python figure_zones.py       # Figure 1
    python figure_a2_1.py        # Figure 2
    python tables.py             # all tables

## Base-case headline values

- Private-partner equity NPV +7, IRR 10.5 per cent, break-even fee 63 (H2).
- Whole-of-system public cost: 601 resource, 481 budgetary, 399 economic; against 681 for public ownership and 682 to 768 for an availability contract; savings 80 and 282 (H1).
- Terminal company value 582 (state share 297, private share 285), single source of truth.
- Coverage within 45 minutes is exactly linear in military availability, 90.5 per cent plus 4.5 points per unit of availability (H3).

All amounts are in million zloty, constant 2026 prices.

## How to cite

If you use this software, please cite both the paper and the software.

Paper:
> Kasperek, M. M. (2026). A Public–Private Mobilisation Reserve for Air Medical
> Evacuation: Institutional Design and Economic Appraisal.

Software:
> Kasperek, M. M. (2026). *Air-rescue civil-military integration models*
> (version 2.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.21632716

## Author

Maciej M. Kasperek. ORCID 0009-0008-7419-0851.

## What is not here

The manuscript source is deliberately not included. This repository holds the
models, the data and the scripts that regenerate every table and figure, which is
what reproduction requires.
