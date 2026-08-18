# Contributing

Thanks for your interest in the Kalshi Crypto 15-Minute Prediction Market Dataset.

This is a **data repository**, so most contributions fall into a few categories:

## Report a data quality issue
If you find malformed rows, unexpected gaps, or inconsistent field values, open an issue with:
- The affected file (`data/KX*15M/*.jsonl`)
- The offending line or row
- A short description of what looks wrong

Data issues are acted on quickly because they affect every downstream user.

## Documentation & examples
Improvements to `README.md`, `docs/DATA.md`, `docs/METHODOLOGY.md`, or new usage examples in the supported languages (Python, jq, pandas) are welcome.

## Collection pipeline
The collection and refresh logic lives in `scripts/build_dataset.py`. If you improve it (new fields, better validation, additional assets), please:
- Keep the JSON Lines output format backward compatible (never break existing consumers).
- Add new fields as additive, with documented defaults for older rows.
- Test that the script runs end-to-end before submitting.

## Guidelines
- One focused change per PR.
- Update documentation alongside code changes.
- Keep the public-facing documents free of implementation-specific or market-proprietary detail.

## Getting started
```bash
# After cloning
pip install -r requirements.txt   # if present
python scripts/build_dataset.py --refresh
```

By contributing, you agree that your contributions are licensed under the repository's [CC BY 4.0](LICENSE) license.
