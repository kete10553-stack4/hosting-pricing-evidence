#!/usr/bin/env python3
"""Export dated, complete first-term/renewal observations, not live offers."""
import argparse
import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["plan_id", "provider", "plan", "currency", "first_term_total", "commitment_months", "monthly_equivalent", "renewal_monthly_rate", "renewal_term_months", "checked_on", "checked_timezone", "upfront_source_url", "term_source_url", "renewal_source_url", "record_type"]


def export(input_path, source_commit, compare_path):
    data = input_path.read_bytes()
    payload = json.loads(data)
    review = payload.get("browser_term_observations") or {}
    compare_bytes = compare_path.read_bytes()
    published = {(anchor, html.unescape(re.sub(r"<[^>]*>", "", plan))) for anchor, plan in re.findall(r'<tr id="plan-([^"]+)"><td><strong>.*?</strong><span>(.*?)</span>', compare_bytes.decode("utf-8"), re.S)}
    if not published:
        raise ValueError("No published complete-plan rows found in the supplied comparison page")
    rows, rejected = [], []
    for index, record in enumerate(review.get("records", [])):
        try:
            if (record.get("plan_id", record.get("provider")), record.get("plan")) not in published:
                raise ValueError("not present in the published complete-plan comparison")
            months = record["commitment_months"]
            if type(months) is not int or months < 1:
                raise ValueError("missing positive initial commitment")
            amounts = [Decimal(str(record[k])) for k in ("first_term_total", "monthly_equivalent", "renewal_monthly_rate")]
            if not all(v.is_finite() and v > 0 for v in amounts):
                raise ValueError("missing positive amounts")
            if (amounts[0] / months).quantize(Decimal("0.01")) != amounts[1]:
                raise ValueError("monthly equivalent does not match recorded total / term")
            checked = record.get("checked_on") or review["checked_on"]
            date.fromisoformat(checked)
            evidence = record["field_evidence"]
            for field in ("first_term_total", "commitment_months", "renewal_monthly_rate"):
                url = urlsplit(evidence[field]["url"])
                if url.scheme != "https" or not url.netloc or not evidence[field]["quote"].strip():
                    raise ValueError("missing field-level official evidence")
            if not re.fullmatch(r"[A-Z]{3}", record["currency"]):
                raise ValueError("missing explicit currency")
            if record.get("renewal_currency", record["currency"]) != record["currency"]:
                raise ValueError("different initial and renewal currencies")
            plan_id = re.sub(r"[^a-z0-9]+", "-", record["provider"] + "-" + record["plan"].lower()).strip("-")
            rows.append(dict(zip(FIELDS, [plan_id, record["provider"], record["plan"], record["currency"], str(amounts[0]), months, str(amounts[1]), str(amounts[2]), "", checked, review.get("checked_timezone", "Not recorded"), evidence["first_term_total"]["url"], evidence["commitment_months"]["url"], evidence["renewal_monthly_rate"]["url"], "dated_manual_observation"])))
        except (KeyError, ValueError, TypeError, InvalidOperation) as error:
            rejected.append({"input_index": index, "reason": str(error)})
    if len({row["plan_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate plan identifiers")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("Pass the full source commit SHA")
    target = ROOT / "data" / "complete-plan-terms.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    if len(rows) != len(published):
        raise ValueError("The exported row count does not match the published comparison")
    metadata = {"exported_at_utc": datetime.now(timezone.utc).isoformat(), "source_repository": "https://github.com/kete10553-stack4/HostDealRadar-promo-radar", "source_commit": source_commit, "source_input_path": "data/offers.json", "source_input_sha256": hashlib.sha256(data).hexdigest(), "source_comparison_path": "site/compare/index.html", "source_comparison_sha256": hashlib.sha256(compare_bytes).hexdigest(), "rows": len(rows), "providers": len({r["provider"] for r in rows}), "earliest_review_date": min(r["checked_on"] for r in rows), "latest_review_date": max(r["checked_on"] for r in rows), "rejected_records": rejected, "selection": "Only rows present in the published complete-plan comparison, with positive source-supported first-term total, commitment and renewal monthly rate; monthly equivalent must equal the recorded total divided by the recorded term, rounded to cents.", "limits": "A dated export, not a new provider-price check or live offer feed. Renewal term remains blank: an initial commitment does not establish a future renewal term. No tax or future invoice is inferred."}
    (ROOT / "data" / "complete-plan-terms-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exported_rows": len(rows), "providers": metadata["providers"], "rejected": len(rejected), "date_range": [metadata["earliest_review_date"], metadata["latest_review_date"]]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--compare-html", type=Path, required=True)
    args = parser.parse_args()
    export(args.input, args.source_commit, args.compare_html)
