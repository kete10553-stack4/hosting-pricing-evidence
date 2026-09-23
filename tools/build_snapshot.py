#!/usr/bin/env python3
"""Build compact evidence CSV files from a HostDealRadar-compatible JSON export."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
def clean(value: object) -> str:
    return " ".join(str(value or "").split())
def valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
def build(input_path: Path) -> dict[str, object]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    offers, source_status = raw.get("offers", []), raw.get("source_status", {})
    price_rows = []
    for offer in offers:
        price_evidence = (offer.get("claim_evidence") or {}).get("price") or {}
        quote, source_url, price = clean(price_evidence.get("quote")), clean(offer.get("source_url")), offer.get("price")
        if not quote or price is None or not valid_http_url(source_url):
            continue
        price_rows.append({
            "slug":clean(offer.get("slug")), "provider":clean(offer.get("provider")), "title":clean(offer.get("title")),
            "category":clean(offer.get("category")), "kind":clean(offer.get("kind") or "standard_price"), "price":price,
            "currency":clean(offer.get("currency")), "billing_period":clean(offer.get("billing_period")),
            "commitment_months":offer.get("commitment_months", ""), "renewal_price":offer.get("renewal_price", ""),
            "discount_percent":offer.get("discount_percent", ""), "coupon_code":clean(offer.get("coupon_code")),
            "valid_until":clean(offer.get("valid_until")), "source_url":source_url, "captured_at":clean(offer.get("fetched_at")),
            "evidence_quote":quote[:500], "evidence_location":clean(price_evidence.get("location")),
            "source_sha256":clean(offer.get("source_sha256"))})
    status_rows = []
    for provider, status in sorted(source_status.items()):
        status_rows.append({"provider":provider, "status":clean(status.get("status")), "request_url":clean(status.get("request_url")),
            "http_status":status.get("http_status", ""), "checked_at":clean(status.get("checked_at")),
            "capture_status":clean(status.get("capture_status")), "published_count":status.get("published_count", 0),
            "captured_count":status.get("captured_count", 0), "retained_count":status.get("retained_count", 0),
            "reason":clean(status.get("reason")), "visible_excerpt":clean(status.get("visible_excerpt"))[:500]})
    price_fields = ["slug","provider","title","category","kind","price","currency","billing_period","commitment_months","renewal_price","discount_percent","coupon_code","valid_until","source_url","captured_at","evidence_quote","evidence_location","source_sha256"]
    status_fields = ["provider","status","request_url","http_status","checked_at","capture_status","published_count","captured_count","retained_count","reason","visible_excerpt"]
    write_csv(DATA_DIR / "hosting-plan-evidence.csv", price_fields, price_rows)
    write_csv(DATA_DIR / "provider-source-status.csv", status_fields, status_rows)
    metadata = {"snapshot_generated_at":clean(raw.get("generated_at")), "exported_price_records":len(price_rows),
        "providers_with_price_records":len({row["provider"] for row in price_rows}), "provider_source_checks":len(status_rows),
        "source_state_counts":{state:sum(1 for row in status_rows if row["status"] == state) for state in sorted({str(row["status"]) for row in status_rows})},
        "selection_rule":"Records require claim_evidence.price.quote and an official HTTP(S) source URL."}
    (DATA_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return metadata
def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); args = parser.parse_args()
    print(json.dumps(build(args.input), indent=2, ensure_ascii=False))
if __name__ == "__main__":
    main()
