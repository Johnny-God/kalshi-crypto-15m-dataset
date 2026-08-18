#!/usr/bin/env python3
"""
build_dataset.py — Refresh the public Kalshi crypto-15m dataset.

Syncs the latest collected data from the live collection store into this
repository, regenerates MANIFEST.json with current row counts and coverage,
and (optionally) commits & pushes to the remote.

Usage:
    python scripts/build_dataset.py [--push] [--commit]

By default this only stages the data (no git operations). --commit creates a
git commit locally. --push additionally pushes to the configured remote.
Publishing is deliberately gated: the daily cron runs with --commit only, so
data is captured and versioned locally every 24h without auto-publishing.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = Path.home() / "Hermes" / "model-bot" / "data"

SERIES = ["KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M",
          "KXBNB15M", "KXHYPE15M", "KXNEAR15M", "KXZEC15M"]

FILES = ["model_training_data.jsonl", "raw_snapshots.jsonl", "trades.jsonl"]

CADENCE = {
    "KXBTC15M": "0.25s", "KXETH15M": "0.5s",
    "KXSOL15M": "1.0s", "KXXRP15M": "1.0s", "KXDOGE15M": "1.0s",
    "KXBNB15M": "1.0s", "KXHYPE15M": "1.0s", "KXNEAR15M": "1.0s",
    "KXZEC15M": "1.0s",
}
ASSET = {"KXBTC15M": "Bitcoin (BTC)", "KXETH15M": "Ethereum (ETH)",
         "KXSOL15M": "Solana (SOL)", "KXXRP15M": "Ripple (XRP)",
         "KXDOGE15M": "Dogecoin (DOGE)", "KXBNB15M": "Binance Coin (BNB)",
         "KXHYPE15M": "Hyperliquid (HYPE)", "KXNEAR15M": "NEAR Protocol (NEAR)",
         "KXZEC15M": "Zcash (ZEC)"}


def count_lines(p: Path) -> int:
    if not p.exists():
        return 0
    n = 0
    with open(p, "rb") as f:
        for _ in f:
            n += 1
    return n


def sync_series(series: str) -> dict:
    """Copy a series' data files from the source store into the repo. Returns stats."""
    src_dir = SRC / series
    dst_dir = REPO / "data" / series
    dst_dir.mkdir(parents=True, exist_ok=True)

    stats = {"training_rows": 0, "raw_snapshots": 0, "live_fills": 0}
    for fname in FILES:
        src_f = src_dir / fname
        if src_f.exists():
            shutil.copy2(src_f, dst_dir / fname)
        if fname == "model_training_data.jsonl":
            stats["training_rows"] = count_lines(dst_dir / fname)
        elif fname == "raw_snapshots.jsonl":
            stats["raw_snapshots"] = count_lines(dst_dir / fname)
        elif fname == "trades.jsonl":
            stats["live_fills"] = count_lines(dst_dir / fname)
    return stats


def build_manifest() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    assets = {}
    totals = {"training_rows": 0, "raw_snapshots": 0, "live_fills": 0}
    for s in SERIES:
        st = sync_series(s)
        assets[s] = {
            "asset": ASSET[s],
            "cadence": CADENCE[s],
            **st,
        }
        for k in totals:
            totals[k] += st[k]
    return {
        "dataset": "Kalshi Crypto 15-Minute Prediction Market Dataset",
        "version": now[:10],  # date-stamped version
        "last_updated": now,
        "update_frequency": "every 24 hours",
        "format": "jsonl",
        "license": "CC BY 4.0",
        "totals": totals,
        "assets": assets,
    }


def write_manifest(mf: dict):
    out = REPO / "MANIFEST.json"
    out.write_text(json.dumps(mf, indent=2) + "\n")


def git(args: list, check=True):
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=check)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="git push to remote")
    ap.add_argument("--commit", action="store_true", help="create a local git commit")
    args = ap.parse_args()

    mf = build_manifest()
    write_manifest(mf)

    t = mf["totals"]
    print(f"[build] synced {len(mf['assets'])} assets")
    print(f"[build] totals: training={t['training_rows']:,} "
          f"raw={t['raw_snapshots']:,} fills={t['live_fills']:,}")
    print(f"[build] MANIFEST.json updated -> {mf['last_updated']}")

    if args.commit or args.push:
        git(["add", "-A"])
        msg = f"daily refresh {mf['last_updated']} — training={t['training_rows']:,} raw={t['raw_snapshots']:,} fills={t['live_fills']:,}"
        git(["commit", "-m", msg, "--allow-empty"])
        print(f"[git] committed: {msg}")
        if args.push:
            r = git(["push"], check=False)
            if r.returncode == 0:
                print("[git] pushed to remote")
            else:
                print(f"[git] PUSH FAILED: {r.stderr.strip()[:300]}", file=sys.stderr)
                return 1
    else:
        print("[build] staging only (no git). Use --commit/--push to version/publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
