# Data Dictionary

This document is the authoritative field-by-field reference for every file type in this dataset. All files are **JSON Lines (JSONL)** — one JSON object per line, no header row, UTF-8 encoded, streamable line-by-line.

---

## Series Naming

Each asset is identified by its Kalshi **series ticker** and lives in its own directory under `data/`:

| Series | Asset | Snapshot cadence |
|---|---|---|
| `KXBTC15M` | Bitcoin (BTC) | 0.25s |
| `KXETH15M` | Ethereum (ETH) | 0.5s |
| `KXSOL15M` | Solana (SOL) | 1.0s |
| `KXXRP15M` | Ripple (XRP) | 1.0s |
| `KXDOGE15M` | Dogecoin (DOGE) | 1.0s |
| `KXBNB15M` | Binance Coin (BNB) | 1.0s |
| `KXHYPE15M` | Hyperliquid (HYPE) | 1.0s |
| `KXNEAR15M` | NEAR Protocol (NEAR) | 1.0s |
| `KXZEC15M` | Zcash (ZEC) | 1.0s |

**Ticker convention:** an individual market ticker encodes the close time, e.g. `KXBTC15M-26AUG150630-30` is a Bitcoin 15-minute market closing at 06:30 on 15 August 2026.

---

## File 1: `model_training_data.jsonl` — Settlement-Labeled Training Data

One row per **snapshot** captured during a market's 15-minute life. Multiple rows share a single `ticker` (the market). Every row carries that market's final settlement as its label.

### Common fields (present on every row)

| Field | Type | Description |
|---|---|---|
| `ticker` | string | The specific Kalshi market (e.g. `KXBTC15M-26AUG150630-30`) |
| `series` | string | Asset series (e.g. `KXBTC15M`) |
| `ts` | string (ISO 8601) | Timestamp of this snapshot |
| `mid` | float 0–1 | Midpoint of the yes bid/ask at snapshot time |
| `label` | int 0/1 | Settlement label: `1` = yes (market settled up), `0` = no |
| `outcome` | string | `"yes"` or `"no"` — human-readable settlement |
| `close_time` | string (ISO 8601) | When the market settled |
| `features` | object | The full feature vector (below) |

### `features` object

| Field | Type | Description |
|---|---|---|
| `yes_mid` | float 0–1 | Mid price of the yes contract |
| `mid_centered` | float | `yes_mid - 0.5`; positive = favored to settle yes |
| `spread` | float | Yes bid–ask spread (0.001 floor) |
| `book_imbalance` | float [-1,1] | (yes depth − no depth) / total depth |
| `fav_dist` | float 0–1 | Distance of mid from 0.5 (`abs(mid_centered) * 2`) |
| `time_norm` | float 0–1 | Fraction of the 15-min window elapsed |
| `momentum_1m` | float | 1-min trade-price momentum (30s avg − 60s avg) |
| `trade_rate` | float | Trades per second over trailing 30s |
| `price_range` | float | High−low of trade prices over trailing 60s |
| `spot_ratio` | float | Spot price ÷ floor strike |
| `spot_edge` | float | `spot_ratio − 1 − mid_centered`; spot-vs-market divergence |
| `spot_ok` | int 0/1 | `1` = live spot price at snapshot, `0` = stale/degraded |
| `yes_bid` / `yes_ask` | float | Yes contract best bid / ask |
| `tape_qty_1m` | float | Contract volume traded, trailing 60s |
| `tape_value_1m` | float | Notional value traded, trailing 60s |
| `tape_imb_1m` | float [-1,1] | Signed buy/sell value imbalance, trailing 60s |
| `btc_mid_ctx` | float | Bitcoin market mid at snapshot (alts only; BTC rows = 0) |
| `btc_mom_diff` | float | BTC vs own-asset 5s momentum diff ×1000 (alts only) |
| `mid_centered_sq` | float | `mid_centered²` (nonlinear feature) |
| `fav_dist_sq` | float | `fav_dist²` (nonlinear feature) |
| `mid_centered_x_time` | float | `mid_centered × time_norm` (interaction) |
| `book_imb_x_time` | float | `book_imbalance × time_norm` (interaction) |

---

## File 2: `raw_snapshots.jsonl` — High-Frequency Order-Book Snapshots

The **lossless raw tape**. One row per snapshot, written continuously during each market's life — before any feature derivation, so all features are reproducible from this file.

| Field | Type | Description |
|---|---|---|
| `ticker` | string | The specific Kalshi market |
| `series` | string | Asset series |
| `ts` | float (epoch sec) | Snapshot timestamp (Unix epoch, seconds) |
| `yb` | float 0–1 | Yes best bid |
| `ya` | float 0–1 | Yes best ask |
| `mid` | float 0–1 | Mid of yb/ya |
| `spot` | float | Concurrent spot price in USD (null if unavailable) |
| `spot_ok` | int 0/1 | Spot freshness flag |
| `btc_mid` | float | BTC market mid at snapshot (null for BTC itself) |
| `yes_depth` | float | Aggregate yes-book quantity |
| `no_depth` | float | Aggregate no-book quantity |
| `book_imb` | float [-1,1] | (yes_depth − no_depth) / (yes_depth + no_depth) |
| `n_trades_60s` | int | Number of trades in trailing 60s |

---

## File 3: `trades.jsonl` — Live Trade Fills

Every executed trade, recorded in near-real-time from the market data feed.

| Field | Type | Description |
|---|---|---|
| `ticker` | string | The specific Kalshi market |
| `series` | string | Asset series |
| `ts` | float (epoch sec) | Trade timestamp |
| `yes_price` | float 0–1 | Execution price of the yes contract |
| `count` | float | Number of contracts in this trade |
| `no_price` | float | Implied no price (`1 − yes_price`) |
| `taker_side` | string | `"buy"` / `"sell"` (or yes/no side when available) |
| `created_time` | string (ISO 8601) | Exchange-side trade timestamp |

---

## Prices & Units

- **Contract prices** (`yes_*`, `mid`, `yb`, `ya`) are probabilities in `[0, 1]` — the price of a binary contract that pays $1 if it settles yes.
- **`spot`** is the underlying crypto spot price in **US dollars**.
- **`count`** is in **contracts** (one contract pays $1 at settlement).
- Timestamps are **UTC** (ISO 8601 strings or Unix epoch seconds as indicated).

---

## Reading the Data

**Python:**
```python
import json
rows = [json.loads(l) for l in open("data/KXBTC15M/model_training_data.jsonl")]
```

**jq (CLI):**
```bash
jq -c 'select(.features.spot_ok == 1)' data/KXBTC15M/raw_snapshots.jsonl
```

**Pandas / PyArrow:** load each file with `pd.read_json(path, lines=True)`.
