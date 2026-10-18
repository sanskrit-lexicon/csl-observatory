#!/usr/bin/env python3
"""Corpus-wide mānadaṇḍa census over the DCS CoNLL-U flatten (H6052).

Counts the kāvya compound mānadaṇḍa ("measuring rod", Kumārasaṃbhava 1.1)
across the full DCS corpus as flattened into VisualDCS `dcs_full.sqlite`,
plus the wider compound family "X-…-daṇḍa" for register/era context.

Method (token-level, sandhi-safe):
  * exact compound  — a token whose lemma starts with `daṇḍ`, whose feat_case
    is NOT `Cpd` (i.e. it is the inflected FINAL member), and whose
    immediately preceding token is a `Cpd` member with lemma `māna`;
    the full member run is walked back to reconstruct the compound.
  * family          — every compound-final `daṇḍa` token regardless of the
    first members. This deliberately EXCLUDES sandhi-fused plain daṇḍa
    (tasmāt+daṇḍaḥ → `tasmāddaṇḍaḥ` on the surface is three plain tokens,
    not a Cpd run) and non-final members.
  * surface guard   — an independent substring scan `mānadaṇḍ` over the
    sandhied sentence text must agree with the token-level exact set
    (sent_id equality); a mismatch fails --selftest.

Time slots come from the DCS chapter-info.xml (dcsTimeSlot 1..5,
1 = Vedic oldest); era labels follow the VisualDCS Fonetika slot_era_map.

Outputs (repo-relative, canonical committed home = the site data dir,
mirrored by the catalog in scripts/data_index.py):
  observatory/site/src/data/manadanda_census.csv          — one row per mānadaṇḍa attestation
  observatory/site/src/data/manadanda_danda_family.csv    — one row per compound-final daṇḍa token

Both are registered in scripts/data_index.py (the refresh workflow's
`data_index.py --check` gate covers them).

Usage:
  python scripts/manadanda_census.py --selftest
  python scripts/manadanda_census.py            # writes CSVs + prints summary

Default paths assume the sibling VisualDCS checkout; override with
--db / --chapter-info. Stdlib only, per repo convention.
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"

DEFAULT_DB = Path.home() / "Documents/GitHub/VisualDCS/src/DCS-data-2026/dcs_full.sqlite"
DEFAULT_CHAPTER_INFO = (
    Path.home()
    / "Documents/GitHub/VisualDCS/src/DCS-data-2026/conllu/lookup/chapter-info.xml"
)

# VisualDCS derived-data/Fonetika/varga-series-diachrony/slot_era_map.csv
SLOT_ERAS = {
    "1": ("Vedic (Saṃhitā–Brāhmaṇa–Śrautasūtra)", "~1500–500 BCE"),
    "2": ("Epic & early śāstra", "~400 BCE–200 CE"),
    "3": ("Early classical", "~200–600 CE"),
    "4": ("Later classical / early medieval", "~600–1000 CE"),
    "5": ("Medieval / late", "~1000–1700 CE"),
}


def load_slots(chapter_info: Path) -> dict[str, tuple[str, str]]:
    """chapterId -> (slot, era_en). Fails loud when the file is absent."""
    if not chapter_info.is_file():
        raise SystemExit(f"chapter-info.xml not found: {chapter_info}")
    out: dict[str, tuple[str, str]] = {}
    for ch in ET.parse(chapter_info).getroot().iter("chapter"):
        cid = (ch.findtext("chapterId") or "").strip()
        slot = (ch.findtext("dcsTimeSlot") or "").strip()
        if cid and slot:
            out[cid] = (slot, SLOT_ERAS.get(slot, ("?", "?"))[0])
    return out


def token_rows(db: sqlite3.Connection) -> dict[str, list[dict]]:
    sids = [r[0] for r in db.execute("SELECT DISTINCT sentence_id FROM token WHERE lemma LIKE 'daṇḍ%'")]
    if not sids:
        return {}
    ph = ",".join("?" * len(sids))
    rows = db.execute(
        f"""
        SELECT t.sentence_id, t.idx, t.form, t.lemma, t.feat_case, t.feat_gender, t.feat_number,
               s.sent_id AS ssid, s.sent_counter, s.sent_subcounter, s.text_sandhied,
               tx.name AS text_name, ch.ref, ch.chapter_id
        FROM token t
        JOIN sentence s ON t.sentence_id = s.id
        JOIN chapter ch ON s.chapter_id = ch.chapter_id
        JOIN text tx ON ch.text_id = tx.text_id
        WHERE t.sentence_id IN ({ph})
        ORDER BY t.sentence_id, t.idx
        """,
        sids,
    )
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(str(r["sentence_id"]), []).append(dict(r))
    return out


def scan(db_path: Path, chapter_info: Path) -> dict:
    if not db_path.is_file():
        raise SystemExit(f"dcs_full.sqlite not found: {db_path}")
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    slots = load_slots(chapter_info)

    n_tokens = db.execute("SELECT COUNT(*) FROM token").fetchone()[0]
    n_danda_lemma = db.execute("SELECT COUNT(*) FROM token WHERE lemma = 'daṇḍa'").fetchone()[0]

    exact: list[dict] = []
    family: list[dict] = []
    for _sid, toks in token_rows(db).items():
        for i, tk in enumerate(toks):
            if not tk["lemma"].startswith("daṇḍ") or tk["feat_case"] == "Cpd":
                continue
            if i == 0 or toks[i - 1]["feat_case"] != "Cpd":
                continue
            j = i - 1
            while j > 0 and toks[j - 1]["feat_case"] == "Cpd":
                j -= 1
            members = [t["lemma"] for t in toks[j:i]]
            comp = "+".join(members + ["daṇḍa"])
            slot, era = slots.get(str(tk["chapter_id"]), ("?", "?"))
            row = {
                "compound": comp,
                "sent_id": tk["ssid"],
                "text": tk["text_name"],
                "ref": tk["ref"],
                "sent_counter": tk["sent_counter"],
                "sent_subcounter": tk["sent_subcounter"],
                "form": tk["form"],
                "case": tk["feat_case"] or "",
                "gender": tk["feat_gender"] or "",
                "number": tk["feat_number"] or "",
                "slot": slot,
                "era": era,
                "sentence": toks[0]["text_sandhied"],
            }
            family.append(row)
            if toks[i - 1]["lemma"] == "māna":
                exact.append(row)

    surface = {
        r[0]
        for r in db.execute("SELECT sent_id FROM sentence WHERE text_sandhied LIKE '%mānadaṇḍ%'")
    }
    db.close()
    return {
        "n_tokens": n_tokens,
        "n_danda_lemma": n_danda_lemma,
        "exact": exact,
        "family": family,
        "surface_sent_ids": surface,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    cols = [
        "compound", "sent_id", "text", "ref", "sent_counter", "sent_subcounter",
        "form", "case", "gender", "number", "slot", "era", "sentence",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def selftest(db_path: Path, chapter_info: Path) -> None:
    res = scan(db_path, chapter_info)
    exact, family = res["exact"], res["family"]
    # 1. exactly the two known attestations, by sent_id
    got = {r["sent_id"] for r in exact}
    assert got == {"485110", "364306"}, f"exact set drifted: {got}"
    # 2. token-level and surface scans agree
    assert got == res["surface_sent_ids"], (
        f"token vs surface mismatch: token={got} surface={res['surface_sent_ids']}"
    )
    # 3. both rows are Nom Sg Masc, slot 3, kāvya-register texts
    for r in exact:
        assert (r["case"], r["gender"], r["number"]) == ("Nom", "Masc", "Sing"), r
        assert r["slot"] == "3", r
        assert r["text"] in {"Kumārasaṃbhava", "Kāvyālaṃkāra"}, r
    # 4. family is a sane superset; every compound ends in +daṇḍa
    assert len(family) >= 400, f"family implausibly small: {len(family)}"
    assert all(r["compound"].endswith("+daṇḍa") for r in family)
    assert {r["compound"] for r in exact} <= {r["compound"] for r in family}
    # 5. every family row resolved a slot
    assert all(r["slot"] != "?" for r in family), "unslotted chapters in family"
    # 6. negative control: nonsense pattern has no surface hits
    assert not res["surface_sent_ids"] - got
    # 7. denominators sane
    assert res["n_tokens"] > 5_000_000 and res["n_danda_lemma"] > 1_000
    print("selftest PASS:", len(exact), "mānadaṇḍa;", len(family), "compound-final daṇḍa;",
          len({r['compound'] for r in family}), "distinct compounds")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--chapter-info", type=Path, default=DEFAULT_CHAPTER_INFO)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest(args.db, args.chapter_info)
        return

    res = scan(args.db, args.chapter_info)
    DATA.mkdir(exist_ok=True)
    write_csv(DATA / "manadanda_census.csv", res["exact"])
    write_csv(DATA / "manadanda_danda_family.csv", res["family"])

    per_m = 1_000_000 * len(res["exact"]) / res["n_tokens"]
    fam_counter = Counter(r["compound"] for r in res["family"])
    era_counter = Counter(r["era"] for r in res["family"])
    print(f"tokens: {res['n_tokens']:,}")
    print(f"lemma 'daṇḍa' tokens: {res['n_danda_lemma']:,}")
    print(f"mānadaṇḍa attestations: {len(res['exact'])}  ({per_m:.2f} per 1M tokens)")
    for r in res["exact"]:
        print(f"  - {r['text']} {r['ref']} sent={r['sent_id']} ctr={r['sent_counter']}.{r['sent_subcounter']} slot={r['slot']}")
    print(f"compound-final daṇḍa: {len(res['family'])} tokens, {len(fam_counter)} distinct compounds")
    print("family top-10:", fam_counter.most_common(10))
    print("family by era:", dict(era_counter))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
