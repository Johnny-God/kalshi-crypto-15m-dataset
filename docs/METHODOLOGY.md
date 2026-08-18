# Methodology

How this dataset is collected, validated, and maintained. This document is written for researchers who need to understand the provenance and quality characteristics of the data before using it.

---

## 1. Data Source

Data is collected from **Kalshi's public market data interfaces** — the same public feed that powers Kalshi's market pages and its documented Trade API. Kalshi is a registered derivatives exchange (CFTC-designated contract market), and all data here is **public market data**, not proprietary or subscriber-only data.

### What Kalshi's 15-minute crypto markets are
A 15-minute crypto binary market is a contract that:
- Tracks one asset (BTC, ETH, SOL, XRP, DOGE, BNB, HYPE, NEAR, ZEC).
- Has a fixed **strike level** and a fixed **close time** every 15 minutes (on a repeating 15-minute grid).
- Pays **$1** if the asset's price closes at or above the strike at settlement ("yes"), **$0** otherwise ("no").
- Is continuously tradable for its entire 15-minute life.

---

## 2. Collection Architecture

### Live data feed
A persistent connection to Kalshi's streaming market-data feed supplies:
- **Quotes** — the yes/no best bid/ask.
- **Order-book deltas** — changes to the full yes/no price ladder, from which a local order book is reconstructed.
- **Trades** — every executed fill.
- **Market lifecycle events** — used to detect settlement and read the outcome.

### Snapshot cadence
Each asset is sampled on its own cadence to balance resolution against volume:

| Asset class | Cadence |
|---|---|
| BTC | 0.25s (4 samples/sec) |
| ETH | 0.5s |
| SOL, XRP, DOGE, BNB, HYPE, NEAR, ZEC | 1.0s |

### Spot price alignment
Because these are crypto markets, the prediction-market price can be compared to the **underlying spot price**. A concurrent spot reference is fetched for each asset (via public crypto exchange price feeds) and attached to every snapshot as `spot` / `spot_ratio` / `spot_edge`. This enables direct measurement of how the prediction market prices the underlying move.

---

## 3. Data Validation

Several quality controls run continuously:

- **Spot freshness flag (`spot_ok`)** — every snapshot records whether the spot reference was live (`1`) or stale/degraded (`0`). Researchers can down-weight rows where spot-derived features are unreliable.
- **Lossless raw tape** — order-book snapshots are written to disk **before** any feature derivation. All features are reproducible from the raw file, so a schema change never loses underlying market data.
- **Settlement verification** — labels are written only when a market's outcome is confirmed via lifecycle events. Where a lifecycle event is missed, the outcome is inferred from the final spot-vs-strike relationship (documented as such).

---

## 4. Update Schedule

The dataset is **refreshed automatically every 24 hours**. Each refresh:
1. Appends all data collected since the previous refresh.
2. Recomputes row counts and coverage for every asset.
3. Bumps the version and updates the `last_updated` timestamp in `MANIFEST.json`.

Because data is appended continuously, the repository reflects a rolling, always-growing history from its collection start date.

---

## 5. Known Limitations

- **Coverage begins at collection start** — there is no backfilled history for periods before collection began. This is forward-only data.
- **Collection gaps** — brief network interruptions may create short gaps in the raw tape. The `ts` field allows precise gap detection.
- **Spot reference rate limits** — some spot sources are rate-limited; `spot_ok` marks rows where the reference may be stale.

---

## 6. Reproducibility

The exact collection pipeline (`scripts/build_dataset.py`) is included in this repository. It is intentionally simple and transparent: read the public feed, append JSON Lines, validate, publish. Anyone with the same collection start point can reproduce the same data from Kalshi's public interfaces.

---

## 7. Fair Use & Attribution

This dataset is independently collected public market data, provided under the **CC BY 4.0** license for research and education. It is not affiliated with, endorsed by, or sponsored by Kalshi. See [LICENSE](../LICENSE) for full terms. If you use this dataset, please cite it (citation available in the [README](../README.md)).
