"""Unit tests for economic_model.py.

Every figure is checked against Tables 2 and 3 of Appendix 1. The economic model
is deterministic, so these assertions are exact to the unit.
"""

import economic_model as em


def test_net_result_matches_table_2():
    expected = [-23, -10, 2, 20, 32, 36, 39, 40, 42, 42]
    assert em.net_result(em.REVENUE) == expected


def test_free_cash_flow_matches_table_2():
    expected = [-8, 5, 17, 35, 47, 42, 54, 55, 57, 57]
    assert em.free_cash_flow(em.REVENUE) == expected


def test_nominal_cash_flow_matches_table_2():
    cf_real = em.free_cash_flow(em.REVENUE)
    cf_nom = [round(x) for x in em.nominal_flow(cf_real)]
    assert cf_nom == [-8, 5, 18, 39, 53, 49, 64, 67, 71, 73]
    assert round(em.nominal_flow([em.RESIDUAL_VALUE] * 10)[9]) == 64


def test_npv_is_307():
    assert round(em.npv(em.free_cash_flow(em.REVENUE))) == 307


def test_fisher_real_and_nominal_npv_agree():
    cf_real = em.free_cash_flow(em.REVENUE)
    cf_nom = em.nominal_flow(cf_real)
    r_nom = em.fisher_rate()
    resid_nom = em.RESIDUAL_VALUE * (1 + em.INFLATION) ** em.HORIZON
    npv_real = em.npv(cf_real)
    npv_nom = em.npv(cf_nom, rate=r_nom, residual=resid_nom)
    assert abs(npv_real - npv_nom) < 0.01


def test_optimistic_npv_is_437_at_quarter_uplift():
    uplift = em.solve_uplift_for_target(437)
    assert abs(uplift - 1.25) < 0.01            # about a quarter
    assert round(em.npv(em.commercial_uplift_flow(uplift))) == 437


def test_cumulative_and_treasury():
    wn = em.net_result(em.REVENUE)
    cum = []
    s = 0
    for x in wn:
        s += x
        cum.append(s)
    assert cum[-1] == 220                         # cumulative over the decade
    assert cum[8] == 178                          # pool through year nine
    assert round(em.dividend_to_treasury(cum[8])) == 77
    assert round(em.dividend_to_treasury(cum[8]) + em.FLEET_MAINTENANCE_SAVING) == 377


def test_table_3_net_balance():
    rows = {r["name"]: r for r in em.sensitivity_rows()}
    assert round(rows["Conservative (worst)"]["gross"]) == 5116
    assert round(rows["Optimistic (best)"]["gross"]) == 3940
    assert round(rows["Central"]["gross"]) == 4528
    assert round(rows["Conservative (worst)"]["comp"]) == 354
    assert round(rows["Optimistic (best)"]["comp"]) == 500
    assert round(rows["Central"]["comp"]) == 427
    assert round(rows["Conservative (worst)"]["net"]) == 4762
    assert round(rows["Central"]["net"]) == 4101
    assert round(rows["Optimistic (best)"]["net"]) == 3440


def test_table_3_present_values():
    rows = {r["name"]: r for r in em.sensitivity_rows()}
    pv = rows["Conservative (worst)"]["pv"]
    assert (round(pv[0.03]), round(pv[0.04]), round(pv[0.05])) == (4558, 4494, 4433)
    pv = rows["Central"]["pv"]
    assert (round(pv[0.03]), round(pv[0.04]), round(pv[0.05])) == (3925, 3870, 3817)
    pv = rows["Optimistic (best)"]["pv"]
    assert (round(pv[0.03]), round(pv[0.04]), round(pv[0.05])) == (3293, 3247, 3202)
