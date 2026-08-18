# Kalshi Crypto 15-Minute Prediction Market Dataset

**High-frequency order-book snapshots, trade fills, and settlement-labeled training data from Kalshi's 15-minute cryptocurrency binary markets.**

This repository publishes a continuously collected, settlement-labeled dataset from Kalshi's crypto prediction markets — the 15-minute binary markets tracking Bitcoin (BTC), Ethereum (ETH), Solana (SOL), Ripple (XRP), Dogecoin (DOGE), Binance Coin (BNB), Hyperliquid (HYPE), NEAR Protocol (NEAR), and Zcash (ZEC). It is one of the few publicly available, continuously updated prediction-market microstructure datasets focused specifically on short-duration crypto binaries.

---

## Quick Stats

| Metric | Value |
|---|---|
| **Market type** | 15-minute binary "Up/Down" prediction markets |
| **Assets** | BTC, ETH, SOL, XRP, DOGE, BNB, HYPE, NEAR, ZEC |
| **Training rows** | 90,367+ |
| **Raw order-book snapshots** | 93,950+ |
| **Live trade fills** | recording continuously |
| **Snapshot cadence** | 0.25s (BTC) / 0.5s (ETH) / 1.0s (alts) |
| **Update frequency** | Every 24 hours |
| **Format** | JSON Lines (JSONL), one JSON object per line |
| **License** | [CC BY 4.0](LICENSE) |
| **Last updated** | See `MANIFEST.json` |

---

## What Is This Data?

Kalshi operates regulated prediction markets where traders buy and sell contracts that pay out if a stated outcome occurs. Its **crypto 15-minute markets** are short-duration binary contracts that settle every 15 minutes based on whether an asset's price closes above or below a fixed strike level.

This dataset captures the full lifecycle of those markets:

1. **Raw order-book snapshots** — the bid/ask ladder, best yes/no prices, and aggregate depth for each asset's active market, sampled at sub-second to 1-second cadence.
2. **Trade fills** — every executed trade, with price, size, and taker direction, recorded in near-real-time.
3. **Settlement-labeled training data** — each market's outcome (yes/no) is written once the market settles, so every snapshot is labeled with the ground-truth result.

All three are available per asset in a clean, consistent JSON Lines format.

---

## Why This Data Matters

### A Missing Niche in Public Prediction-Market Data
Most publicly available prediction-market datasets cover large event markets (elections, sports, macro) at coarse granularity — daily or hourly snapshots of mid prices. **Short-duration crypto binaries are underrepresented**, yet they are among the most actively traded contracts on Kalshi. The combination of:

- **Sub-second to 1-second sampling** (not minutes or hours),
- **Full order-book depth** (not just last price),
- **Trade-level fills**, and
- **Complete settlement labels** for every market

makes this dataset unusually well suited for high-frequency microstructure research.

### What It Is Used For
This data supports a wide range of research and applications:

- **Prediction-market microstructure** — studying bid/ask spreads, order-book imbalance, liquidity, and price formation in short-horizon binary markets.
- **Market efficiency** — testing whether 15-minute crypto binaries efficiently price the underlying asset's expected move.
- **Machine learning & forecasting** — training models to estimate the probability a market settles "yes" given the order book, trade flow, and spot price; evaluating calibration and edge.
- **Quantitative finance education** — a clean, labeled, open dataset for teaching order-flow, microstructure, and time-series modeling.
- **Benchmarking** — a reproducible benchmark for comparing forecasting models across a consistent market microstructure.

---

## Repository Structure

```
kalshi-crypto-15m/
├── README.md              # This file — overview, stats, and quick start
├── LICENSE                # CC BY 4.0
├── MANIFEST.json          # Dataset version, row counts, coverage, last-updated
├── data/
│   ├── KXBTC15M/
│   │   ├── model_training_data.jsonl   # Settlement-labeled training rows
│   │   ├── raw_snapshots.jsonl          # High-frequency order-book snapshots
│   │   └── trades.jsonl                 # Live trade fills
│   ├── KXETH15M/
│   ├── KXSOL15M/
│   ├── KXXRP15M/
│   ├── KXDOGE15M/
│   ├── KXBNB15M/
│   ├── KXHYPE15M/
│   ├── KXNEAR15M/
│   └── KXZEC15M/
├── docs/
│   ├── DATA.md            # Full field-by-field data dictionary
│   └── METHODOLOGY.md     # How the data is collected and validated
└── scripts/
    └── build_dataset.py   # Refresh pipeline (runs every 24h)
```

Each asset has its own directory under `data/`, keyed by its Kalshi series ticker (e.g. `KXBTC15M` = Bitcoin 15-minute markets).

---

## Quick Start

```python
import json

# Read the settlement-labeled training data for Bitcoin 15-min markets
rows = []
with open("data/KXBTC15M/model_training_data.jsonl") as f:
    for line in f:
        rows.append(json.loads(line))

print(f"{len(rows)} labeled training rows")
print(json.dumps(rows[-1], indent=2))
```

Each line is a standalone JSON object — no header row, no nested file format, streamable line-by-line.

---

## Example: A Settlement-Labeled Training Row

```json
{
  "ticker": "KXBTC15M-26AUG150630-30",
  "series": "KXBTC15M",
  "features": {
    "yes_mid": 0.485,
    "mid_centered": -0.015,
    "spread": 0.01,
    "book_imbalance": 0.0,
    "fav_dist": 0.03,
    "time_norm": 0.4814,
    "momentum_1m": -0.0002,
    "trade_rate": 5.13,
    "price_range": 0.04,
    "spot_ratio": 0.9999,
    "spot_edge": 0.0149
  },
  "label": 0,
  "outcome": "no",
  "mid": 0.485,
  "close_time": "2026-08-15T10:30:08Z"
}
```

The `features` object captures the market state at a moment in time; `outcome`/`label` give the ground-truth settlement (`yes` = 1, `no` = 0). See **[docs/DATA.md](docs/DATA.md)** for the complete field-by-field dictionary.

---

## Data Coverage

- **Assets:** 9 crypto series — BTC, ETH, SOL, XRP, DOGE, BNB, HYPE, NEAR, ZEC.
- **Cadence:** BTC snapshots every 0.25 seconds, ETH every 0.5 seconds, all others every 1.0 second.
- **Time span:** Continuous, growing from the collection start date onward (see `MANIFEST.json` for exact coverage).
- **Labels:** Every market in the training data carries its actual settlement outcome.

---

## Methodology & Data Quality

Data is collected directly from Kalshi's public market data interfaces in near-real-time and appended continuously to per-asset JSON Lines files. Key quality controls:

- **Spot price alignment** — snapshots include a concurrent spot reference price so researchers can measure the gap between the prediction-market price and the underlying spot.
- **Data-quality flagging** — a `spot_ok` flag marks snapshots where the spot reference was live vs. stale, so unreliable rows can be down-weighted.
- **Continuous raw tape** — the raw order-book tape is written losslessly before any feature derivation, so features can be recomputed from source data.
- **Full details in** **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)**.

---

## Comparison to Other Datasets

| Dataset | Cadence | Order book | Trade fills | Settlement labels | Crypto 15-min focus |
|---|---|---|---|---|---|
| **This dataset** | 0.25–1s | ✅ full depth | ✅ | ✅ | ✅ |
| Large event-market archives | hours/days | ❌ | partial | ✅ | ❌ |
| Polymarket datasets | varies | ❌ | ✅ | ✅ | ❌ |

---

## Citation

If you use this dataset in research, please cite it:

```bibtex
@misc{kalshi_crypto_15m,
  author       = {Kalshi Crypto 15M Dataset Contributors},
  title        = {Kalshi Crypto 15-Minute Prediction Market Dataset},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {Updated every 24 hours}
}
```

---

## License

This dataset is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. You are free to share and adapt it with attribution. See [LICENSE](LICENSE) for the full terms.

*Kalshi is a registered CFTC-designated contract market. This dataset contains independently collected public market data and is provided for research and educational purposes only. It is not investment advice, and no dataset contributor is affiliated with or endorsed by Kalshi.*

---

## Updates & Maintenance

This dataset is **refreshed automatically every 24 hours**. Each refresh appends newly collected data, updates row counts, and bumps the version in `MANIFEST.json`.

Issues, feature requests, and contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
