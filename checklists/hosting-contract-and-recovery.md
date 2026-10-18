# Hosting contract and recovery worksheet

Use one copy for each actual quote. Leave missing fields blank. Do not substitute a crossed-out price or a new-customer promotion for a renewal invoice.

## Quote identity

- Provider, named product, infrastructure provider and region:
- Configuration: CPU / RAM / storage / transfer allowance:
- Currency and tax treatment:
- Official URL and observation date, including time zone:
- Screenshot or saved quote reference, with personal details removed:

## Cash and commitments

- Total payable for the initial term:
- Initial commitment length:
- Payment frequency (monthly payment and monthly commitment are different):
- Published renewal rate:
- Renewal term and total (do not infer from the initial term):
- Backup, email, support, control-panel and other required add-ons:
- Usage charges, minimum spending and caps:
- Promotion code, eligibility, expiration and discount duration, if any:
- Cancellation route, deadline and any refund conditions:

## Recovery and migration

- Independent backup location and owner:
- Has a restore into a different server been tested? Record the date and result:
- Recovery time and extra charges observed in that test:
- DNS/IP cutover plan and any overlap payments:
- Data export, cancellation and deletion order:
- Rollback plan before the old service is removed:

## Calculations

Initial monthly equivalent = recorded initial total / recorded initial months.

This is an amortized comparison figure, not a monthly payment option. The initial prepaid amount is still due even if you only need part of the term. Use `tools/compare_terms.py` for explicit cash scenarios. A future renewal amount remains unknown unless both its rate and billing term are supplied.

## Cloudways-specific source questions

These official Help Center pages were checked for the site's October 17, 2026 trial guide; this worksheet does not perform a new account or checkout test.

- Identify Flexible versus Autonomous before relying on trial-end behavior: [standard trial upgrade](https://support.cloudways.com/en/articles/5116141-how-to-upgrade-cloudways-account-from-trial-to-full), [Autonomous trial](https://support.cloudways.com/en/articles/10061824-how-to-subscribe-autonomous-trial).
- Review payment-method state before the Autonomous trial ends; the cited instructions describe an automatic paid upgrade when a payment method was added beforehand.
- Read [monthly versus hourly billing](https://support.cloudways.com/en/articles/12157984-understanding-monthly-vs-hourly-billing-on-cloudways) and the [payment guide](https://support.cloudways.com/en/articles/5119615-how-does-cloudways-payment-system-work) for provider-specific caps, stopped-server charges, add-ons and invoice timing. Follow the current official wording; do not assume a stop button ends every charge.
