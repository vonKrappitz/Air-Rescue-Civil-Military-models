"""Unit tests for economic_model.py, base case fee 65, growth 2.5 per cent.

Deterministic model, so headline values are checked to the unit. The private
partner keeps a contribution of 180, the readiness fee is 65, and the company
is valued at exit as a going concern at ten times the year-ten profit.
"""

import economic_model as em


# --- company simulation ---------------------------------------------------- #
def test_net_result_base():
    assert [round(x) for x in em.net_result()] == [3, 18, 31, 41, 48, 50, 54, 54, 57, 58]


def test_revenue_and_opex_year_ten():
    assert round(em.revenue()[-1]) == 152
    assert round(em.opex()[-1]) == 73


def test_break_even_year_one_at_fee_65():
    # the high readiness fee alone nearly covers cost, so profit is positive early
    assert em.break_even_year() == 1


# --- three value measures -------------------------------------------------- #
def test_three_value_measures():
    assert round(em.pv_operating()) == 492
    assert round(em.npv_project()) == 122          # positive at fee 65
    assert round(em.npv_project_new_money()) == 242


def test_initial_capital_structure():
    assert em.I0_PUBLIC == 190
    assert em.I0_PRIVATE == 180
    assert em.I0_TOTAL == 370
    assert abs(em.PRIVATE_SHARE - 0.49) < 1e-9


# --- private equity, H2 ---------------------------------------------------- #
def test_equity_npv_positive_at_fee_65():
    assert round(em.equity_npv()) == 7             # +6.8, H2 holds
    assert em.equity_npv() > 0


def test_equity_irr_clears_hurdle():
    irr = em.equity_irr()
    assert irr > em.HURDLE_PRIVATE                  # 10.5% > 10%
    assert round(irr * 100, 1) == 10.5


def test_fee_threshold_for_equity_breakeven():
    # F*, the fee at which the private equity NPV is zero
    assert round(em.fee_for_equity_breakeven()) == 63


def test_equity_underwater_at_old_fee():
    # at the original fee of 35 the private partner is deeply negative
    assert em.equity_npv(fee=35) < -100


# --- capability-equivalent public cost, H1 --------------------------------- #
def test_public_costs_consistent():
    assert round(em.public_cost_status_quo()) == 256
    assert round(em.public_cost_public_ownership()) == 425
    lo, hi = em.public_cost_availability()
    assert (round(lo), round(hi)) == (427, 512)
    assert round(em.public_cost_ppp(terminal="cash")) == 345       # in-kind fleet at full value
    assert round(em.public_cost_ppp(terminal="economic")) == 143    # economic view, stake valued


def test_terminal_value_is_single_source_of_truth():
    # guard against the earlier bug: private exit and state economic residual
    # must be shares of the same terminal company value, summing to the whole
    tcv = em.terminal_company_value()
    state_share = em.PUBLIC_SHARE * tcv
    private_share = em.PRIVATE_SHARE * tcv
    assert abs((state_share + private_share) - tcv) < 1e-9
    # the private exit used in the FCFE equals its share of the same tcv
    fcfe = em.private_fcfe()
    exit_in_fcfe = fcfe[-1] - em._dividends_private()[-1]
    assert abs(exit_in_fcfe - private_share) < 1e-6


def test_ppp_is_cheapest_capability_equivalent():
    d = em.public_cost_ppp(terminal="cash")               # even on the conservative view
    assert d < em.public_cost_public_ownership()          # beats public ownership
    assert d < em.public_cost_availability()[0]           # beats availability contract


def test_fiscal_saving_h1_both_views():
    assert round(em.fiscal_saving(terminal="cash")) == 80         # in-kind fleet at full value
    assert round(em.fiscal_saving(terminal="economic")) == 282    # stake valued
    lo, hi = em.public_cost_availability()
    assert round((lo + hi) / 2 - em.public_cost_ppp(terminal="cash")) == 125   # vs availability


# --- both hypotheses hold at the base case --------------------------------- #
def test_both_hypotheses_hold():
    assert em.equity_npv() > 0                     # H2
    assert em.fiscal_saving() > 0                  # H1


# --- conversion-saving split (review point 7) ------------------------------ #
def test_conversion_saving_split():
    # cash financing requirement excludes the avoided-replacement saving
    cash = em.cash_financing_requirement("mid", "mid")
    econ = em.incremental_economic_cost("mid", "mid")
    assert cash > econ                              # avoided cost lowers economic cost only
    # the difference is exactly the conversion saving
    conv = em.CONVERSION_SAVING["units"] * (em.CONVERSION_SAVING["low"] + em.CONVERSION_SAVING["high"]) / 2
    assert abs((cash - econ) - conv) < 1e-6


# --- investment balance, Table 3 (unchanged fleet-price sensitivity) ------- #
def test_table_3_net_balance():
    rows = {r["name"]: r for r in em.sensitivity_rows()}
    assert round(rows["Conservative (worst)"]["gross"]) == 5116
    assert round(rows["Central"]["gross"]) == 4528
    assert round(rows["Optimistic (best)"]["gross"]) == 3940
    assert round(rows["Conservative (worst)"]["net"]) == 4762
    assert round(rows["Central"]["net"]) == 4101
    assert round(rows["Optimistic (best)"]["net"]) == 3440


def test_table_3_present_values():
    rows = {r["name"]: r for r in em.sensitivity_rows()}
    assert tuple(round(rows["Central"]["pv"][r]) for r in (0.03, 0.04, 0.05)) == (3925, 3870, 3817)


# --- whole-of-system (world-cost) convention -------------------------------- #
def test_world_costs():
    assert round(em.world_cost_public_ownership()) == 681
    lo, hi = em.world_cost_availability()
    assert (round(lo), round(hi)) == (682, 768)
    assert round(em.world_resource_cost()) == 601
    assert round(em.world_budgetary_outlay()) == 481
    assert round(em.world_economic_cost()) == 399


def test_world_saving_invariant_to_convention():
    # the world convention must reproduce the same differences as the net one
    assert round(em.world_saving("resource")) == round(em.fiscal_saving(terminal="cash"))
    assert round(em.world_saving("resource")) == 80
    old_economic_saving = em.public_cost_public_ownership() - em.economic_cost()
    assert round(em.world_saving("economic")) == round(old_economic_saving) == 282


def test_symmetric_withdrawal_gap_disclosed():
    # if the legacy fleet were withdrawn in every variant, the advantage reverses
    assert round(em.symmetric_withdrawal_gap()) == -176


def test_stake_rate_sensitivity():
    rows = em.stake_rate_sensitivity()
    assert [round(r["economic"]) for r in rows] == [399, 437, 482, 505]
    savings = [r["saving"] for r in rows]
    assert savings == sorted(savings, reverse=True)
    assert round(savings[0]) == 282 and round(savings[-1]) == 176
