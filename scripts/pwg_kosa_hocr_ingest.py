#!/usr/bin/env python3
"""Harvest BSB per-page hOCR for the amara_dlc PWG kosa edition, align it to the
campaign's per-page index, and measure a real character error rate against the
committed AMAR e-text (H1720).

H1715 measured that OCR-from-scratch loses to the hOCR the Bayerische
Staatsbibliothek already publishes (reports/pwg_kosa_etext_pilot.md). This script
harvests that hOCR for every page indexed by the amara_dlc campaign
(app1/pywork/index.txt, 374 pages), derives the repo-page -> BSB-page offset
empirically (do not assume it -- it differs from abch2's), and computes CER
against AMAR/amar.txt over a page-depth-stratified sample.

Alignment method for CER: AMAR/amar.txt uses a DIFFERENT verse-numbering scheme
than the index.txt "section/from-v/to-v" columns (verse numbers are continuous
through the front matter into the first varga, then reset per varga; index.txt's
own section boundaries do not visibly line up with AMAR's varga boundaries at the
first checked anchor). Rather than trust a cross-edition verse-number match
literally -- the FINDINGS #480 trap this handoff explicitly warns about, applied
to citation numbers instead of page numbers -- this script aligns each hOCR page
to AMAR by CONTENT: restrict the search to the correct kanda (unambiguous, from
index.txt's "book" column and AMAR's `;k{}` markers), then slide a window across
that kanda's token stream to find the position of highest token overlap with the
page's OCR text. That is the same token-overlap principle
scripts/pwg_kosa_ocr_probe.py used to derive the abch2 offset, applied per-page.

Run:
  python scripts/pwg_kosa_hocr_ingest.py --harvest         # fetch + cache hOCR (idempotent)
  python scripts/pwg_kosa_hocr_ingest.py --cer             # CER over the sampled pages
  python scripts/pwg_kosa_hocr_ingest.py --harvest --cer   # both
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from indic_transliteration import sanscript

REPO_ROOT = Path(__file__).resolve().parent.parent
AMAR_PATH = Path(r"C:\Users\user\Documents\GitHub\AMAR\amar.txt")
INDEX_URL = "https://raw.githubusercontent.com/sanskrit-lexicon-scans/amara_dlc/main/app1/pywork/index.txt"
BSB_ID = "bsb10250868"
BSB_OCR = f"https://api.digitale-sammlungen.de/ocr/{BSB_ID}"
BLOB = "https://github.com/sanskrit-lexicon/csl-observatory/blob/main"

DATA_DIR = REPO_ROOT / "data" / "pwg_kosa_hocr" / "amara_dlc"
RAW_DIR = DATA_DIR / "raw"
TEXT_DIR = DATA_DIR / "text"
INDEX_CACHE = DATA_DIR / "index.txt"
MANIFEST_PATH = DATA_DIR / "manifest.tsv"
CER_OUT = DATA_DIR / "cer_sample.tsv"

DEVA = re.compile(r"[\u0900-\u097F]+")

# Derived empirically 27/28-07-2026 (H1720): token-overlap match at repo page 32
# (index.txt book1/chapter1/section1/v1-4, the first substantive content page)
# peaks at BSB page 29 (overlap 9 vs <=1 for every neighbouring offset -15..+15),
# and independently confirmed at repo page 229 (kanda2 vocab, overlap 44 at BSB
# page 226 vs 15-38 for neighbouring offsets -8..0). Both anchors agree: offset -3.
# NOT copied from abch2 (whose offset is -1) -- see the handoff's explicit warning
# against copying the offset across editions.
PAGE_OFFSET = -3


def fetch_url(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "csl-observatory/H1720 (research harvest; contact via github.com/sanskrit-lexicon)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


# ------------------------------------------------------------------- index.txt

def load_index():
    if not INDEX_CACHE.exists():
        INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_CACHE.write_bytes(fetch_url(INDEX_URL))
    rows = []
    with open(INDEX_CACHE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            page = r.get("page")
            if not page or not page.strip().isdigit():
                continue
            book_raw = (r.get("book") or "").strip()
            book = int(book_raw) if book_raw.isdigit() else None
            rows.append({
                "page": int(page.strip()),
                "book": book,
                "chapter": (r.get("chapter") or "").strip(),
                "section": (r.get("section") or "").strip(),
                "fromv": (r.get("from v.") or r.get("fromv") or "").strip(),
                "tov": (r.get("to v.") or r.get("tov") or "").strip(),
                "ipage": (r.get("ipage") or "").strip(),
                "remark": (r.get("remark(s)") or "").strip(),
            })
    return rows


def distinct_pages(rows):
    seen = []
    seen_set = set()
    for r in rows:
        if r["page"] not in seen_set:
            seen_set.add(r["page"])
            seen.append(r["page"])
    return seen


# ------------------------------------------------------------------------ harvest

def harvest(rows, rate_limit_s=0.4):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    pages = distinct_pages(rows)
    manifest = []
    n_fetched = n_cached = n_error = 0
    for repo_page in pages:
        bsb_page = repo_page + PAGE_OFFSET
        raw_path = RAW_DIR / f"{repo_page:03d}.html"
        text_path = TEXT_DIR / f"{repo_page:03d}.txt"
        status = "ok"
        if raw_path.exists() and text_path.exists():
            n_cached += 1
        else:
            try:
                html = fetch_url(f"{BSB_OCR}/{bsb_page}").decode("utf-8", errors="replace")
                raw_path.write_text(html, encoding="utf-8")
                text_path.write_text(strip_html(html), encoding="utf-8")
                n_fetched += 1
                time.sleep(rate_limit_s)
            except urllib.error.HTTPError as e:
                status = f"http_{e.code}"
                n_error += 1
            except Exception as e:
                status = f"error_{type(e).__name__}"
                n_error += 1
        char_count = text_path.stat().st_size if text_path.exists() else 0
        manifest.append({
            "repo_page": repo_page, "bsb_page": bsb_page, "status": status,
            "chars": char_count,
        })
        if (n_fetched) and n_fetched % 50 == 0:
            print(f"  ...{n_fetched} fetched so far", file=sys.stderr)

    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["repo_page", "bsb_page", "status", "chars"], delimiter="\t")
        w.writeheader()
        w.writerows(manifest)

    print(f"harvest: {len(pages)} indexed pages, offset={PAGE_OFFSET}, "
          f"{n_fetched} fetched, {n_cached} already cached, {n_error} errors")
    return manifest


# --------------------------------------------------------------------- AMAR ref

KANDA_MARKERS = [
    (";k{<s>praTamaM kARqam</s>}", 1),
    (";k{<s>dvitIyaM kARqam</s>}", 2),
    (";k{<s>tftIyaM sAmAnyakARqam</s>}", 3),
]


def load_amar_kandas():
    """Return {book_no: devanagari word list, in reading order} for kanda 1-3."""
    txt = AMAR_PATH.read_text(encoding="utf-8", errors="replace")
    bounds = []
    for marker, book_no in KANDA_MARKERS:
        idx = txt.index(marker)
        bounds.append((idx, book_no))
    bounds.sort()
    kandas = {}
    for i, (start, book_no) in enumerate(bounds):
        end = bounds[i + 1][0] if i + 1 < len(bounds) else len(txt)
        chunk = txt[start:end]
        # drop XML-ish attribute noise (kvvv="...", eid markers) before tokenising
        chunk = re.sub(r'kvvv="[^"]*"', " ", chunk)
        slp1_words = [t for t in re.split(r"[^A-Za-z']+", chunk) if len(t) > 1]
        deva_words = [sanscript.transliterate(t, sanscript.SLP1, sanscript.DEVANAGARI) for t in slp1_words]
        kandas[book_no] = deva_words
    return kandas


# --------------------------------------------------------------------------- CER

def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ca = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ca == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]


def best_window(page_words, kanda_words, step=4):
    """Slide a window the length of page_words across kanda_words; return the
    text of the window with highest token-multiset overlap."""
    n = len(page_words)
    if n == 0 or not kanda_words:
        return "", 0
    page_multiset = {}
    for w in page_words:
        page_multiset[w] = page_multiset.get(w, 0) + 1
    best_score, best_start = -1, 0
    # running window counts
    window = kanda_words[:n]
    counts = {}
    for w in window:
        counts[w] = counts.get(w, 0) + 1

    def score(counts):
        return sum(min(c, page_multiset.get(w, 0)) for w, c in counts.items())

    best_score = score(counts)
    best_start = 0
    i = 0
    N = len(kanda_words)
    while i + step + n <= N:
        for _ in range(step):
            out_w = kanda_words[i]
            counts[out_w] -= 1
            if counts[out_w] == 0:
                del counts[out_w]
            i += 1
            in_w = kanda_words[i + n - 1]
            counts[in_w] = counts.get(in_w, 0) + 1
        s = score(counts)
        if s > best_score:
            best_score, best_start = s, i
    return " ".join(kanda_words[best_start:best_start + n]), best_score


def normalize_for_cer(text: str) -> str:
    words = DEVA.findall(text)
    return " ".join(words)


def compute_cer(rows):
    kandas = load_amar_kandas()
    pages = distinct_pages(rows)
    page_book = {}
    for r in rows:
        page_book.setdefault(r["page"], r["book"])
    n = len(pages)
    # stratified sample: ~4 evenly-spaced pages per decile of page-depth order -> >=30 pages
    deciles = 10
    sample_idx = set()
    for d in range(deciles):
        lo = d * n // deciles
        hi = max(lo + 1, (d + 1) * n // deciles)
        span = list(range(lo, hi))
        picks = span if len(span) <= 4 else [span[k * (len(span) - 1) // 3] for k in range(4)]
        sample_idx.update(picks)
    sample_idx = sorted(sample_idx)

    results = []
    for idx in sample_idx:
        repo_page = pages[idx]
        book = page_book.get(repo_page)
        text_path = TEXT_DIR / f"{repo_page:03d}.txt"
        if book not in kandas or not text_path.exists():
            continue
        ocr_text = text_path.read_text(encoding="utf-8", errors="replace")
        page_words = DEVA.findall(ocr_text)
        if len(page_words) < 5:
            continue
        ref_text, overlap_score = best_window(page_words, kandas[book])
        hyp_norm = normalize_for_cer(ocr_text)
        ref_norm = ref_text
        if not ref_norm:
            continue
        dist = levenshtein(hyp_norm, ref_norm)
        cer = dist / max(1, len(ref_norm))
        decile = idx * deciles // n + 1
        results.append({
            "repo_page": repo_page, "book": book, "decile": decile,
            "n_hyp_chars": len(hyp_norm), "n_ref_chars": len(ref_norm),
            "overlap_score": overlap_score, "edit_distance": dist,
            "cer": round(cer, 4),
        })
        print(f"page {repo_page:>3} (decile {decile:>2}, book {book}): "
              f"CER={cer:.3f}  hyp_chars={len(hyp_norm)} ref_chars={len(ref_norm)} "
              f"overlap={overlap_score}")

    with open(CER_OUT, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["repo_page", "book", "decile", "n_hyp_chars", "n_ref_chars",
                      "overlap_score", "edit_distance", "cer"]
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        w.writerows(results)

    if results:
        overall = sum(r["cer"] for r in results) / len(results)
        print(f"\n{len(results)} pages sampled. mean CER (unweighted) = {overall:.3f}")
        by_decile = {}
        for r in results:
            by_decile.setdefault(r["decile"], []).append(r["cer"])
        print("per-decile mean CER:")
        for d in sorted(by_decile):
            vals = by_decile[d]
            print(f"  decile {d:>2}: n={len(vals):>2}  mean CER={sum(vals)/len(vals):.3f}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", action="store_true")
    ap.add_argument("--cer", action="store_true")
    ap.add_argument("--rate-limit", type=float, default=0.4)
    args = ap.parse_args()

    rows = load_index()
    print(f"index.txt: {len(rows)} rows, {len(distinct_pages(rows))} distinct pages")

    if args.harvest:
        harvest(rows, rate_limit_s=args.rate_limit)
    if args.cer:
        compute_cer(rows)
    if not args.harvest and not args.cer:
        print("nothing to do -- pass --harvest and/or --cer", file=sys.stderr)


if __name__ == "__main__":
    main()
