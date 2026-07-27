"""figure_zones.py

Generate the zone matrix of the paper, the central figure of the appraisal.
The readiness fee is on the vertical axis and the company's mature annual
commercial revenue on the horizontal axis. Each point is coloured by which
parties the arrangement satisfies, computed by economic_model.py so the figure
is reproducible and consistent with the tables.

    red    the private partner's equity NPV is negative, no investor takes it
    amber  the private partner is satisfied but the state does not save against
           a capability-equivalent all-public operator
    green  both sides win, the only region where the PPP is viable

The base case, a readiness fee of 65 and the base commercial revenue, is marked.

Run it with

    python figure_zones.py

and it writes figure_zones.png next to the script.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

import economic_model as em

_HERE = os.path.dirname(os.path.abspath(__file__))

RED = "#4a4a4a"      # dark grey, private partner loses
AMBER = "#9e9e9e"    # medium grey, private wins but state does not save
GREEN = "#e2e2e2"    # light grey, both sides win
GROWTH = em.COMMERCIAL_GROWTH


def _net_result(fee, scale):
    com = [em.COMMERCIAL_RAMP[k] * scale * (1 + GROWTH) ** k for k in range(em.HORIZON)]
    ox = [em.OPEX_BASE[k] + em.MARGINAL_COST * em.COMMERCIAL_RAMP[k] * scale * ((1 + GROWTH) ** k - 1)
          for k in range(em.HORIZON)]
    return [fee + com[k] - ox[k] - em.DEPRECIATION for k in range(em.HORIZON)]


def _equity_npv(fee, scale):
    wn = _net_result(fee, scale)
    div = [(wn[i - 1] * (1 - em.REINVEST_SHARE) * em.PRIVATE_SHARE)
           if (i >= 1 and wn[i - 1] > 0) else 0.0 for i in range(em.HORIZON)]
    exit_value = em.PRIVATE_SHARE * em.EXIT_MULTIPLE * wn[-1]
    fcfe = [-em.I0_PRIVATE] + [div[k] + (exit_value if k == em.HORIZON - 1 else 0.0)
                              for k in range(em.HORIZON)]
    return sum(cf / (1 + em.HURDLE_PRIVATE) ** t for t, cf in enumerate(fcfe))


def _fiscal_saving(fee, scale):
    wn = _net_result(fee, scale)
    div_public = sum((wn[i - 1] * em.PUBLIC_SHARE * (1 - em.REINVEST_SHARE)) / (1 + em.SOCIAL_RATE) ** (i + 1)
                     for i in range(1, em.HORIZON) if wn[i - 1] > 0)
    outlay = em.IN_KIND_FLEET + em.PUBLIC_CASH + em.annuity(fee)
    residual_state = em.PUBLIC_SHARE * em.RESIDUAL_VALUE / (1 + em.SOCIAL_RATE) ** em.HORIZON
    d = outlay - div_public - em.annuity(em.MAINT_PUBLIC_FLEET) - residual_state
    return em.public_cost_public_ownership() - d


def zone(fee, scale):
    if _equity_npv(fee, scale) < 0:
        return 0
    if _fiscal_saving(fee, scale) <= 0:
        return 1
    return 2


def mature_commercial(scale):
    return em.COMMERCIAL_RAMP[-1] * scale * (1 + GROWTH) ** (em.HORIZON - 1)


def main():
    fees = np.linspace(30, 100, 220)
    scales = np.linspace(0.5, 2.0, 220)
    grid = np.zeros((len(fees), len(scales)))
    for i, fee in enumerate(fees):
        for j, scale in enumerate(scales):
            grid[i, j] = zone(fee, scale)

    x = np.array([mature_commercial(s) for s in scales])
    fig, ax = plt.subplots(figsize=(8.2, 6.0))
    cmap = matplotlib.colors.ListedColormap([RED, AMBER, GREEN])
    ax.pcolormesh(x, fees, grid, cmap=cmap, vmin=0, vmax=2, shading="auto")

    # base case marker
    base_x = mature_commercial(1.0)
    ax.plot(base_x, em.READINESS_FEE, "o", color="white", markersize=11,
            markeredgecolor="black", markeredgewidth=1.6, zorder=5)
    ax.annotate("base case\nfee 65", (base_x, em.READINESS_FEE),
                textcoords="offset points", xytext=(10, 10),
                fontsize=10, fontweight="bold", color="black")

    ax.set_xlabel("mature annual commercial revenue, million PLN", fontsize=11)
    ax.set_ylabel("annual readiness fee, million PLN", fontsize=11)
    ax.set_title("Where the public-private reserve is viable", fontsize=13, fontweight="bold")

    # in-figure region labels, so the zones read without relying on shade alone
    ax.text(52, 41, "private\npartner\nloses", fontsize=11, ha="center", va="center",
            color="white", fontweight="bold")
    ax.text(70, 93, "private wins,\nstate does not save", fontsize=11, ha="center",
            va="center", color="black", fontweight="bold")
    ax.text(145, 47, "both sides win", fontsize=11, ha="center", va="center",
            color="black", fontweight="bold")

    legend = [Patch(facecolor=RED, edgecolor="black", linewidth=0.4, label="private partner loses"),
              Patch(facecolor=AMBER, edgecolor="black", linewidth=0.4, label="private wins, state does not save"),
              Patch(facecolor=GREEN, edgecolor="black", linewidth=0.4, label="both sides win")]
    ax.legend(handles=legend, loc="lower right", framealpha=0.95, fontsize=9.5)
    ax.tick_params(labelsize=10)
    fig.tight_layout()
    out = os.path.join(_HERE, "figure_zones.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")
    # sanity report
    print(f"base case zone (fee 65, scale 1.0): {zone(em.READINESS_FEE, 1.0)} (2 = both win)")
    print(f"  equity NPV = {_equity_npv(em.READINESS_FEE, 1.0):.1f}, "
          f"fiscal saving = {_fiscal_saving(em.READINESS_FEE, 1.0):.1f}")


if __name__ == "__main__":
    main()
