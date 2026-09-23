#!/usr/bin/env python3
"""Validate the published CSV snapshot without network access."""
from __future__ import annotations
import csv, json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
def is_url(value: str) -> bool:
    parsed = urlparse(value); return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
def is_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00")); return True
    except ValueError:
        return False
def main() -> None:
    offers = read_csv("hosting-plan-evidence.csv")
    statuses = read_csv("provider-source-status.csv")
    metadata = json.loads((DATA / "metadata.json").read_text(encoding="utf-8"))
    errors = []; slugs = set()
    for index, row in enumerate(offers, start=2):
        label = f"hosting-plan-evidence.csv:{index}"
        for field in ("slug","provider","title","source_url","captured_at","evidence_quote"):
            if not row.get(field, "").strip(): errors.append(f"{label}: missing {field}")
        if row["slug"] in slugs: errors.append(f"{label}: duplicate slug {row['slug']}")
        slugs.add(row["slug"])
        if not is_url(row["source_url"]): errors.append(f"{label}: invalid source_url")
        if not is_timestamp(row["captured_at"]): errors.append(f"{label}: invalid captured_at")
        try:
            if float(row["price"]) <= 0: errors.append(f"{label}: price must be positive")
        except ValueError: errors.append(f"{label}: price is not numeric")
    allowed = {"evidenced","unreadable","challenge"}; providers = set()
    for index, row in enumerate(statuses, start=2):
        label = f"provider-source-status.csv:{index}"
        if not row["provider"]: errors.append(f"{label}: missing provider")
        if row["provider"] in providers: errors.append(f"{label}: duplicate provider {row['provider']}")
        providers.add(row["provider"])
        if row["status"] not in allowed: errors.append(f"{label}: unknown status {row['status']}")
        if row["request_url"] and not is_url(row["request_url"]): errors.append(f"{label}: invalid request_url")
        if not is_timestamp(row["checked_at"]): errors.append(f"{label}: invalid checked_at")
        if row["status"] == "evidenced" and not row["visible_excerpt"]: errors.append(f"{label}: evidenced source has no visible excerpt")
    if metadata.get("exported_price_records") != len(offers): errors.append("metadata price-record count does not match CSV")
    if metadata.get("provider_source_checks") != len(statuses): errors.append("metadata provider-check count does not match CSV")
    if errors: raise SystemExit("\n".join(errors))
    print(f"OK: {len(offers)} price records, {len(statuses)} provider source checks")
if __name__ == "__main__":
    main()
