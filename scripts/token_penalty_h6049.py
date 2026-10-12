#!/usr/bin/env python3
"""Devanagari token penalty on our corpora (H6049).

Replicates the script-penalty methodology of arXiv:2609.12960 ("Fewer Words,
Not Fewer Tokens: Measuring the Sanskrit Tokenization Penalty per Proposition")
on estate data:

  * dictionary articles — MW sample ~10k entries (Sanskrit layer: headword k1
    + all <s>/<s1> spans), read READ-ONLY from the local csl-orig checkout
    (never committed);
  * prose — DCS 2026 sentences (restricted local sqlite, aggregates only are
    committed) from five prose texts.

Unit text is transliterated into four schemes (Devanagari, IAST,
Harvard-Kyoto, SLP1) and token-counted under five tokenizer arms:
GPT BPE (o200k_base + cl100k_base), LLaMA-3 BPE, GLM-4 BPE, ByT5 (= UTF-8
bytes), plus the derived TransLIST-style "transliterate-then-tokenize" arm.

Penalty(scheme, tokenizer) = mean tokens per unit in scheme / mean tokens per
unit in SLP1 (the paper's reference script), with 95% bootstrap percentile
intervals (unit-level paired resampling, B=2000) and a two-sided paired
sign-flip permutation test (B=10000). The ratio factorises into a
character-length ratio and a tokens-per-character ratio, reported separately.

Outputs (committed):
  data/token_penalty_h6049/mw_units_counts.tsv.gz      per-entry counts
  data/token_penalty_h6049/dcs_units_counts.tsv.gz     per-sentence counts
  data/token_penalty_h6049/penalty_matrix.csv          all cells + CIs + p
  reports/devanagari_token_penalty.md                  the report

Usage:
  python scripts/token_penalty_h6049.py \
      --mw-src  ~/Documents/GitHub/csl-orig/v02/mw/mw.txt \
      --dcs-db  ~/Documents/GitHub/VisualDCS/src/DCS-data-2026/dcs_full.sqlite

Deps (non-stdlib): numpy, tiktoken, transformers, indic-transliteration.
Deterministic: fixed seeds, fixed strides. No network at run time beyond
one-time tokenizer-file downloads (HF/tiktoken caches).
"""

from __future__ import annotations

import argparse
import gzip
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

import numpy as np
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SCHEMES, transliterate

REPO = Path(__file__).resolve().parent.parent
SCHEMES_ORDER = ["devanagari", "iast", "hk", "slp1"]
SCHEME_CONST = {
    "devanagari": sanscript.DEVANAGARI,
    "iast": sanscript.IAST,
    "hk": sanscript.HK,
    "slp1": sanscript.SLP1,
}
REF = "slp1"  # reference script, following arXiv:2609.12960
SEED_BOOT, SEED_PERM = 42, 43
B_BOOT, B_PERM = 2000, 10000
DCS_PROSE_TEXTS = [
    "Tantrākhyāyikā",      # Pañcatantra recension, prose
    "Daśakumāracarita",    # prose novel
    "Hitopadeśa",          # prose+verse fable collection
    "Narmamālā",           # prose satire
    "Kathāsaritsāgara",    # story cycle (mixed prose/verse)
]
MW_TARGET_N, DCS_TARGET_N = 10000, 2000
MIN_UNIT_CHARS = 20

LLAMA_CHAIN = [
    "unsloth/llama-3.2-3b-instruct",
    "unsloth/Llama-3.2-3B-Instruct",
    "NousResearch/Meta-Llama-3-8B",
    "hf-internal-testing/llama-tokenizer",
]
GLM_CHAIN = [
    "zai-org/glm-4-9b-chat-hf",
    "THUDM/glm-4-9b-chat-hf",
    "zai-org/glm-4-9b-chat",
    "THUDM/glm-4-9b-chat",
]


# ---------------------------------------------------------------- samples ---

def mw_entries(path: Path, limit: int):
    """Parse csl-orig v02 mw.txt read-only; return [(entry_id, slp1_text)]."""
    raw = path.read_text(encoding="utf-8")
    entries = []
    for chunk in raw.split("<LEND>"):
        m = re.match(r"\s*<L>([\d.]+)", chunk)
        if not m:
            continue
        k1 = re.search(r"<k1>([^<]*)", chunk)
        if k1 is None:
            continue
        spans = re.findall(r"<s\d?>(.*?)</s\d?>", chunk, re.S)
        text = " ".join([k1.group(1)] + [s.strip() for s in spans if s.strip()])
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) >= MIN_UNIT_CHARS:
            entries.append((m.group(1), text))
    stride = max(1, -(-len(entries) // limit))  # ceil div
    return entries[::stride][:limit]


def dcs_sentences(db_path: Path, limit: int):
    """Stride-sample prose sentences (IAST) from the local DCS sqlite."""
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    q = db.execute
    names = ",".join("?" * len(DCS_PROSE_TEXTS))
    rows = q(
        f"""SELECT s.id, s.text_sandhied FROM sentence s
            JOIN chapter c ON s.chapter_id = c.chapter_id
            JOIN text t ON c.text_id = t.text_id
            WHERE t.name IN ({names}) ORDER BY s.id""",
        DCS_PROSE_TEXTS,
    ).fetchall()
    rows = [(i, re.sub(r"\s+", " ", t).strip()) for i, t in rows]
    rows = [(i, t) for i, t in rows if len(t) >= MIN_UNIT_CHARS]
    stride = max(1, -(-len(rows) // limit))
    return rows[::stride][:limit]


# ------------------------------------------------------------- tokenizers ---

def build_tokenizers():
    """Return OrderedDict name -> (vocab_size, fn(texts)->list[int])."""
    import tiktoken

    toks = {}

    def tik(name: str, enc_name: str):
        enc = tiktoken.get_encoding(enc_name)
        toks[name] = (enc.n_vocab, lambda t, e=enc: [len(x) for x in e.encode_ordinary_batch(t)])

    tik("gpt-o200k", "o200k_base")
    tik("gpt-cl100k", "cl100k_base")

    def hf(name: str, chain: list[str]):
        from transformers import AutoTokenizer

        for repo in chain:
            try:
                tk = AutoTokenizer.from_pretrained(repo, use_fast=True)
                hf.resolved[name] = repo

                def make_fn(k=tk):
                    return lambda t: [len(x) for x in k(t, add_special_tokens=False)["input_ids"]]

                toks[name] = (tk.vocab_size, make_fn())
                return
            except Exception as e:  # noqa: BLE001 — try next mirror
                print(f"  [{name}] {repo} failed: {type(e).__name__}: {e}", file=sys.stderr)
        raise RuntimeError(f"no mirror in chain worked for {name}: {chain}")

    hf.resolved = {}
    hf("llama3", LLAMA_CHAIN)
    hf("glm4", GLM_CHAIN)
    build_tokenizers.resolved = dict(hf.resolved)

    toks["byt5"] = (256, lambda t: [len(s.encode("utf-8")) for s in t])  # byte-level
    return toks


# ------------------------------------------------------------------ stats ---

def cell_stats(tok_s: np.ndarray, tok_ref: np.ndarray):
    """Penalty vs reference with bootstrap CI + sign-flip permutation p."""
    rng = np.random.default_rng(SEED_BOOT)
    n = len(tok_s)
    boots = np.empty(B_BOOT)
    for i in range(0, B_BOOT, 250):  # chunked to bound memory
        j = min(B_BOOT, i + 250)
        idx = rng.integers(0, n, size=(j - i, n))
        boots[i:j] = tok_s[idx].mean(axis=1) / tok_ref[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    d = np.log(tok_s / tok_ref)
    obs = d.mean()
    rng2 = np.random.default_rng(SEED_PERM)
    signs = rng2.choice([-1.0, 1.0], size=(B_PERM, n))
    null = signs @ d / n
    p = float((np.abs(null) >= abs(obs)).mean())
    return float(lo), float(hi), p


# ----------------------------------------------------------------- driver ---

def measure(units, source_scheme, tok_fns):
    """units: [(id, text_in_source_scheme)]. Returns per-scheme char + token arrays."""
    texts_by_scheme = {}
    for sch in SCHEMES_ORDER:
        if sch == source_scheme:
            texts_by_scheme[sch] = [t for _, t in units]
        else:
            texts_by_scheme[sch] = [
                transliterate(t, SCHEME_CONST[source_scheme], SCHEME_CONST[sch]) for _, t in units
            ]
    chars = {s: np.array([len(t) for t in texts_by_scheme[s]], dtype=np.int64)
             for s in SCHEMES_ORDER}
    counts = {}
    for tname, (_, fn) in tok_fns.items():
        for s in SCHEMES_ORDER:
            counts[(tname, s)] = np.array(fn(texts_by_scheme[s]), dtype=np.int64)
    return texts_by_scheme, chars, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mw-src", type=Path, required=True)
    ap.add_argument("--dcs-db", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=REPO / "data" / "token_penalty_h6049")
    args = ap.parse_args()

    print("building tokenizers …")
    toks = build_tokenizers()
    resolved = getattr(build_tokenizers, "resolved", {})
    for k, (v, _) in toks.items():
        print(f"  {k}: vocab={v}" + (f"  repo={resolved[k]}" if k in resolved else ""))

    corpora = {}
    mw = mw_entries(args.mw_src, MW_TARGET_N)
    print(f"MW entries sampled: {len(mw)}")
    corpora["mw"] = ("slp1", mw)
    dcs = dcs_sentences(args.dcs_db, DCS_TARGET_N)
    print(f"DCS prose sentences sampled: {len(dcs)}")
    corpora["dcs"] = ("iast", dcs)

    args.outdir.mkdir(parents=True, exist_ok=True)
    matrix_rows = []
    per_corpus = {}
    for cname, (src, units) in corpora.items():
        _, chars, counts = measure(units, src, toks)
        n = len(units)
        # committed per-unit counts
        cols = ["unit_id"] + [f"chars_{s}" for s in SCHEMES_ORDER] + [
            f"tok_{t}_{s}" for t in toks for s in SCHEMES_ORDER
        ]
        with gzip.open(args.outdir / f"{cname}_units_counts.tsv.gz", "wt", encoding="utf-8") as f:
            f.write("\t".join(cols) + "\n")
            for i, (uid, _) in enumerate(units):
                row = [str(uid)] + [str(chars[s][i]) for s in SCHEMES_ORDER] + [
                    str(counts[(t, s)][i]) for t in toks for s in SCHEMES_ORDER
                ]
                f.write("\t".join(row) + "\n")
        ref_chars = chars[REF].mean()
        stats = {}
        for tname in toks:
            ref = counts[(tname, REF)]
            for s in SCHEMES_ORDER:
                c = counts[(tname, s)]
                lo, hi, p = cell_stats(c, ref)
                stats[(tname, s)] = dict(
                    mean_tokens=c.mean(), penalty=c.mean() / ref.mean(),
                    ci_lo=lo, ci_hi=hi, p=p,
                    char_ratio=chars[s].mean() / ref_chars,
                    tpc=(c.mean() / chars[s].mean()) / (ref.mean() / ref_chars),
                )
                matrix_rows.append(
                    [cname, tname, s, n, round(c.mean(), 2),
                     round(stats[(tname, s)]["penalty"], 4), round(lo, 4), round(hi, 4),
                     round(p, 5), round(chars[s].mean(), 1),
                     round(stats[(tname, s)]["char_ratio"], 4),
                     round(stats[(tname, s)]["tpc"], 4)]
                )
        per_corpus[cname] = stats

    hdr = ["corpus", "tokenizer", "scheme", "n_units", "mean_tokens", "penalty_vs_slp1",
           "ci95_lo", "ci95_hi", "perm_p", "mean_chars", "char_ratio", "tpc_ratio"]
    with open(args.outdir / "penalty_matrix.csv", "w", encoding="utf-8", newline="") as f:
        f.write(",".join(hdr) + "\n")
        for r in matrix_rows:
            f.write(",".join(str(x) for x in r) + "\n")

    meta = {
        "date": str(date.today()),
        "mw_source": str(args.mw_src),
        "dcs_source": str(args.dcs_db),
        "dcs_texts": DCS_PROSE_TEXTS,
        "n_mw": len(corpora["mw"][1]),
        "n_dcs": len(corpora["dcs"][1]),
        "vocab": {k: v for k, (v, _) in toks.items()},
        "hf_resolved": getattr(build_tokenizers, "resolved", {}),
        "schemes": SCHEMES_ORDER,
        "reference": REF,
        "bootstrap_B": B_BOOT,
        "permutation_B": B_PERM,
    }
    import json

    (args.outdir / "run_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote", args.outdir)
    print("next: python scripts/token_penalty_report_h6049.py  (renders the report)")


if __name__ == "__main__":
    main()
