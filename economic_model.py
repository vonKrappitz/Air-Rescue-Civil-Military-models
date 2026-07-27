"""economic_model.py

Ex ante economic appraisal of a public-private air-medical mobilisation reserve
for Poland. The model compares capability-equivalent ways of providing a defined
intercontinental MEDEVAC readiness and tests three hypotheses.

    H1  For an identical readiness output, the discounted public cost of the
        LEM-PPP model is lower than a capability-equivalent all-public operator.
    H2  Under the conservative commercial-demand scenario, the private partner's
        equity NPV is non-negative at the assumed required rate of return.
    (H3 is the spatial-availability test in reserve_placement.py.)

All amounts are in million PLN, constant 2026 prices. The model is deterministic
and every headline value is reproduced to the unit by the test suite.

Reference for M. M. Kasperek (2026), Defence and Peace Economics (preprint).
"""

# --------------------------------------------------------------------------- #
# 1. Base-case parameters
# --------------------------------------------------------------------------- #
HORIZON = 10

# Capital structure at t = 0. The public side contributes the existing long-range
# fleet in kind (two Learjet 75 and one Piaggio Avanti II, about 120 at current
# value) plus a cash top-up. The private partner contributes cash of 180.
IN_KIND_FLEET = 120
PUBLIC_CASH = 70
PRIVATE_CONTRIBUTION = 180
I0_PUBLIC = IN_KIND_FLEET + PUBLIC_CASH        # 190
I0_PRIVATE = PRIVATE_CONTRIBUTION              # 180
I0_TOTAL = I0_PUBLIC + I0_PRIVATE              # 370

PUBLIC_SHARE = 0.51
PRIVATE_SHARE = 1 - PUBLIC_SHARE               # 0.49
REINVEST_SHARE = 0.15

# Readiness fee. The state pays the company an annual fee to hold the capability
# on standby. It is the central lever of the appraisal and is varied in the
# threshold analysis.
READINESS_FEE = 65

# Commercial revenue. A utilisation ramp as the operation matures, then modest
# organic growth at 2.5 per cent a year, well below the market rate of about ten
# to eleven per cent, so the base case does not lean on optimistic demand.
COMMERCIAL_RAMP = [24, 38, 50, 59, 64, 66, 68, 68, 69, 70]
COMMERCIAL_GROWTH = 0.025

# Operating cost. A fixed readiness cost plus a marginal cost on the commercial
# volume that grows beyond the base ramp. MARGINAL_COST is the variable cost per
# unit of extra commercial revenue.
OPEX_BASE = [65, 65, 65, 65, 65, 66, 66, 67, 67, 68]
MARGINAL_COST = 0.30

DEPRECIATION = 21                              # whole fleet ~311 m over 15 years
CAPEX = [3, 3, 3, 3, 3, 12, 3, 3, 3, 3]        # routine plus a mid-life refit
RESIDUAL_VALUE = 50                            # real terminal fleet value, year 10

# Rates
FINANCIAL_RATE = 0.04                          # company appraisal, real
SOCIAL_RATE = 0.03                             # public balance
INFLATION = 0.025
HURDLE_PRIVATE = 0.10                           # private required return, real
EXIT_MULTIPLE = 10                              # going-concern exit, times year-10 profit

# Counterfactual parameters
MAINT_PUBLIC_FLEET = 30                         # current fixed-wing upkeep, a year
FIXED_READINESS = 40                            # public readiness cost, no commercial
XRS_CAPEX = 121                                 # buy and convert two long-range jets
AVAILABILITY_FEE = (50, 60)                      # pure availability contract, a year


# --------------------------------------------------------------------------- #
# 2. Company simulation
# --------------------------------------------------------------------------- #
def commercial(growth=COMMERCIAL_GROWTH):
    return [COMMERCIAL_RAMP[k] * (1 + growth) ** k for k in range(HORIZON)]


def opex(growth=COMMERCIAL_GROWTH):
    return [OPEX_BASE[k] + MARGINAL_COST * COMMERCIAL_RAMP[k] * ((1 + growth) ** k - 1)
            for k in range(HORIZON)]


def revenue(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    com = commercial(growth)
    return [fee + com[k] for k in range(HORIZON)]


def net_result(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    rev = revenue(fee, growth)
    ox = opex(growth)
    return [rev[k] - ox[k] - DEPRECIATION for k in range(HORIZON)]


def free_cash_flow(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    wn = net_result(fee, growth)
    return [wn[k] + DEPRECIATION - CAPEX[k] for k in range(HORIZON)]


def npv(flow, rate, residual=0.0):
    pv = sum(flow[k] / (1 + rate) ** (k + 1) for k in range(len(flow)))
    return pv + residual / (1 + rate) ** HORIZON


def annuity(amount, rate=SOCIAL_RATE, years=HORIZON):
    return sum(amount / (1 + rate) ** t for t in range(1, years + 1))


# --------------------------------------------------------------------------- #
# 3. Three value measures
# --------------------------------------------------------------------------- #
def pv_operating(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Present value of operating flows plus residual, before the t=0 capital."""
    return npv(free_cash_flow(fee, growth), FINANCIAL_RATE, RESIDUAL_VALUE)


def npv_project(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Project NPV with the full initial capital at t = 0."""
    return pv_operating(fee, growth) - I0_TOTAL


def npv_project_new_money(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Project NPV counting only new cash at t = 0, the in-kind fleet excluded."""
    return pv_operating(fee, growth) - (PUBLIC_CASH + I0_PRIVATE)


def break_even_year(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """First year with a positive annual accounting result."""
    wn = net_result(fee, growth)
    for k in range(HORIZON):
        if wn[k] > 0:
            return k + 1
    return None


# --------------------------------------------------------------------------- #
# 4. Private-equity cash flow (H2)
# --------------------------------------------------------------------------- #
def _dividends_private(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Private share of dividends, declared on the prior year's positive profit."""
    wn = net_result(fee, growth)
    return [(wn[i - 1] * (1 - REINVEST_SHARE) * PRIVATE_SHARE)
            if (i >= 1 and wn[i - 1] > 0) else 0.0 for i in range(HORIZON)]


def terminal_company_value(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH,
                           exit_multiple=EXIT_MULTIPLE):
    """Going-concern value of the whole company at year 10.

    Single source of truth for the terminal value, used by both the private
    exit and the state's economic residual, so the two cannot diverge.
    """
    return exit_multiple * net_result(fee, growth)[-1]


def private_fcfe(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, exit_multiple=EXIT_MULTIPLE):
    """Free cash flow to the private partner, t = 0..10.

    Contribution at t = 0, dividends each year, and the resale of the 49 per cent
    stake at year 10 valued as a going concern at exit_multiple times profit.
    """
    div = _dividends_private(fee, growth)
    exit_value = PRIVATE_SHARE * terminal_company_value(fee, growth, exit_multiple)
    return [-I0_PRIVATE] + [div[k] + (exit_value if k == HORIZON - 1 else 0.0)
                            for k in range(HORIZON)]


def equity_npv(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, rate=HURDLE_PRIVATE,
               exit_multiple=EXIT_MULTIPLE):
    fcfe = private_fcfe(fee, growth, exit_multiple)
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(fcfe))


def equity_irr(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, exit_multiple=EXIT_MULTIPLE):
    fcfe = private_fcfe(fee, growth, exit_multiple)
    lo, hi = -0.9, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        v = sum(cf / (1 + mid) ** t for t, cf in enumerate(fcfe))
        if v > 0:
            lo = mid
        else:
            hi = mid
    return mid


def equity_payback(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, exit_multiple=EXIT_MULTIPLE):
    """First year the undiscounted cumulative FCFE turns non-negative."""
    fcfe = private_fcfe(fee, growth, exit_multiple)
    cum = 0.0
    for t, cf in enumerate(fcfe):
        cum += cf
        if t > 0 and cum >= 0:
            return t
    return None


# --------------------------------------------------------------------------- #
# 5. Capability-equivalent comparators, public cost (H1)
# --------------------------------------------------------------------------- #
def public_cost_status_quo():
    """Variant A. Present fleet kept, no intercontinental readiness (not equivalent)."""
    return annuity(MAINT_PUBLIC_FLEET)


def public_cost_public_ownership(fixed_readiness=FIXED_READINESS):
    """Variant B. The state buys and operates the jets, no commercial business."""
    return XRS_CAPEX + annuity(fixed_readiness) - RESIDUAL_VALUE / (1 + SOCIAL_RATE) ** HORIZON


def public_cost_availability(fee_range=AVAILABILITY_FEE):
    """Variant C. A private owner sells guaranteed availability, no state equity."""
    low, high = fee_range
    return (annuity(low), annuity(high))


def public_cost_ppp(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, terminal="cash"):
    """Variant D. The proposed 51/49 company, net public cost.

    Outlays are the in-kind fleet at its full contributed value, the cash top-up
    and the readiness fee. Returns are the state share of dividends and of the
    terminal value, and the upkeep of the old fixed-wing unit avoided once the
    company takes over.

    terminal='cash' credits the state only its share of the fleet resale, the
    conservative fiscal view where the state holds the stake and never sells it.
    terminal='economic' credits the state its 51 per cent of the going-concern
    company value, the economic view the reviewer also asks for.
    """
    wn = net_result(fee, growth)
    div_public = sum((wn[i - 1] * PUBLIC_SHARE * (1 - REINVEST_SHARE)) / (1 + SOCIAL_RATE) ** (i + 1)
                     for i in range(1, HORIZON) if wn[i - 1] > 0)
    outlay = IN_KIND_FLEET + PUBLIC_CASH + annuity(fee)
    if terminal == "economic":
        terminal_state = PUBLIC_SHARE * terminal_company_value(fee, growth)
    else:
        terminal_state = PUBLIC_SHARE * RESIDUAL_VALUE
    residual_state = terminal_state / (1 + SOCIAL_RATE) ** HORIZON
    return outlay - div_public - annuity(MAINT_PUBLIC_FLEET) - residual_state


def fiscal_saving(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH, terminal="cash"):
    """H1 headline. Public cost of the all-public comparator less the PPP."""
    return public_cost_public_ownership() - public_cost_ppp(fee, growth, terminal)


def public_cost_components(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """PV components of the public cost, million zloty at the social rate.

    Exposed so the public-cost table can show the full arithmetic and a reader
    can trace the three measures without opening the model.
    """
    wn = net_result(fee, growth)
    pv_fee = annuity(fee)
    div_public = sum((wn[i - 1] * PUBLIC_SHARE * (1 - REINVEST_SHARE)) / (1 + SOCIAL_RATE) ** (i + 1)
                     for i in range(1, HORIZON) if wn[i - 1] > 0)
    pv_avoided = annuity(MAINT_PUBLIC_FLEET)
    pv_stake_gc = PUBLIC_SHARE * terminal_company_value(fee, growth) / (1 + SOCIAL_RATE) ** HORIZON
    pv_stake_fleet = PUBLIC_SHARE * RESIDUAL_VALUE / (1 + SOCIAL_RATE) ** HORIZON
    return dict(in_kind=float(IN_KIND_FLEET), cash=float(PUBLIC_CASH), pv_fee=pv_fee,
                div_public=div_public, pv_avoided=pv_avoided,
                pv_stake_gc=pv_stake_gc, pv_stake_fleet=pv_stake_fleet)


def budgetary_outlay(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Measure 1. New cash from the budget, the in-kind fleet excluded.

    The existing fleet is already owned by the state, so it is not a fresh
    budgetary expense. This measure counts only new cash out (top-up and fee),
    less the cash the state receives back (dividends, avoided upkeep, fleet-share
    residual).
    """
    c = public_cost_components(fee, growth)
    return c["cash"] + c["pv_fee"] - c["div_public"] - c["pv_avoided"] - c["pv_stake_fleet"]


def resource_cost(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Measure 2. Resource cost, the in-kind fleet counted at its value.

    Comparable with public ownership, which also counts the aircraft as a
    resource. This is the figure the public_cost_ppp cash basis returns.
    """
    return IN_KIND_FLEET + budgetary_outlay(fee, growth)


def economic_cost(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Measure 3. Economic cost, the state's going-concern stake recognised.

    Instead of crediting the state only its share of the fleet residual, this
    measure credits its 51 per cent of the going-concern company value at exit.
    """
    c = public_cost_components(fee, growth)
    return (c["in_kind"] + c["cash"] + c["pv_fee"] - c["div_public"]
            - c["pv_avoided"] - c["pv_stake_gc"])


# --------------------------------------------------------------------------- #
# 6. Thresholds
# --------------------------------------------------------------------------- #
def fee_for_equity_breakeven(growth=COMMERCIAL_GROWTH):
    """F*. The readiness fee at which the private equity NPV is zero."""
    lo, hi = 20.0, 200.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if equity_npv(mid, growth) < 0:
            lo = mid
        else:
            hi = mid
    return mid


def rate_threshold_table(rates=(0.65, 0.86, 1.03, 1.21)):
    """PV of operating flows across average intercontinental mission rates.

    Rates in million PLN a mission map to a year-one commercial figure through
    the fleet mission ceiling, so the table shows sensitivity to the one price
    the base case most depends on. Reported for context, not as the base.
    """
    rows = []
    for price in rates:
        # commercial year-one scales with the rate relative to the 0.86 base
        scale = price / 0.86
        g = COMMERCIAL_GROWTH
        com = [COMMERCIAL_RAMP[k] * scale * (1 + g) ** k for k in range(HORIZON)]
        ox = [OPEX_BASE[k] + MARGINAL_COST * COMMERCIAL_RAMP[k] * scale * ((1 + g) ** k - 1)
              for k in range(HORIZON)]
        rev = [READINESS_FEE + com[k] for k in range(HORIZON)]
        wn = [rev[k] - ox[k] - DEPRECIATION for k in range(HORIZON)]
        fcf = [wn[k] + DEPRECIATION - CAPEX[k] for k in range(HORIZON)]
        rows.append(dict(price=price, pv=npv(fcf, FINANCIAL_RATE, RESIDUAL_VALUE),
                         profit10=wn[-1]))
    return rows


# --------------------------------------------------------------------------- #
# 7. Investment balance of the reform (Table 3), fleet-price sensitivity
# --------------------------------------------------------------------------- #
FLEET = {
    "AW101 heavy MEDEVAC": dict(units=4, low=280, high=340),
    "H145 HEMS-Primary": dict(units=28, low=90, high=120),
    "H145 reserve": dict(units=3, low=90, high=120),
    "Cessna Grand Caravan EX (STOL)": dict(units=3, low=10, high=12),
}
RESALE_WITHDRAWN = dict(units=14, low=6, high=10)
CONVERSION_SAVING = dict(units=9, low=30, high=40)


def gross_purchase(level):
    total = 0.0
    for item in FLEET.values():
        unit = (item["low"] + item["high"]) / 2 if level == "mid" else item[level]
        total += item["units"] * unit
    return total


def compensations(level):
    if level == "mid":
        resale = RESALE_WITHDRAWN["units"] * (RESALE_WITHDRAWN["low"] + RESALE_WITHDRAWN["high"]) / 2
        conv = CONVERSION_SAVING["units"] * (CONVERSION_SAVING["low"] + CONVERSION_SAVING["high"]) / 2
    else:
        resale = RESALE_WITHDRAWN["units"] * RESALE_WITHDRAWN[level]
        conv = CONVERSION_SAVING["units"] * CONVERSION_SAVING[level]
    return resale + conv


def cash_financing_requirement(cost_level, recovery_level):
    """Gross fleet purchase less the resale of withdrawn airframes only."""
    resale = (RESALE_WITHDRAWN["units"] * RESALE_WITHDRAWN[recovery_level]
              if recovery_level != "mid"
              else RESALE_WITHDRAWN["units"] * (RESALE_WITHDRAWN["low"] + RESALE_WITHDRAWN["high"]) / 2)
    return gross_purchase(cost_level) - resale


def incremental_economic_cost(cost_level, recovery_level):
    """Cash financing requirement less the avoided cost of an all-new light fleet."""
    conv = (CONVERSION_SAVING["units"] * CONVERSION_SAVING[recovery_level]
            if recovery_level != "mid"
            else CONVERSION_SAVING["units"] * (CONVERSION_SAVING["low"] + CONVERSION_SAVING["high"]) / 2)
    return cash_financing_requirement(cost_level, recovery_level) - conv


def present_value_even(net, rate, years=4):
    ann = sum(1 / (1 + rate) ** t for t in range(years))
    return (net / years) * ann


def sensitivity_rows():
    scenarios = [
        ("Conservative (worst)", "high", "low"),
        ("Central", "mid", "mid"),
        ("Optimistic (best)", "low", "high"),
    ]
    rows = []
    for name, cost_level, recovery_level in scenarios:
        gross = gross_purchase(cost_level)
        comp = compensations(recovery_level)
        net = gross - comp
        pv = {r: present_value_even(net, r) for r in (0.03, 0.04, 0.05)}
        rows.append(dict(name=name, gross=gross, comp=comp, net=net, pv=pv))
    return rows


# --------------------------------------------------------------------------- #
# 8. Reporting
# --------------------------------------------------------------------------- #
def main():
    wn = net_result()
    print("=== Company simulation, readiness fee 65, growth 2.5% ===")
    print(f"revenue      : {[round(x) for x in revenue()]}")
    print(f"opex         : {[round(x) for x in opex()]}")
    print(f"net result   : {[round(x) for x in wn]}")
    print(f"break-even   : year {break_even_year()} (first positive annual result)")
    print()
    print("=== Three value measures ===")
    print(f"PV of operating flows       = {pv_operating():7.1f}")
    print(f"Project NPV, full I0 = 370  = {npv_project():7.1f}")
    print(f"Project NPV, new money only = {npv_project_new_money():7.1f}")
    print()
    print("=== Private equity, H2 (contribution 180, hurdle 10%) ===")
    print(f"equity NPV   = {equity_npv():7.1f}")
    print(f"equity IRR   = {equity_irr() * 100:7.1f} %")
    pb = equity_payback()
    print(f"payback      = {pb if pb else 'none'} years")
    print(f"F* fee for equity NPV = 0   = {fee_for_equity_breakeven():.0f}")
    print()
    print("=== Capability-equivalent public cost, H1 (PV, 3%) ===")
    print(f"A status quo (less capable) = {public_cost_status_quo():6.0f}")
    print(f"B public ownership          = {public_cost_public_ownership():6.0f}")
    lo, hi = public_cost_availability()
    print(f"C availability contract     = {lo:6.0f} to {hi:6.0f}")
    print(f"D proposed PPP, cash view   = {public_cost_ppp(terminal='cash'):6.0f}")
    print(f"D proposed PPP, economic    = {public_cost_ppp(terminal='economic'):6.0f}")
    print(f"fiscal saving vs B, cash    = {fiscal_saving(terminal='cash'):6.0f}")
    print(f"fiscal saving vs B, economic= {fiscal_saving(terminal='economic'):6.0f}")
    print(f"terminal company value r10  = {terminal_company_value():6.0f} "
          f"(state 51% = {PUBLIC_SHARE * terminal_company_value():.0f}, "
          f"private 49% = {PRIVATE_SHARE * terminal_company_value():.0f})")


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------- #
# 9. Whole-of-system (world-cost) convention
# --------------------------------------------------------------------------- #
# The fleet is segmented by range. The existing fixed-wing aircraft carry the
# short-and-medium-haul medical transport task, and the new ultra-long-range
# pair carries the long haul, one jet on standby and one in commercial service.
# The short-and-medium-range task exists in every world, so in variants B and C
# the existing fleet keeps flying as a separate state unit and its upkeep is an
# explicit cost of those worlds, while in variant D the fleet and its task move
# inside the company. No variant receives a credit the others lack.

def legacy_upkeep_pv():
    """PV of the continued upkeep of the existing fixed-wing unit, 30 a year."""
    return annuity(MAINT_PUBLIC_FLEET)


def world_cost_public_ownership():
    """Variant B, whole of system: the new jets plus the continuing legacy unit."""
    return public_cost_public_ownership() + legacy_upkeep_pv()


def world_cost_availability():
    lo, hi = public_cost_availability()
    return (lo + legacy_upkeep_pv(), hi + legacy_upkeep_pv())


def world_resource_cost(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Variant D, whole of system, resource measure.

    No credit for avoided legacy upkeep, because the legacy task and its cost
    sit inside the company and are met from the fee and commercial revenue.
    """
    c = public_cost_components(fee, growth)
    return c["in_kind"] + c["cash"] + c["pv_fee"] - c["div_public"] - c["pv_stake_fleet"]


def world_budgetary_outlay(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Variant D world cost on new cash only, the in-kind fleet excluded."""
    return world_resource_cost(fee, growth) - IN_KIND_FLEET


def world_economic_cost(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Variant D world cost with the going-concern stake recognised."""
    c = public_cost_components(fee, growth)
    return world_resource_cost(fee, growth) - (c["pv_stake_gc"] - c["pv_stake_fleet"])


def world_saving(measure="resource", fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    d = {"resource": world_resource_cost, "budgetary": world_budgetary_outlay,
         "economic": world_economic_cost}[measure](fee, growth)
    return world_cost_public_ownership() - d


def symmetric_withdrawal_gap(fee=READINESS_FEE, growth=COMMERCIAL_GROWTH):
    """Sensitivity. If the legacy fleet were withdrawn in every variant, B falls
    to its net figure while D keeps its world cost, and the gap reverses."""
    return public_cost_public_ownership() - world_resource_cost(fee, growth)


def stake_rate_sensitivity(rates=(0.03, 0.05, 0.08, 0.10)):
    """World economic cost and saving as the state's stake is discounted at r."""
    c = public_cost_components()
    stake = PUBLIC_SHARE * terminal_company_value()
    out = []
    for r in rates:
        eco = world_resource_cost() - (stake / (1 + r) ** HORIZON - c["pv_stake_fleet"])
        out.append(dict(rate=r, economic=eco, saving=world_cost_public_ownership() - eco))
    return out
