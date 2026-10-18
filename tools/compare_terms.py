#!/usr/bin/env python3
"""Model prepaid hosting cash requirements; never infer a renewal billing term."""
import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def amount(value, name):
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(name + " must be numeric") from error
    if not result.is_finite() or result < 0:
        raise ValueError(name + " must be finite and nonnegative")
    return result


def money(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def cash_model(initial_total, initial_months, horizon_months, currency, renewal_monthly=None, renewal_months=None, monthly_addons="0", one_time="0"):
    for name, value in (("initial_months", initial_months), ("horizon_months", horizon_months)):
        if type(value) is not int or value <= 0:
            raise ValueError(name + " must be a positive integer")
    if renewal_months is not None and (type(renewal_months) is not int or renewal_months <= 0):
        raise ValueError("renewal_months must be a positive integer")
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("Use one explicit three-letter currency; no currency conversion is performed")
    initial = amount(initial_total, "initial_total")
    addons = amount(monthly_addons, "monthly_addons")
    startup = amount(one_time, "one_time")
    rate = amount(renewal_monthly, "renewal_monthly") if renewal_monthly is not None else None
    remaining = max(0, horizon_months - initial_months)
    known = initial + addons * horizon_months + startup
    complete = not remaining or (rate is not None and renewal_months is not None)
    renewals = (remaining + renewal_months - 1) // renewal_months if remaining and complete else 0
    renewal_block = (rate * renewal_months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if remaining and complete else None
    renewal_cash = renewal_block * renewals if renewal_block is not None else Decimal("0")
    coverage = initial_months + renewals * (renewal_months or 0) if complete else initial_months
    return {
        "currency": currency, "horizon_months": horizon_months,
        "initial_total": money(initial), "initial_commitment_months": initial_months,
        "initial_monthly_equivalent_calculated": money(initial / initial_months),
        "monthly_addons_assumed": money(addons), "one_time_cost_assumed": money(startup),
        "renewal_monthly_rate_input": str(rate) if rate is not None else None,
        "renewal_term_months_user_supplied": renewal_months,
        "renewal_blocks_needed": renewals if complete else None,
        "renewal_block_amount_calculated": money(renewal_block) if renewal_block is not None else None,
        "cash_required_before_tax_calculated": money(known + renewal_cash) if complete else None,
        "known_cash_before_unknown_renewal": money(known),
        "prepaid_months_after_horizon": max(0, coverage - horizon_months) if complete else None,
        "status": "scenario_calculated" if complete else "unknown_renewal_term_or_rate",
        "formulas": {
            "initial_monthly_equivalent": "initial_total / initial_months",
            "renewal_blocks": "ceil(max(0, horizon_months - initial_months) / renewal_months)",
            "cash_before_tax": "initial_total + renewal_blocks * round(renewal_monthly * renewal_months, 2) + monthly_addons * horizon_months + one_time"
        },
        "assumptions": ["The entire initial term is prepaid, even when the selected horizon is shorter.", "Any renewal term is an explicit user input, never copied from the initial term.", "The renewal rate is held constant only for this scenario; a future invoice or price is not verified.", "Add-ons are assumed payable monthly for the selected horizon. No cancellation refunds, taxes, overages or exchange rates are inferred."]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", help="Exact plan_id from the dated CSV; use --list to find identifiers")
    parser.add_argument("--csv", type=Path, default=ROOT / "data" / "complete-plan-terms.csv")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--initial-total")
    parser.add_argument("--initial-months", type=int)
    parser.add_argument("--currency")
    parser.add_argument("--horizon-months", type=int, default=12)
    parser.add_argument("--renewal-monthly")
    parser.add_argument("--renewal-months", type=int)
    parser.add_argument("--monthly-addons", default="0")
    parser.add_argument("--one-time", default="0")
    args = parser.parse_args()
    provenance = {"input_type": "user_supplied_scenario"}
    if args.list or args.plan:
        with args.csv.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if args.list:
            print(json.dumps([{k: r[k] for k in ("plan_id", "plan", "currency", "checked_on")} for r in rows], indent=2))
            return
        found = [r for r in rows if r["plan_id"] == args.plan]
        if len(found) != 1:
            parser.error("Plan not found uniquely; run --list")
        if any(v is not None for v in (args.initial_total, args.initial_months, args.currency, args.renewal_monthly)):
            parser.error("Do not override CSV values in --plan mode; use manual scenario mode instead")
        row = found[0]
        args.initial_total, args.initial_months, args.currency, args.renewal_monthly = row["first_term_total"], int(row["commitment_months"]), row["currency"], row["renewal_monthly_rate"]
        provenance = {"input_type": "dated_manual_observation", "plan_id": row["plan_id"], "checked_on": row["checked_on"], "checked_timezone": row["checked_timezone"], "official_sources": {k: row[k] for k in ("upfront_source_url", "term_source_url", "renewal_source_url")}, "limit": "This export does not recheck today's price or guarantee a future renewal invoice."}
    if any(v is None for v in (args.initial_total, args.initial_months, args.currency)):
        parser.error("Provide --plan or all of --initial-total, --initial-months and --currency")
    try:
        result = cash_model(args.initial_total, args.initial_months, args.horizon_months, args.currency, args.renewal_monthly, args.renewal_months, args.monthly_addons, args.one_time)
    except ValueError as error:
        parser.error(str(error))
    result["provenance"] = provenance
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
