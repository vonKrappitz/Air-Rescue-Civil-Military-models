"""economic_model.py

Ten-year economic simulation of the LEM-PPP air-medical company and the
investment-balance sensitivity of the wider reform.

This script regenerates Table 2 (company simulation, net present value) and
Table 3 (sensitivity of the net investment balance) of Appendix 1 in:

    M. M. Kasperek (2026). Civil-military integration of a reformed national
    air-rescue network. Defence and Peace Economics (preprint).

All amounts are in million PLN, in constant 2026 prices unless stated.
The model is fully deterministic. Running the file prints both tables and the
headline figures, and every value is reproduced to the unit.

Conventions follow the appraisal framework of Section 4:
    WN_t  = R_t - OPEX_t - D_t            (net accounting result)
    CF_t  = WN_t + D_t - CapEx_t          (free cash flow, depreciation added back)
    NPV   = sum_t CF_t / (1+r)^t + RV / (1+r)^T

The financial rate r is 4 per cent real (EU Economic Appraisal Vademecum
2021-2027). The social rate of 3 per cent is used for the public balance, and
the sensitivity spans 3, 4 and 5 per cent. The nominal variant grows the flows
at the 2.5 per cent inflation target and discounts at the matching nominal rate,
so by the Fisher relation it returns the same present value.
"""

from itertools import combinations  # noqa: F401  (kept for parity with placement module)

# --------------------------------------------------------------------------- #
# Company simulation inputs (Table 2), million PLN, constant 2026 prices
# --------------------------------------------------------------------------- #
REVENUE = [55, 68, 80, 98, 110, 115, 118, 120, 122, 123]
OPEX = [60, 60, 60, 60, 60, 61, 61, 62, 62, 63]
DEPRECIATION = 18                       # in-kind fleet (~190 m PLN) over 15 years
CAPEX = [3, 3, 3, 3, 3, 12, 3, 3, 3, 3]  # routine 3 per year, mid-life refit 12 in year 6
RESIDUAL_VALUE = 50                     # real terminal value, year 10
HORIZON = 10

# Rates
FINANCIAL_RATE = 0.04                   # company appraisal, real
SOCIAL_RATE = 0.03                      # public balance
INFLATION = 0.025                       # NBP target, used for the nominal variant

# The annual readiness fee from the Ministry of National Defence is part of
# revenue. The optimistic scenario lifts only the commercial part (revenue less
# the fee), so the fee is held fixed.
MON_FEE = 35

# Ownership and dividend policy
PUBLIC_SHARE = 0.51                     # MON 31 % + MZ 20 %
REINVEST_SHARE = 0.15                   # each side reinvests at least this fraction
FLEET_MAINTENANCE_SAVING = 300          # treasury saving over the decade


# --------------------------------------------------------------------------- #
# Core functions
# --------------------------------------------------------------------------- #
def net_result(revenue, opex=OPEX, depreciation=DEPRECIATION):
    """WN_t = R_t - OPEX_t - D_t."""
    return [revenue[i] - opex[i] - depreciation for i in range(HORIZON)]


def free_cash_flow(revenue, capex=CAPEX, depreciation=DEPRECIATION):
    """CF_t = WN_t + D_t - CapEx_t."""
    wn = net_result(revenue, depreciation=depreciation)
    return [wn[i] + depreciation - capex[i] for i in range(HORIZON)]


def npv(cash_flow, rate=FINANCIAL_RATE, residual=RESIDUAL_VALUE):
    """Present value of a ten-year flow with a terminal residual at year T.

    Flows are dated t = 1..T. The residual is discounted at year T.
    """
    pv = sum(cash_flow[i] / (1 + rate) ** (i + 1) for i in range(HORIZON))
    return pv + residual / (1 + rate) ** HORIZON


def nominal_flow(real_flow, inflation=INFLATION):
    """Inflate a real flow to nominal terms at year t = i + 1."""
    return [real_flow[i] * (1 + inflation) ** (i + 1) for i in range(len(real_flow))]


def fisher_rate(real_rate=FINANCIAL_RATE, inflation=INFLATION):
    """(1 + r_nom) = (1 + r)(1 + pi)."""
    return (1 + real_rate) * (1 + inflation) - 1


def commercial_uplift_flow(uplift, fee=MON_FEE):
    """Revenue with the commercial part (revenue less the fee) scaled by uplift."""
    scaled = [fee + (REVENUE[i] - fee) * uplift for i in range(HORIZON)]
    return free_cash_flow(scaled)


def solve_uplift_for_target(target_npv, fee=MON_FEE):
    """Commercial-revenue uplift that brings the NPV to a target value.

    Linear in the uplift, so it is solved in closed form rather than searched.
    """
    base = npv(free_cash_flow(REVENUE))
    df = [1 / (1 + FINANCIAL_RATE) ** (i + 1) for i in range(HORIZON)]
    pv_commercial = sum((REVENUE[i] - fee) * df[i] for i in range(HORIZON))
    return 1 + (target_npv - base) / pv_commercial


def dividend_to_treasury(cumulative_to_year_nine):
    """State cash from dividends.

    Dividends are declared on the prior year's profit, so the pool available in a
    ten-year window is the cumulative result through year nine. The public side
    takes its share and reinvests a fraction of it.
    """
    return cumulative_to_year_nine * PUBLIC_SHARE * (1 - REINVEST_SHARE)


# --------------------------------------------------------------------------- #
# Investment-balance sensitivity (Table 3)
# --------------------------------------------------------------------------- #
# Fleet unit prices (million PLN). Low end is the optimistic purchase, high end
# the conservative one. The civilian AW101 omits naval defence systems, so it is
# priced below the 412.5 m PLN per unit of the 2019 naval contract.
FLEET = {
    "AW101 heavy MEDEVAC": dict(units=4, low=280, high=340),
    "H145 HEMS-Primary": dict(units=28, low=90, high=120),
    "H145 reserve": dict(units=3, low=90, high=120),
    "Cessna Grand Caravan EX (STOL)": dict(units=3, low=10, high=12),
}
RESALE_WITHDRAWN = dict(units=14, low=6, high=10)     # EC135/H135 secondary market
CONVERSION_SAVING = dict(units=9, low=30, high=40)    # H135 to light class, per unit


def gross_purchase(level):
    """Total fleet purchase. level is 'low', 'high' or 'mid'."""
    total = 0.0
    for item in FLEET.values():
        if level == "mid":
            unit = (item["low"] + item["high"]) / 2
        else:
            unit = item[level]
        total += item["units"] * unit
    return total


def compensations(level):
    """Resale of withdrawn airframes plus the conversion saving.

    The recovery is highest in the optimistic case, so 'high' here pairs with the
    low purchase price, and 'low' with the high purchase price.
    """
    if level == "mid":
        resale = RESALE_WITHDRAWN["units"] * (RESALE_WITHDRAWN["low"] + RESALE_WITHDRAWN["high"]) / 2
        conv = CONVERSION_SAVING["units"] * (CONVERSION_SAVING["low"] + CONVERSION_SAVING["high"]) / 2
    else:
        resale = RESALE_WITHDRAWN["units"] * RESALE_WITHDRAWN[level]
        conv = CONVERSION_SAVING["units"] * CONVERSION_SAVING[level]
    return resale + conv


def present_value_even(net, rate, years=4):
    """Net balance spread evenly over the outlay years, first tranche undiscounted.

    The outlays fall in 2026-2029, so the first tranche is dated t = 0.
    """
    annuity = sum(1 / (1 + rate) ** t for t in range(years))
    return (net / years) * annuity


def sensitivity_rows():
    """Three scenarios of the net investment balance with present values."""
    scenarios = [
        ("Conservative (worst)", "high", "low"),   # highest cost, lowest recovery
        ("Central", "mid", "mid"),
        ("Optimistic (best)", "low", "high"),      # lowest cost, highest recovery
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
# Reporting
# --------------------------------------------------------------------------- #
def print_table_2():
    wn = net_result(REVENUE)
    cf_real = free_cash_flow(REVENUE)
    cf_nom = nominal_flow(cf_real)
    print("Table 2. Economic simulation of the LEM-PPP company, ten years (million PLN)")
    print(f"{'Year':>4} {'Revenue':>8} {'OPEX':>5} {'Depr.':>6} "
          f"{'Net':>5} {'CF real':>8} {'CF nom':>7}")
    for i in range(HORIZON):
        print(f"{i + 1:>4} {REVENUE[i]:>8} {OPEX[i]:>5} {DEPRECIATION:>6} "
              f"{wn[i]:>5} {cf_real[i]:>8} {round(cf_nom[i]):>7}")
    print(f"{'Residual, year 10':>32} {RESIDUAL_VALUE:>8} {round(nominal_flow([RESIDUAL_VALUE]*10)[9]):>7}")

    npv_real = npv(cf_real)
    r_nom = fisher_rate()
    npv_nom = npv(cf_nom, rate=r_nom, residual=RESIDUAL_VALUE * (1 + INFLATION) ** HORIZON)
    print(f"NPV (4% financial), real  = {npv_real:6.1f}")
    print(f"NPV (Fisher nominal)      = {npv_nom:6.1f}")

    uplift = solve_uplift_for_target(437)
    npv_opt = npv(commercial_uplift_flow(uplift))
    print(f"Optimistic NPV            = {npv_opt:6.1f}  "
          f"(commercial revenue +{(uplift - 1) * 100:.0f}%, NPV +{(npv_opt / npv_real - 1) * 100:.0f}%)")

    cum = []
    s = 0
    for x in wn:
        s += x
        cum.append(s)
    treasury = dividend_to_treasury(cum[8]) + FLEET_MAINTENANCE_SAVING
    print(f"Cumulative net result, decade        = {cum[-1]:.0f}")
    print(f"Cumulative through year nine (pool)  = {cum[8]:.0f}")
    print(f"State dividend share                 = {dividend_to_treasury(cum[8]):.0f}")
    print(f"Treasury benefit (dividend + saving) = {treasury:.0f}")


def print_table_3():
    print("\nTable 3. Sensitivity of the net investment balance (million PLN)")
    print(f"{'Scenario':>22} {'Gross':>6} {'Comp.':>6} {'Net':>6} "
          f"{'PV 3%':>7} {'PV 4%':>7} {'PV 5%':>7}")
    for row in sensitivity_rows():
        pv = row["pv"]
        print(f"{row['name']:>22} {row['gross']:>6.0f} {row['comp']:>6.0f} "
              f"{row['net']:>6.0f} {pv[0.03]:>7.0f} {pv[0.04]:>7.0f} {pv[0.05]:>7.0f}")


def main():
    print_table_2()
    print_table_3()


if __name__ == "__main__":
    main()
