# Attribution notice

Copyright 2026 Maciej M. Kasperek. Code licensed under the Apache License, Version 2.0; see `LICENSE`.

## Boundary data

`poland_boundary.geojson` (ADM0) and `poland_voivodeships.geojson` (ADM1) are the
national and voivodeship boundaries of Poland from the **geoBoundaries** open
database (gbOpen release), redistributed here **unmodified**.

geoBoundaries gbOpen is made available under the **Creative Commons Attribution 4.0
International licence (CC BY 4.0)**, <https://creativecommons.org/licenses/by/4.0/>.
Attribution is a condition of use. Licence terms recorded for an individual boundary
are held in the geoBoundaries metadata for that boundary; users who redistribute
these files further should check that metadata and carry any additional attribution
it requires.

Please cite:

> Runfola, D., Anderson, A., Baier, H., Crittenden, M., Dowker, E., Fuhrig, S.,
> Goodman, S., et al. (2020). geoBoundaries: A global database of political
> administrative boundaries. *PLOS ONE*, 15(4), e0231866.
> https://doi.org/10.1371/journal.pone.0231866

<https://www.geoboundaries.org>

### Upstream sources of the two files

As recorded in the geoBoundaries country table for Poland:

- `poland_boundary.geojson` (ADM0, 2011) — source: Wiki Commons Media.
- `poland_voivodeships.geojson` (ADM1, 2017) — source: OpenStreetMap contributors
  and Wambacher. OpenStreetMap data are published under the Open Database Licence
  (ODbL), <https://www.openstreetmap.org/copyright>.

geoBoundaries releases both files under CC BY 4.0; the upstream sources are named
here so that credit reaches them as well.

## Third-party libraries

The models use only the Python standard library. The figure scripts and the test
suite additionally use matplotlib (Matplotlib/PSF-style licence), NumPy
(BSD-3-Clause) and pytest (MIT). No code from these projects is redistributed in
this package; they are listed here for information only.
