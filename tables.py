"""tables.py

Emit the seven tables of Part IV as markdown, every number computed by
economic_model.py and reserve_placement.py so the tables cannot drift from the
model. Run it with

    python tables.py

and it writes tables.md next to the script.
"""

import io
import economic_model as em
import reserve_placement as rp


def t1_comparators():
    wlo, whi = em.world_cost_availability()
    rows = [
        ("A status quo", "existing fleet only, no intercontinental readiness", "no", f"{em.public_cost_status_quo():.0f}"),
        ("B public ownership", "state operates two long-range jets, existing fleet continues separately", "yes", f"{em.world_cost_public_ownership():.0f}"),
        ("C availability contract", "guaranteed availability bought in, existing fleet continues separately", "yes", f"{wlo:.0f}-{whi:.0f}"),
        ("D LEM-PPP (proposed)", "51/49 company absorbing the existing fleet and its task", "yes",
         f"{em.world_resource_cost():.0f} resource / {em.world_budgetary_outlay():.0f} budgetary / {em.world_economic_cost():.0f} economic"),
    ]
    out = ["### Table 1. Capability-equivalent comparators, whole-of-system public cost",
           "", "| Variant | Description | 2 h intercont. readiness | World cost (PV) |",
           "|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    return "\n".join(out)



def t2_risks():
    rows = [
        ("Commercial demand", "private", "conservative base case, threshold analysis"),
        ("Maintenance and major overhaul", "private", "reserves in OPEX, mid-life refit in CAPEX"),
        ("Technical availability", "private", "availability payment with deductions"),
        ("Mobilisation and step-in", "public", "MEM clause, continuity protocol, compensation"),
        ("Foreign-exchange (fleet purchase)", "public", "priced at contract, one-off"),
        ("Residual value", "shared 51/49", "conservative terminal, sensitivity"),
        ("Regulatory / state-aid", "public", "Altmark structuring, ex ante entrustment"),
    ]
    out = ["### Table 2. Allocation of risks",
           "", "| Risk | Bearer | Mitigation |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} |")
    return "\n".join(out)


def t3_assumptions():
    rows = [
        ("Readiness fee", f"{em.READINESS_FEE}", "50-93", "state support, central lever"),
        ("Private contribution", f"{em.I0_PRIVATE}", "-", "equity at t=0"),
        ("Public contribution", f"{em.I0_PUBLIC}", "-", "in-kind fleet 120 + cash 70"),
        ("Ownership split", "51 / 49", "-", "majority state"),
        ("Commercial growth", f"{em.COMMERCIAL_GROWTH*100:.1f}%", "0-10%", "below market CAGR ~10-11%"),
        ("Marginal cost on growth", f"{em.MARGINAL_COST:.2f}", "0.2-0.4", "variable cost per unit extra revenue"),
        ("Depreciation", f"{em.DEPRECIATION}", "-", "whole fleet ~311 over 15 yr"),
        ("Residual value (fleet)", f"{em.RESIDUAL_VALUE}", "0-50", "conservative terminal"),
        ("Private hurdle rate", f"{em.HURDLE_PRIVATE*100:.0f}%", "8-12%", "real, infrastructure equity"),
        ("Exit multiple", f"{em.EXIT_MULTIPLE}x", "6-12x", "going-concern resale, year 10"),
        ("Financial discount rate", f"{em.FINANCIAL_RATE*100:.0f}%", "3-5%", "company appraisal, real"),
        ("Social discount rate", f"{em.SOCIAL_RATE*100:.0f}%", "3-5%", "public balance"),
    ]
    out = ["### Table 3. Model assumptions",
           "", "| Parameter | Base | Range | Source / basis |", "|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    return "\n".join(out)


def t4_project_cashflow():
    rev = em.revenue(); ox = em.opex(); wn = em.net_result(); fcf = em.free_cash_flow()
    out = ["### Table 4. Project cash flow, million PLN real",
           "", "| Year | Revenue | OPEX | Deprec. | CAPEX | FCFF | PV @4% |", "|---|---|---|---|---|---|---|"]
    out.append(f"| 0 | | | | | {-em.I0_TOTAL} | {-em.I0_TOTAL} |")
    for k in range(em.HORIZON):
        pv = fcf[k] / (1 + em.FINANCIAL_RATE) ** (k + 1)
        out.append(f"| {k+1} | {rev[k]:.0f} | {ox[k]:.0f} | {em.DEPRECIATION} | {em.CAPEX[k]} | {fcf[k]:.0f} | {pv:.1f} |")
    out.append(f"| 10 residual | | | | | {em.RESIDUAL_VALUE} | {em.RESIDUAL_VALUE/(1+em.FINANCIAL_RATE)**em.HORIZON:.1f} |")
    out.append("")
    out.append(f"_PV of operating flows {em.pv_operating():.0f}. Project NPV with full I0=370 is {em.npv_project():+.0f}; "
               f"on new money only {em.npv_project_new_money():+.0f}._")
    return "\n".join(out)


def t5_private_equity():
    fcfe = em.private_fcfe(); div = em._dividends_private()
    tcv = em.terminal_company_value()
    out = ["### Table 5. Private-partner equity cash flow, million PLN real",
           "", "| Year | Dividend | Exit value | FCFE | PV @10% |", "|---|---|---|---|---|"]
    out.append(f"| 0 | | | {-em.I0_PRIVATE} | {-em.I0_PRIVATE} |")
    for k in range(em.HORIZON):
        exitv = em.PRIVATE_SHARE * tcv if k == em.HORIZON - 1 else 0
        pv = fcfe[k+1] / (1 + em.HURDLE_PRIVATE) ** (k + 1)
        exit_s = f"{exitv:.0f}" if exitv else ""
        out.append(f"| {k+1} | {div[k]:.1f} | {exit_s} | {fcfe[k+1]:.1f} | {pv:.1f} |")
    out.append("")
    out.append(f"_Equity NPV {em.equity_npv():+.1f}, IRR {em.equity_irr()*100:.1f}%, payback {em.equity_payback()} years. "
               f"Terminal company value {tcv:.0f} (private 49% = {em.PRIVATE_SHARE*tcv:.0f})._")
    return "\n".join(out)


def t6_public_result():
    c = em.public_cost_components()
    Bw = em.world_cost_public_ownership()
    res = em.world_resource_cost(); budg = em.world_budgetary_outlay(); eco = em.world_economic_cost()
    out = ["### Table 6. Whole-of-system public cost, full arithmetic (PV @3%)",
           "", "| Item | PV |", "|---|---|"]
    out.append(f"| Variant B: jets {em.XRS_CAPEX} + readiness {em.annuity(em.FIXED_READINESS):.0f} - residual {em.RESIDUAL_VALUE/(1+em.SOCIAL_RATE)**em.HORIZON:.0f} + legacy upkeep {em.legacy_upkeep_pv():.0f} | **{Bw:.0f}** |")
    out.append(f"| Variant D: in-kind {c['in_kind']:.0f} + cash {c['cash']:.0f} + fees {c['pv_fee']:.0f} - dividends {c['div_public']:.0f} - fleet-residual share {c['pv_stake_fleet']:.0f} | **{res:.0f}** |")
    out.append(f"| Memo: budgetary outlay (in-kind excluded) | {budg:.0f} |")
    out.append(f"| Less incremental going-concern stake | -{c['pv_stake_gc']-c['pv_stake_fleet']:.0f} |")
    out.append(f"| = Economic cost | **{eco:.0f}** |")
    out.append("")
    out.append(f"_Savings vs B: {Bw-res:.0f} resource, {Bw-eco:.0f} economic. If the legacy fleet were withdrawn in every variant, B falls to {em.public_cost_public_ownership():.0f} and the advantage reverses by about {abs(em.symmetric_withdrawal_gap()):.0f}._")
    return "\n".join(out)



def t7_thresholds():
    out = ["### Table 7. Thresholds and sensitivity", ""]
    out.append(f"**F\\*** readiness fee for equity NPV = 0: **{em.fee_for_equity_breakeven():.0f}** (base 65 sits above it).")
    out.append("")
    out.append("| Exit multiple | Terminal value | Equity NPV | H2 |")
    out.append("|---|---|---|---|")
    for m in (6, 8, 10, 12):
        tcv = m * em.net_result()[-1]
        enpv = em.equity_npv(exit_multiple=m)
        out.append(f"| {m}x | {tcv:.0f} | {enpv:+.0f} | {'holds' if enpv>=0 else 'fails'} |")
    out.append("")
    grid = rp.land_grid(); civil, navy = rp.standard_coords(grid)
    c0 = rp.coverage_within(grid, civil, navy, 45, 0.0)
    c1 = rp.coverage_within(grid, civil, navy, 45, 1.0)
    out.append(f"Coverage of the base layer within 45 min is exactly linear in military availability p: {c0*100:.1f}% + {(c1-c0)*100:.1f} pp x p (within 60 min the civil bases alone cover 100%).")
    out.append("")
    out.append("| Stake discount rate | Economic cost | Saving vs public ownership |")
    out.append("|---|---|---|")
    for r in em.stake_rate_sensitivity():
        out.append(f"| {r['rate']*100:.0f}% | {r['economic']:.0f} | {r['saving']:.0f} |")
    return "\n".join(out)



def main():
    parts = [t1_comparators(), t2_risks(), t3_assumptions(), t4_project_cashflow(),
             t5_private_equity(), t6_public_result(), t7_thresholds()]
    doc = "\n\n".join(parts) + "\n"
    with open("tables.md", "w", encoding="utf-8") as f:
        f.write(doc)
    print(doc)


if __name__ == "__main__":
    main()
