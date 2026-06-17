# Air-rescue civil-military integration models

Computational supplement to the study

> M. M. Kasperek (2026). *Civil-military integration of a reformed national
> air-rescue network.* Defence and Peace Economics (preprint).

This repository holds the two deterministic models that regenerate the figures
of the paper. Running them reproduces every quantitative result of Appendix 1
and Appendix 2 to the unit, with the small exception noted below for the
placement minutes.

The Polish-language version of this README is in `README.pl.md`.

## Contents

| File | Reproduces | What it does |
| --- | --- | --- |
| `economic_model.py` | Tables 2 and 3 (Appendix 1) | Ten-year simulation of the LEM-PPP company, net present value, the optimistic scenario, and the sensitivity of the net investment balance to the discount rate. |
| `reserve_placement.py` | Appendix 2 | Discrete p-centre (minimax) placement of the four civil AW101, by exhaustive enumeration of all 35 combinations of the seven Regional Centres, plus the two-pillar variant adding the Navy base at Darlowo. |
| `poland_boundary.geojson` | Appendix 2 | National outline (ADM0) of Poland from geoBoundaries, the land grid for the placement is built from it. |
| `poland_voivodeships.geojson` | Figure A2.1 | Voivodeship borders (ADM1) from geoBoundaries, drawn on the map for orientation. |
| `figure_a2_1.py` | Figure A2.1 | Renders the two-pillar reach-time map, the five bases and the two southern residual salients. Needs matplotlib and numpy. |
| `tests/` | both | Nineteen unit tests that check the reproduced figures against the paper. |

## Requirements

Python 3.8 or newer. The two models use only the standard library, so they have
no runtime dependencies. The test suite uses `pytest`.

```bash
pip install -r requirements.txt   # only needed to run the tests
```

## Running the models

```bash
python economic_model.py
python reserve_placement.py
```

`economic_model.py` prints Table 2 (the company simulation with real and nominal
cash flows, the net present value, the optimistic value, and the treasury
benefit) and Table 3 (the sensitivity of the net investment balance at 3, 4 and
5 per cent). Every figure matches the paper exactly.

`reserve_placement.py` prints the single-pillar optimum (Krakow, Lublin, Poznan
and Olsztyn), its worst-case reach, the conventional four-city reference, and the
two-pillar worst-case after the Navy base at Darlowo is added. It also reports
the reach to the named reference points on the Baltic coast and at the southern
mountain salients.

## Running the tests

```bash
python -m pytest tests/ -v
```

## Generating Figure A2.1

```bash
python figure_a2_1.py
```

This writes `figure_A2_1.png`, the two-pillar reach-time map. It colours every
land point by its reach to the nearest reserve base, marks the five bases, and
crosses the two southern residual salients near Klodzko and in the Bieszczady,
both about 57 minutes. The script needs matplotlib and numpy.

## Boundary and figures

The placement runs on `poland_boundary.geojson`, the national outline (ADM0) of
Poland from the geoBoundaries open database. With this boundary the model
reproduces the paper. The optimum is Krakow, Lublin, Poznan and Olsztyn. The
single-pillar worst case is 58.6 minutes, at the central Baltic coast near Rowy,
against 69.8 for the conventional four-city set. The Navy base at Darlowo sits on
that same central stretch of coast, so adding it brings the central coast within
about 15 minutes and the north-western corner within about 37. The country-wide
two-pillar worst case is 57.3 minutes, at the southern mountain salients, Klodzko
in the south-west and the Bieszczady in the south-east, a near tie. The economic
model is exact to the unit. On a five-kilometre grid the single-pillar worst case
falls between 58 and 59 minutes depending on which coastal cell is sampled.
Substituting another national boundary in `poland_boundary.geojson` changes
nothing in the algorithm.

## Method, in brief

The placement follows a discrete p-centre rule. For every combination of four of
the seven Regional Centres, the model computes the worst-case reach over a
five-kilometre land grid, where reach is great-circle distance divided by a
cruise speed of 278 km/h plus five minutes for start-up. The combination with
the smallest worst-case reach is the global optimum, found by enumeration rather
than by a heuristic.

The economic model values the company as a financial entity over a ten-year
horizon, with a net result, a free cash flow that adds back depreciation and
subtracts replacement capital, and a terminal residual value. The company is
discounted at 4 per cent in real terms, the public balance at the social rate of
3 per cent. A nominal variant grown at the 2.5 per cent inflation target and
discounted at the matching nominal rate returns the same present value, by the
Fisher relation.

## Boundary data

`poland_boundary.geojson` (ADM0) and `poland_voivodeships.geojson` (ADM1) are
Poland outlines from geoBoundaries (gbOpen release). geoBoundaries is distributed
under CC BY 4.0, separately from the Apache-licensed code. Please keep this
attribution if you redistribute the files.

> Runfola, D., et al. (2020). geoBoundaries: A global database of political
> administrative boundaries. *PLoS ONE* 15(4), e0231866.
> https://www.geoboundaries.org

## How to cite

If you use this software, please cite both the paper and the software record.

Paper:

> Kasperek, M. M. (2026). Civil-military integration of a reformed national
> air-rescue network. *Defence and Peace Economics* (preprint).

Software:

> Kasperek, M. M. (2026). *Air-rescue civil-military integration models*
> (version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.20734498

## Author

Maciej M. Kasperek. ORCID 0009-0008-7419-0851.

## Licence

Apache License 2.0. See `LICENSE` and `NOTICE`.
