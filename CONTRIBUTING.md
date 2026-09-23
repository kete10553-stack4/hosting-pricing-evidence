# Contributing

Contributions should improve verifiability rather than increase row count.

For a new or changed record, include:

1. The provider's official public URL.
2. The UTC capture time.
3. The exact short quote that supports the price claim.
4. The response status and source state.
5. A stable slug that does not collide with an existing record.

Do not submit third-party coupon pages, forum claims, inferred currencies, inferred billing periods, estimated expiry dates, or copied affiliate descriptions.

Run the validator before opening a pull request:

```bash
python tools/validate_dataset.py
```
