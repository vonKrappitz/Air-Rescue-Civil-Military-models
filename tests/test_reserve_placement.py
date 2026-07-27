"""Unit tests for reserve_placement.py.

The optimum set, the combination count and the boundary source are exact. With
the bundled geoBoundaries outline the reach figures reproduce the paper, so the
minute assertions are tight, allowing only sub-minute rounding.
"""

from itertools import combinations

import reserve_placement as rp

# Computed once and shared, the grid and the optimum are the costly steps.
GRID = rp.land_grid()
BEST = rp.optimal_placement(GRID)
CIVIL = [rp.CANDIDATES[c] for c in BEST["bases"]]
TWO_PILLAR = CIVIL + list(rp.NAVY_BASE.values())


def test_combination_count_is_35():
    assert len(list(combinations(rp.CANDIDATES, rp.RESERVE_SIZE))) == 35


def test_boundary_loaded():
    assert len(rp.POLAND_BOUNDARY) > 500            # full national outline
    lats = [p[0] for p in rp.POLAND_BOUNDARY]
    lons = [p[1] for p in rp.POLAND_BOUNDARY]
    assert 48.9 < min(lats) < 49.2 and 54.7 < max(lats) < 55.0
    assert 14.0 < min(lons) < 14.3 and 24.0 < max(lons) < 24.3


def test_haversine_known_distance():
    # Warszawa to Krakow is about 252 km.
    d = rp.haversine_km(rp.CANDIDATES["Warszawa"], rp.CANDIDATES["Krakow"])
    assert 245 < d < 260


def test_optimum_is_the_four_dispersed_centres():
    assert set(BEST["bases"]) == {"Krakow", "Lublin", "Poznan", "Olsztyn"}


def test_single_pillar_worst_case_about_58():
    assert 57.5 <= BEST["worst"] <= 59.5            # 58.6 with this boundary


def test_conventional_set_is_worse_about_70():
    conv = [rp.CANDIDATES[c] for c in rp.CONVENTIONAL]
    conv_wc, _ = rp.worst_case_reach(conv, GRID)
    assert conv_wc > BEST["worst"]
    assert 69 <= conv_wc <= 71                      # 69.8 with this boundary


def test_two_pillar_worst_case_about_57():
    tp_wc, _ = rp.worst_case_reach(TWO_PILLAR, GRID)
    assert 56.5 <= tp_wc <= 58.0                    # 57.3 with this boundary


def test_central_coast_is_slowest_civil_margin():
    civil_ref = rp.reach_to_reference(CIVIL)
    coast = "Central Baltic coast (Rowy)"
    assert 57.0 <= civil_ref[coast] <= 59.0          # about 58, the slowest civil margin


def test_darlowo_cuts_nw_corner_to_about_37():
    civil_ref = rp.reach_to_reference(CIVIL)
    tp_ref = rp.reach_to_reference(TWO_PILLAR)
    nw = "NW corner (Swinoujscie)"
    assert 56.5 <= civil_ref[nw] <= 59.0             # about 58 before Darlowo
    assert 36.0 <= tp_ref[nw] <= 39.0                # about 37 after Darlowo


def test_southern_salients_are_the_residual_about_57():
    tp_ref = rp.reach_to_reference(TWO_PILLAR)
    for salient in ("SW salient (Klodzko)", "SE salient (Bieszczady)"):
        assert 56.0 <= tp_ref[salient] <= 58.5       # about 57, unhelped by Darlowo
    # the two are within a tenth of a minute of each other, a near tie
    assert abs(tp_ref["SW salient (Klodzko)"] - tp_ref["SE salient (Bieszczady)"]) < 0.5


# --- H3, spatial availability of the military pillar ----------------------- #
def _h3_setup():
    import reserve_placement as rp
    grid = rp.land_grid()
    civil, navy = rp.standard_coords(grid)
    return rp, grid, civil, navy


def test_h3_holds():
    rp, grid, civil, navy = _h3_setup()
    assert rp.h3_holds(grid, civil, navy) is True


def test_h3_coverage_at_45_min():
    rp, grid, civil, navy = _h3_setup()
    row = {r["threshold"]: r for r in rp.h3_coverage_table(grid, civil, navy)}[45]
    assert abs(row["civil_only"] - 0.905) < 0.005          # civil bases alone
    assert abs(row["by_availability"][0.25] - 0.916) < 0.005
    assert abs(row["full"] - 0.950) < 0.005                # military always free


def test_h3_coverage_at_60_min_is_full():
    rp, grid, civil, navy = _h3_setup()
    row = {r["threshold"]: r for r in rp.h3_coverage_table(grid, civil, navy)}[60]
    assert row["civil_only"] > 0.999                        # civil fleet already covers all


def test_h3_coverage_monotone_in_availability():
    rp, grid, civil, navy = _h3_setup()
    cov = [rp.coverage_within(grid, civil, navy, 45, p) for p in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert cov == sorted(cov)                               # more availability, more coverage
    assert cov[-1] > cov[0]


def test_h3_expected_reach_falls_with_availability():
    rp, grid, civil, navy = _h3_setup()
    reach = [rp.expected_reach(grid, civil, navy, p) for p in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert reach == sorted(reach, reverse=True)             # more availability, lower reach


def test_coverage_exactly_linear_in_availability():
    rp, grid, civil, navy = _h3_setup()
    c0 = rp.coverage_within(grid, civil, navy, 45, 0.0)
    c1 = rp.coverage_within(grid, civil, navy, 45, 1.0)
    for p in (0.1, 0.33, 0.5, 0.77):
        expected = c0 + p * (c1 - c0)
        assert abs(rp.coverage_within(grid, civil, navy, 45, p) - expected) < 1e-12
