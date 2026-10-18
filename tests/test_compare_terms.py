import csv
from decimal import Decimal
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compare_terms import cash_model


class ContractCashCases(unittest.TestCase):
    def test_short_horizon_still_requires_whole_prepaid_term(self):
        result = cash_model("143.52", 48, 12, "USD")
        self.assertEqual(result["cash_required_before_tax_calculated"], "143.52")
        self.assertEqual(result["prepaid_months_after_horizon"], 36)

    def test_renewal_at_horizon_boundary_not_counted(self):
        self.assertEqual(cash_model("120", 12, 12, "USD")["cash_required_before_tax_calculated"], "120.00")

    def test_missing_renewal_term_is_unknown(self):
        result = cash_model("120", 12, 13, "USD", "20")
        self.assertIsNone(result["cash_required_before_tax_calculated"])
        self.assertEqual(result["status"], "unknown_renewal_term_or_rate")

    def test_annual_renewal_is_full_block_even_for_one_extra_month(self):
        result = cash_model("120", 12, 13, "USD", "20", 12)
        self.assertEqual(result["cash_required_before_tax_calculated"], "360.00")
        self.assertEqual(result["prepaid_months_after_horizon"], 11)

    def test_two_monthly_renewals_and_explicit_extras(self):
        result = cash_model("120", 12, 14, "USD", "20", 1, "3", "5")
        self.assertEqual(result["cash_required_before_tax_calculated"], "207.00")

    def test_reject_nonfinite_and_negative_inputs(self):
        for value in ("NaN", "Infinity", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cash_model(value, 12, 12, "USD")

    def test_reject_invalid_terms(self):
        for months in (0, -1, True, 1.5):
            with self.subTest(months=months), self.assertRaises(ValueError):
                cash_model("120", months, 12, "USD")

    def test_snapshot_has_traceable_complete_rows(self):
        with (ROOT / "data" / "complete-plan-terms.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows)
        self.assertEqual(len(rows), len({r["plan_id"] for r in rows}))
        metadata = json.loads((ROOT / "data" / "complete-plan-terms-metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["rows"], len(rows))
        self.assertEqual(metadata["providers"], len({r["provider"] for r in rows}))
        for row in rows:
            with self.subTest(plan=row["plan_id"]):
                self.assertEqual((Decimal(row["first_term_total"]) / int(row["commitment_months"])).quantize(Decimal("0.01")), Decimal(row["monthly_equivalent"]))
                self.assertTrue(all(row[k].startswith("https://") for k in ("upfront_source_url", "term_source_url", "renewal_source_url")))
                self.assertEqual(row["renewal_term_months"], "")


if __name__ == "__main__":
    unittest.main()
