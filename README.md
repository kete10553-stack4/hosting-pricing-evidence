# Hosting Pricing Evidence

A source-linked hosting-price dataset, contract-cash calculator, and evidence validators. All tools use the Python standard library and run locally without an account or network requests.

## Complete contract examples and cash calculator

The October 18, 2026 export contains **41 dated complete plan examples across 20 providers**, matching the source site's published comparison rows. Their original official-page checks range from September 26 to October 16, 2026; exporting them does not recheck today's prices. Every row includes the recorded first-term total, commitment, renewal monthly rate, currency, review date and three field-specific official source URLs.

- [Complete plan terms (CSV)](data/complete-plan-terms.csv)
- [Provenance, selection rule and rejected incomplete inputs](data/complete-plan-terms-metadata.json)
- [Contract, billing and recovery worksheet (Markdown)](checklists/hosting-contract-and-recovery.md)
- [Offline cash calculator](tools/compare_terms.py)

List the dated examples, then calculate one scenario:

```bash
python tools/compare_terms.py --list
python tools/compare_terms.py --plan hostinger-premium-web-hosting-48-month-card --horizon-months 12
```

That recorded example requires the entire **USD 143.52** initial payment, covering **48 months**, even for a **12-month** use horizon; USD 2.99 is the calculated monthly equivalent, not a monthly payment option. The row was checked September 30, 2026. It is not a price guarantee or purchase test.

For a provider-independent example, supply your own numbers:

```bash
python tools/compare_terms.py --initial-total 120 --initial-months 12 --currency USD --horizon-months 13 --renewal-monthly 20
```

The result is `unknown_renewal_term_or_rate`: a renewal monthly rate does not establish the next invoice's billing term. If your actual quote specifies a 12-month renewal, supply it explicitly:

```bash
python tools/compare_terms.py --initial-total 120 --initial-months 12 --currency USD --horizon-months 13 --renewal-monthly 20 --renewal-months 12
```

This **hypothetical input**, not a provider quote, produces USD 360 before tax: USD 120 + one prepaid renewal block of 12 × USD 20. Eleven prepaid months remain after the chosen horizon. JSON output preserves the formula, inputs, provenance and assumptions. It never converts currencies or infers taxes, refunds, overages or future price changes. Add-ons default to an explicit zero-cost scenario assumption; use `--monthly-addons` and `--one-time` to supply known costs.

Run the offline checks:

```bash
python tools/validate_dataset.py
python -m unittest discover -s tests -v
```

To reproduce the complete-term export, obtain `data/offers.json` and `site/compare/index.html` from the exact source commit recorded in the metadata, then run:

```bash
python tools/export_complete_terms.py offers.json --compare-html compare.html --source-commit FULL_SOURCE_COMMIT_SHA
```

`renewal_term_months` is intentionally blank in the CSV. This export does not infer a renewal term from the original commitment. Reproduction preserves factual rows; the export timestamp will reflect your new export.

## Earlier automated evidence snapshot

The following two files remain the original **September 23, 2026** snapshot. They are historical source captures, not current offers. Their generation date and counts remain in `data/metadata.json`.

The snapshot is built from public provider pages. Each published price row keeps the official source URL, capture time, a short quote containing the price, and a SHA-256 identifier for the captured source. Rows without price-level evidence are excluded instead of being filled from memory.

### What is included

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
