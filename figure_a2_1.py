"""figure_a2_1.py

Generate Figure A2.1 of the paper, the reach-time map of the two-pillar AW101
reserve. Every land point of Poland is coloured by its reach in minutes to the
nearest reserve base, for the four civil Regional Centres (Krakow, Lublin,
Poznan, Olsztyn) plus the Navy base at Darlowo. The civil bases are drawn as
stars, the Navy base as a triangle, and the two residual critical points, the
southern mountain salients near Klodzko and in the Bieszczady, as crosses.
Voivodeship borders are drawn for orientation.

Everything is computed by reserve_placement.py, so the figure is reproducible
and consistent with the placement results. The whole northern coast is brought
in close by Darlowo, and the binding margin moves to the two southern mountain
salients, both about 57 minutes.

This script needs matplotlib and numpy (see requirements.txt). Run it with

    python figure_a2_1.py

and it writes figure_A2_1.png next to the script.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

import reserve_placement as rp

_HERE = os.path.dirname(os.path.abspath(__file__))
VOIVODESHIP_FILE = os.path.join(_HERE, "poland_voivodeships.geojson")

CIVIL = ("Krakow", "Lublin", "Poznan", "Olsztyn")
CITY_LABELS = {
    "Krakow": "Krakow", "Lublin": "Lublin", "Poznan": "Poznan", "Olsztyn": "Olsztyn",
}
RESIDUAL = {"Klodzko": (50.10, 16.55), "Bieszczady": (49.01, 22.88)}

# Greyscale palette for print. Reach is a light-to-dark grey ramp and the
# markers are distinguished by shape, so the map reads in black and white.
CIVIL_COLOR = "#111111"      # near-black star
NAVY_COLOR = "#666666"       # mid-grey triangle
BORDER_COLOR = "#9aa0a8"     # voivodeship lines
OUTLINE_COLOR = "#202020"    # national outline
CMAP = LinearSegmentedColormap.from_list("reach_grey", ["#cfcfcf", "#1a1a1a"])
VMIN, VMAX = 5, 60


def _rings(geojson_path):
    """Return every polygon ring as a list of (lon, lat) pairs."""
    with open(geojson_path, encoding="utf-8") as handle:
        gj = json.load(handle)
    rings = []
    for feature in gj["features"]:
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "Polygon" else \
            [ring for poly in geom["coordinates"] for ring in poly]
        if geom["type"] == "Polygon":
            polys = geom["coordinates"]
            for ring in polys:
                rings.append(ring)
        else:
            for poly in geom["coordinates"]:
                for ring in poly:
                    rings.append(ring)
    return rings


def make_figure(path="figure_A2_1.png", dot_spacing_km=6, dot_size=6):
    civil = [rp.CANDIDATES[c] for c in CIVIL]
    darlowo = list(rp.NAVY_BASE.values())[0]
    bases = civil + [darlowo]

    # Dotted reach field on a uniform land grid
    dots = rp.land_grid(spacing_km=dot_spacing_km)
    dlat = [p[0] for p in dots]
    dlon = [p[1] for p in dots]
    reach = [rp.reach_min(min(rp.haversine_km(p, b) for b in bases)) for p in dots]

    fig, ax = plt.subplots(figsize=(11, 9.5))

    scatter = ax.scatter(dlon, dlat, c=reach, cmap=CMAP, vmin=VMIN, vmax=VMAX,
                         s=33, marker="o", linewidths=0, zorder=2)

    # Voivodeship borders, then the national outline on top
    for ring in _rings(VOIVODESHIP_FILE):
        ax.plot([p[0] for p in ring], [p[1] for p in ring],
                color=BORDER_COLOR, linewidth=0.4, zorder=3)
    poly = rp.POLAND_BOUNDARY
    ax.plot([p[1] for p in poly], [p[0] for p in poly],
            color=OUTLINE_COLOR, linewidth=1.1, zorder=4)

    # Civil Regional Centres as navy stars with bold labels
    ax.scatter([c[1] for c in civil], [c[0] for c in civil], marker="*", s=430,
               color=CIVIL_COLOR, edgecolors="white", linewidths=0.7, zorder=6)
    for name in CIVIL:
        lat, lon = rp.CANDIDATES[name]
        ax.annotate(CITY_LABELS[name], (lon, lat), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=12, fontweight="bold",
                    color="black", zorder=7)

    # Navy base as a purple triangle
    ax.scatter([darlowo[1]], [darlowo[0]], marker="^", s=200, color=NAVY_COLOR,
               edgecolors="white", linewidths=0.7, zorder=6)
    ax.annotate("Darlowo (Navy)", (darlowo[1], darlowo[0]),
                textcoords="offset points", xytext=(0, 14), ha="center",
                fontsize=12, fontweight="bold", color="black", zorder=7)

    # The two residual critical points as black crosses
    for coord in RESIDUAL.values():
        ax.scatter([coord[1]], [coord[0]], marker="X", s=230, color="black",
                   edgecolors="white", linewidths=0.8, zorder=8)

    # Clean map, no axes
    ax.set_aspect(1 / np.cos(np.radians(52.0)))
    ax.axis("off")
    ax.set_title(
        "Two-pillar AW101 reserve. Four civil Regional Centres and the Navy base at Darlowo.\n"
        "Worst-case national reach about 57 minutes. Baltic coast cut from 58 to 37 minutes.",
        fontsize=12.5)

    cbar = fig.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("AW101 reach time [min]", rotation=270, labelpad=18, fontsize=11)

    handles = [
        Line2D([0], [0], marker="*", color="none", markerfacecolor=CIVIL_COLOR,
               markeredgecolor="white", markersize=18, label="Civil AW101 (Regional Centre)"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor=NAVY_COLOR,
               markeredgecolor="white", markersize=13, label="Military AW101 (Darlowo)"),
        Line2D([0], [0], marker="X", color="none", markerfacecolor="black",
               markeredgecolor="white", markersize=13, label="residual critical point"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=10.5, framealpha=0.95)

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


if __name__ == "__main__":
    out = make_figure()
    print(f"Wrote {out}")
