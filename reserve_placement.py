"""reserve_placement.py

Dispersed placement of the four civil AW101 heavy all-weather helicopters.

This script regenerates Appendix 2 of:

    M. M. Kasperek (2026). Civil-military integration of a reformed national
    air-rescue network. Defence and Peace Economics (preprint).

The placement follows a discrete p-centre (minimax) rule. The candidate set is
the seven Regional Centres of the reformed network. The model selects the four
that minimise the worst-case reach to any land point of Poland, by exhaustive
enumeration of all C(7,4) = 35 combinations, so the result is a global optimum
and not a heuristic.

Reach is straight-line (great-circle) distance divided by a cruise speed of
278 km/h, with five minutes added for start-up. It is evaluated over a land grid
of five-kilometre spacing built from a national boundary of Poland.

The two-pillar variant adds the Navy base at Darlowo to the four civil bases and
reports the reduced worst-case reach, in particular on the Baltic coast.

The boundary is loaded from poland_boundary.geojson, the country outline (ADM0)
from the geoBoundaries open database (gbOpen release, ISO POL). With this
boundary the model reproduces the paper. The optimum is Krakow, Lublin, Poznan
and Olsztyn. The single-pillar worst case is 58.6 minutes, at the central
Baltic coast near Rowy, against 69.8 for the conventional four-city set. The
Navy base at Darlowo sits on that same central stretch of coast, 48 km from the
worst point, so adding it brings the central coast within about 15 minutes and
the north-western corner within about 37. The country-wide two-pillar worst case
is 57.3 minutes, at the southern mountain salients, Klodzko in the south-west and
the Bieszczady in the south-east, a near tie. On a five-kilometre grid the
single-pillar worst case falls between 58 and 59 minutes depending on which
coastal cell is sampled, consistent with the paper's about 58.
"""

import json
import math
import os
from itertools import combinations

# --------------------------------------------------------------------------- #
# Parameters (Appendix 2)
# --------------------------------------------------------------------------- #
CRUISE_KMH = 278          # AW101 cruise
STARTUP_MIN = 5           # added to every reach
GRID_KM = 5               # land-grid spacing
RESERVE_SIZE = 4          # civil AW101 to place

EARTH_RADIUS_KM = 6371.0

# Candidate bases, the seven Regional Centres (latitude, longitude)
CANDIDATES = {
    "Warszawa": (52.23, 21.01),
    "Krakow": (50.06, 19.94),
    "Wroclaw": (51.11, 17.03),
    "Gdansk": (54.35, 18.65),
    "Lublin": (51.25, 22.57),
    "Poznan": (52.41, 16.93),
    "Olsztyn": (53.78, 20.49),
}

# The conventional four-city set, used as a reference point in the paper
CONVENTIONAL = ("Warszawa", "Krakow", "Wroclaw", "Gdansk")

# The Navy base added in the two-pillar variant
NAVY_BASE = {"Darlowo": (54.42, 16.41)}

# Reference points named in the paper, reported for context. Reaches are the
# values this script computes, so the labels are backed by the data.
REFERENCE_POINTS = {
    "Central Baltic coast (Rowy)": (54.66, 17.03),    # slowest civil margin, ~58
    "NW corner (Swinoujscie)": (53.92, 14.27),        # worst coastal point once Darlowo is added, ~37
    "SW salient (Klodzko)": (50.10, 16.55),           # southern residual, ~57
    "SE salient (Bieszczady)": (49.01, 22.88),        # southern residual, ~57
}

_HERE = os.path.dirname(os.path.abspath(__file__))
BOUNDARY_FILE = os.path.join(_HERE, "poland_boundary.geojson")


def load_boundary(path=BOUNDARY_FILE):
    """Load the Poland outline and return its mainland ring as (lat, lon) points.

    The file is a GeoJSON country outline (geoBoundaries ADM0, ISO POL). GeoJSON
    stores coordinates as (lon, lat), so they are swapped to (lat, lon) here. The
    largest ring is the mainland and is the one used for the land grid.
    """
    with open(path, encoding="utf-8") as handle:
        gj = json.load(handle)
    geom = gj["features"][0]["geometry"]
    if geom["type"] == "MultiPolygon":
        rings = [ring for polygon in geom["coordinates"] for ring in polygon]
    else:
        rings = geom["coordinates"]
    mainland = max(rings, key=len)
    return [(lat, lon) for lon, lat in mainland]


POLAND_BOUNDARY = load_boundary()


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
def haversine_km(p1, p2):
    """Great-circle distance between two (lat, lon) points, in kilometres."""
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def reach_min(distance_km):
    """Reach in minutes, flight time at cruise plus start-up."""
    return distance_km / CRUISE_KMH * 60 + STARTUP_MIN


def point_in_polygon(point, polygon):
    """Ray-casting test. point is (lat, lon), polygon a list of (lat, lon)."""
    lat, lon = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]
        if ((lon_i > lon) != (lon_j > lon)) and \
           (lat < (lat_j - lat_i) * (lon - lon_i) / (lon_j - lon_i) + lat_i):
            inside = not inside
        j = i
    return inside


def land_grid(polygon=POLAND_BOUNDARY, spacing_km=GRID_KM):
    """Generate land points on an approximately uniform grid inside the polygon."""
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    dlat = spacing_km / 111.32
    grid = []
    lat = lat_min
    while lat <= lat_max:
        dlon = spacing_km / (111.32 * math.cos(math.radians(lat)))
        lon = lon_min
        while lon <= lon_max:
            if point_in_polygon((lat, lon), polygon):
                grid.append((lat, lon))
            lon += dlon
        lat += dlat
    return grid


# --------------------------------------------------------------------------- #
# p-centre
# --------------------------------------------------------------------------- #
def worst_case_reach(base_coords, grid):
    """Maximum over land points of the reach to the nearest base, in minutes.

    Returns the worst-case reach and the land point that attains it.
    """
    worst = -1.0
    worst_point = None
    for p in grid:
        nearest = min(haversine_km(p, b) for b in base_coords)
        r = reach_min(nearest)
        if r > worst:
            worst = r
            worst_point = p
    return worst, worst_point


def optimal_placement(grid, size=RESERVE_SIZE):
    """Exhaustive minimax over all combinations of the candidate set."""
    best = None
    for combo in combinations(CANDIDATES, size):
        coords = [CANDIDATES[c] for c in combo]
        wc, point = worst_case_reach(coords, grid)
        if best is None or wc < best["worst"]:
            best = dict(bases=combo, worst=wc, worst_point=point)
    return best


def reach_to_reference(base_coords):
    """Reach in minutes to each named reference point."""
    out = {}
    for name, coord in REFERENCE_POINTS.items():
        nearest = min(haversine_km(coord, b) for b in base_coords)
        out[name] = reach_min(nearest)
    return out


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def main():
    grid = land_grid()
    n_combos = len(list(combinations(CANDIDATES, RESERVE_SIZE)))
    print(f"Boundary vertices: {len(POLAND_BOUNDARY)}  (geoBoundaries ADM0, ISO POL)")
    print(f"Land grid points (about {GRID_KM} km spacing): {len(grid)}")
    print(f"Candidate combinations C(7,4): {n_combos}")

    best = optimal_placement(grid)
    print("\nSingle-pillar optimum (four civil AW101)")
    print(f"  Bases        : {', '.join(best['bases'])}")
    print(f"  Worst-case   : {best['worst']:.1f} min "
          f"at ({best['worst_point'][0]:.2f}, {best['worst_point'][1]:.2f})")

    conv_coords = [CANDIDATES[c] for c in CONVENTIONAL]
    conv_wc, conv_pt = worst_case_reach(conv_coords, grid)
    print(f"\nConventional four-city set ({', '.join(CONVENTIONAL)})")
    print(f"  Worst-case   : {conv_wc:.1f} min "
          f"at ({conv_pt[0]:.2f}, {conv_pt[1]:.2f})")

    two_pillar = [CANDIDATES[c] for c in best["bases"]] + list(NAVY_BASE.values())
    tp_wc, tp_pt = worst_case_reach(two_pillar, grid)
    print(f"\nTwo-pillar (four civil bases plus {list(NAVY_BASE)[0]})")
    print(f"  Worst-case   : {tp_wc:.1f} min "
          f"at ({tp_pt[0]:.2f}, {tp_pt[1]:.2f})")

    print("\nReach to reference points (minutes)")
    civil = [CANDIDATES[c] for c in best["bases"]]
    civil_ref = reach_to_reference(civil)
    tp_ref = reach_to_reference(two_pillar)
    for name in REFERENCE_POINTS:
        print(f"  {name:<30} civil {civil_ref[name]:>5.1f}   two-pillar {tp_ref[name]:>5.1f}")


if __name__ == "__main__":
    main()
