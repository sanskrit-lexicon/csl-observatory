#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_readme_visuals.py — per-dictionary README progress bars (H7720).

Renders a compact, committed static SVG progress card for any dictionary key,
for embedding in dictionary-repo READMEs (pilot: MWS docs/assets/). Data source
is the committed OBS-T release snapshot — never a live query — so the same
committed inputs always regenerate a byte-identical SVG.

Inputs (all committed in this repo):
  data/manifest.json                                — org snapshot metadata (snapshot_date)
  observatory/site/src/data/obs_t_dict.csv          — per-dictionary correction events
  observatory/site/src/data/obs_t_summary.json      — org-wide events total + date range

The bar scale is the largest per-dictionary event count in the snapshot, so a
card shows the dictionary's correction volume relative to the org maximum.
Every number on the card cites the snapshot in its caption (readme-truth-pass).

Refresh cadence: monthly, riding the correction-batch PR — re-run with --all,
commit the regenerated assets/readme/*.svg together with the refreshed snapshot
files they cite.

Usage:
  python tools/render_readme_visuals.py --dict mw
  python tools/render_readme_visuals.py --dict mw --out /path/to/mws/docs/assets/progress-mw.svg
  python tools/render_readme_visuals.py --all          # regenerate every committed card

Stdlib only; no network, no fonts embedded (labels are ASCII dict codes and
digits), output is deterministic (no timestamps).
"""
import argparse
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST_PATH = os.path.join(ROOT, "data", "manifest.json")
DICT_CSV_PATH = os.path.join(ROOT, "observatory", "site", "src", "data", "obs_t_dict.csv")
SUMMARY_PATH = os.path.join(ROOT, "observatory", "site", "src", "data", "obs_t_summary.json")
DEFAULT_OUT_DIR = os.path.join(ROOT, "assets", "readme")

# Fixed palette — no gradients, no external services (anti-slop fig canon).
INK = "#111827"
MUTED = "#6b7280"
BAR = "#0f4c81"
TRACK = "#e5e7eb"
RULE = "#d1d5db"

FONT = "Helvetica, Arial, sans-serif"

CARD_W = 640
CARD_H = 132
PAD = 12.0
BAR_X = PAD
BAR_W = CARD_W - 2 * PAD
BAR_H = 14.0


def load_inputs():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(SUMMARY_PATH, encoding="utf-8") as f:
        summary = json.load(f)
    rows = {}
    with open(DICT_CSV_PATH, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows[row["dict"]] = {
                "events": int(row["events"]),
                "entries": int(row["entries"]),
                "per_1k": row["per_1k_entries"],
            }
    if not rows:
        raise SystemExit("no rows in " + DICT_CSV_PATH)
    return manifest, summary, rows


def fmt(n):
    return f"{n:,}"


def render_card(key, row, org_max, org_max_key, snapshot_date, date_range):
    """Deterministic SVG string for one dictionary card."""
    code = key.upper()
    share = row["events"] / org_max
    filled = round(BAR_W * share, 2)
    y_title = 26.0
    y_bar = 40.0
    y_rule = y_bar + BAR_H + 8.0
    y_sub = y_rule + 16.0
    y_cap1 = y_sub + 26.0
    y_cap2 = y_cap1 + 15.0
    out = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="{code} corrections progress card">
  <rect width="{CARD_W}" height="{CARD_H}" fill="#ffffff"/>
  <text x="{PAD}" y="{y_title}" font-family="{FONT}" font-size="16" font-weight="bold" fill="{INK}">{code}</text>
  <text x="{CARD_W - PAD}" y="{y_title}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{INK}">{fmt(row['events'])} corrections recorded</text>
  <rect x="{BAR_X}" y="{y_bar}" width="{BAR_W}" height="{BAR_H}" rx="3" fill="{TRACK}"/>
  <rect x="{BAR_X}" y="{y_bar}" width="{filled}" height="{BAR_H}" rx="3" fill="{BAR}"/>
  <line x1="{BAR_X}" y1="{y_rule}" x2="{BAR_X + BAR_W}" y2="{y_rule}" stroke="{RULE}" stroke-width="1"/>
  <text x="{PAD}" y="{y_sub}" font-family="{FONT}" font-size="11" fill="{MUTED}">scale: {fmt(org_max)} in the most-corrected dictionary ({org_max_key.upper()}) &#183; {fmt(row['entries'])} entries in {code} &#183; {row['per_1k']} corrections per 1,000 entries</text>
  <text x="{PAD}" y="{y_cap1}" font-family="{FONT}" font-size="10" fill="{MUTED}">OBS-T correction events {date_range[0]}&#8211;{date_range[1]} &#183; org snapshot {snapshot_date} &#183; data: sanskrit-lexicon/csl-observatory</text>
  <text x="{PAD}" y="{y_cap2}" font-family="{FONT}" font-size="10" fill="{MUTED}">Corrections are recorded against the canonical source via change files &#8212; see the correction workflow in sanskrit-lexicon/csl-corrections.</text>
</svg>
"""
    return out


def main():
    ap = argparse.ArgumentParser(description="Render per-dictionary README progress SVGs (H7720).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dict", dest="dict_key", help="dictionary key, e.g. mw")
    g.add_argument("--all", action="store_true", help="regenerate every card into assets/readme/")
    ap.add_argument("--out", help="output path (default: assets/readme/<key>-progress.svg)")
    args = ap.parse_args()

    manifest, summary, rows = load_inputs()
    org_max_key = max(rows, key=lambda k: rows[k]["events"])
    org_max = rows[org_max_key]["events"]
    snapshot_date = manifest["snapshot_date"]
    date_range = summary["dateRange"]

    targets = sorted(rows) if args.all else [args.dict_key.lower()]
    for key in targets:
        if key not in rows:
            sys.exit(f"unknown dict key {key!r}; known: {', '.join(sorted(rows))}")
        svg = render_card(key, rows[key], org_max, org_max_key, snapshot_date, date_range)
        out = args.out if args.out else os.path.join(DEFAULT_OUT_DIR, f"{key}-progress.svg")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"wrote {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
