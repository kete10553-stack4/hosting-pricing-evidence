# Hosting Pricing Evidence

A source-linked dataset and small validator for hosting-plan prices and provider source checks.

The snapshot is built from public provider pages. Each published price row keeps the official source URL, capture time, a short quote containing the price, and a SHA-256 identifier for the captured source. Rows without price-level evidence are excluded instead of being filled from memory.

## What is included

- `data/hosting-plan-evidence.csv` — evidence-backed price records.
- `data/provider-source-status.csv` — provider source checks with HTTP status, check time, and one of three states: `evidenced`, `unreadable`, or `challenge`.
- `data/metadata.json` — snapshot counts and generation time.
- `tools/validate_dataset.py` — deterministic checks for required fields, URLs, timestamps, positive prices, evidence text, and duplicate slugs.
- `tools/build_snapshot.py` — rebuilds the CSV files from a compatible `offers.json` export.

## Use the data

```bash
python tools/validate_dataset.py
```

Example Python query:

```python
import csv

with open("data/hosting-plan-evidence.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

promotions = [row for row in rows if row["kind"] == "promotion"]
print(f"{len(promotions)} evidence-backed promotion rows")
```

## Evidence model

`evidenced` means an official public source returned a readable response and the configured extraction rule matched. It does **not** mean a promotion is still active unless the record also contains an official validity date.

`unreadable` means the source could not be read reliably. `challenge` means the response was an anti-bot or human-verification page. Neither state is converted into a current claim.

Prices are not normalized across currencies, billing periods, products, or commitments. The files are source evidence, not a cheapest-host ranking.

The editorial method and live presentation are documented at [HostDealRadar](https://hostdealradar.com/methodology/).

## Rebuild a snapshot

```bash
python tools/build_snapshot.py path/to/offers.json
python tools/validate_dataset.py
```

The input file is expected to contain `offers`, `source_status`, and `generated_at` fields. Only records with `claim_evidence.price.quote` are exported to the price dataset.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Do not submit coupon codes, prices, expiry dates, or billing terms without an official public source and an exact supporting quote.

## License

Code and original repository text are released under the MIT License. Provider names, short source excerpts, and linked source material remain attributable to their respective owners and are included for verification.
