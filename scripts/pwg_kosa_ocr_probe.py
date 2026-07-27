#!/usr/bin/env python3
"""PWG kośa e-text pilot — is OCR-from-scratch the right job? (H1715)

The [H1706 e-text queue](../data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv)
ranks the two heaviest PWG kośa scan sets at the top: `amara_dlc` (Amarakoṣa, Deslongchamps
1839) and `abch2` (Hemacandra's Abhidhānacintāmaṇi, Böhtlingk & Rieu 1847). H1715 proposed
OCR-ing them with tesseract 5 `san`, anchored to the campaign's committed per-page index.

This script is the measurement that answers whether that is the right method. It runs two
engines over the SAME pages and scores both with the SAME metric:

  A. tesseract 5 `san`, locally, on the scan repo's own page PDFs.
  B. the per-page hOCR the Bayerische Staatsbibliothek ALREADY publishes for both editions,
     reachable from the IIIF manifest's `seeAlso` (word-level bounding boxes included).

METRIC — valid-token rate, not CER. The share of extracted Devanagari tokens that are real
Sanskrit words, checked against the vocabulary of the *same work* already digitized in
csl-orig (`abch` + `acph` + `acsj`, Nirṇaya-sāgara 1896) plus the MW headword inventory.

Why not a character error rate: a CER needs hand-transcribed ground truth, and 1839/1847
Devanagari with archaic orthography is material this author cannot transcribe reliably
enough to serve as truth. The valid-token rate needs no transcription, and a control run
puts the reference text itself through the identical tokenizer so that method loss is
visible and separable.

READ THE NUMBER HONESTLY. The reference is a DIFFERENT edition of the same work, so a miss
is not automatically an OCR error — edition variants, sandhi splits and 1847 orthography
all produce legitimate misses. The absolute level is therefore a conservative floor. The
COMPARISON is nonetheless sound, because both engines are scored against the identical
reference with the identical tokenizer.

Run:  python scripts/pwg_kosa_ocr_probe.py                 # cached, offline after first run
      python scripts/pwg_kosa_ocr_probe.py --sweep         # also sweep dpi x psm x preprocessing
      python scripts/pwg_kosa_ocr_probe.py --cache <dir>   # where page PDFs + hOCR are kept
"""

import argparse
import csv
import re
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CSL_ORIG = Path(r"C:\Users\user\Documents\GitHub\csl-orig\v02")
SCANS_RAW = "https://raw.githubusercontent.com/sanskrit-lexicon-scans"
BSB_OCR = "https://api.digitale-sammlungen.de/ocr"

# Böhtlingk & Rieu 1847 Abhidhānacintāmaṇi. The repo page number and the BSB sequence
# number differ by a constant; the offset is established empirically below, not assumed.
WORK = {
    "repo": "abch2",
    "bsb_id": "bsb10250953",
    "pages": ["060", "090", "110", "140", "170", "200", "230", "260", "290", "320", "350", "380"],
}

DEVA = re.compile(r"[\u0900-\u097F]+")
REPO_BLOB = "https://github.com/sanskrit-lexicon/csl-observatory/blob/main"


# ------------------------------------------------------------------ reference vocabulary

def build_reference_vocab():
    """SLP1 token vocabulary from the already-digitized Abhidhānacintāmaṇi + MW headwords."""
    vocab = set()
    for code in ("abch", "acph", "acsj"):
        p = CSL_ORIG / code / f"{code}.txt"
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"<s>(.*?)</s>", txt, re.S):
            vocab.update(t for t in re.split(r"[^A-Za-z]+", m.group(1)) if len(t) > 1)
        for line in txt.splitlines():
            if line[:4] in ("<L>x", "<k1>", "<k2>") or line.startswith("<L>"):
                vocab.update(t for t in re.split(r"[^A-Za-z]+", line) if len(t) > 1)
    mw = CSL_ORIG / "mw" / "mw.txt"
    if mw.exists():
        for line in mw.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("<k1>") or line.startswith("<k2>"):
                vocab.update(t for t in re.split(r"[^A-Za-z]+", line) if len(t) > 1)
    return vocab


def slp1(tokens):
    from indic_transliteration import sanscript
    return [sanscript.transliterate(t, sanscript.DEVANAGARI, sanscript.SLP1) for t in tokens]


def score(text, vocab):
    toks = slp1([t for t in DEVA.findall(text) if len(t) > 1])
    return sum(1 for t in toks if t in vocab), len(toks)


# ------------------------------------------------------------------------------- engines

def fetch(url, dest: Path):
    if dest.exists() and dest.stat().st_size:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())
    return dest


def tesseract_page(pdf: Path, cache: Path, dpi=300, psm="6", top=0.04, bot=0.60):
    """OCR the Devanagari block of one page image. Returns raw text."""
    import fitz
    d = fitz.open(pdf)
    pg = d[0]
    r = pg.rect
    clip = fitz.Rect(r.x0, r.y0 + r.height * top, r.x1, r.y0 + r.height * bot)
    png = cache / f"{pdf.stem}_{dpi}_{psm}.png"
    pg.get_pixmap(dpi=dpi, clip=clip).save(png)
    out = subprocess.run(["tesseract", str(png), "stdout", "-l", "san", "--psm", psm],
                         capture_output=True, encoding="utf-8", errors="replace")
    return out.stdout or ""


def bsb_hocr(bsb_id, page_no, cache: Path):
    """The hOCR the library already publishes for that page. Returns plain text."""
    dest = cache / f"hocr_{bsb_id}_{page_no}.html"
    try:
        fetch(f"{BSB_OCR}/{bsb_id}/{page_no}", dest)
    except Exception as exc:
        return "", f"{type(exc).__name__}"
    s = dest.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip(), ""


def page_pdf(repo, page, cache: Path):
    return fetch(f"{SCANS_RAW}/{repo}/main/pdfpages/{repo}-{page}.pdf",
                 cache / f"{repo}-{page}.pdf")


def has_text_layer(pdf: Path):
    """§470/§480: test the SCRIPT of the extracted text, not merely its length."""
    import fitz
    pg = fitz.open(pdf)[0]
    txt = pg.get_text()
    return len(txt.strip()), bool(DEVA.search(txt)), len(pg.get_images(full=True))


# ---------------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None, help="where page PDFs and hOCR are kept")
    ap.add_argument("--sweep", action="store_true", help="also sweep dpi x psm x preprocessing")
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()

    outdir = Path(args.outdir)
    cache = Path(args.cache) if args.cache else outdir / ".ocr_cache"
    cache.mkdir(parents=True, exist_ok=True)

    vocab = build_reference_vocab()
    if not vocab:
        print(f"BLOCKED: no reference vocabulary; is csl-orig at {CSL_ORIG}?", file=sys.stderr)
        sys.exit(1)
    print(f"reference vocabulary: {len(vocab):,} distinct SLP1 tokens "
          f"(csl-orig abch + acph + acsj + MW headwords)")

    # Control: the reference text through the identical tokenizer. Below 100% here would
    # be method loss, and would have to be subtracted from both engines alike.
    from indic_transliteration import sanscript
    ctrl_src = (CSL_ORIG / "abch" / "abch.txt").read_text(encoding="utf-8", errors="replace")
    ctrl_tokens = []
    for seg in re.findall(r"<s>(.*?)</s>", ctrl_src, re.S)[:400]:
        for t in re.split(r"[^A-Za-z]+", seg):
            if len(t) > 1:
                ctrl_tokens.append(sanscript.transliterate(t, sanscript.SLP1, sanscript.DEVANAGARI))
    c_hit, c_tot = score(" ".join(ctrl_tokens), vocab)
    print(f"control (reference text, same tokenizer): {c_hit}/{c_tot} = "
          f"{100*c_hit/c_tot:.1f}%\n")

    repo, bsb_id, pages = WORK["repo"], WORK["bsb_id"], WORK["pages"]

    # Does a text layer exist at all? Sample first -- if it does, none of the rest matters.
    probe_pdf = page_pdf(repo, pages[0], cache)
    n_chars, has_deva, n_imgs = has_text_layer(probe_pdf)
    print(f"text-layer probe on {probe_pdf.name}: {n_chars} chars, "
          f"devanagari={has_deva}, embedded images={n_imgs}")
    if n_chars and has_deva:
        print("  -> a usable text layer EXISTS; OCR is not required. Stopping.")
        return

    # Establish the repo-page -> BSB-page offset empirically.
    probe_tokens = set(slp1([t for t in DEVA.findall(
        tesseract_page(probe_pdf, cache)) if len(t) > 1]))
    best = (0, -1)
    for off in range(-3, 4):
        txt, _ = bsb_hocr(bsb_id, int(pages[0]) + off, cache)
        if not txt:
            continue
        ov = len(probe_tokens & set(slp1([t for t in DEVA.findall(txt) if len(t) > 1])))
        if ov > best[0]:
            best = (ov, off)
    offset = best[1]
    print(f"repo->BSB page offset: {offset:+d} (token overlap {best[0]})\n")

    rows = []
    print(f"{'repo page':<13}{'BSB':>5} | {'tess tok':>9}{'ok':>5}{'rate':>8} | "
          f"{'BSB tok':>8}{'ok':>5}{'rate':>8}")
    print("-" * 68)
    tt = th = bt = bh = 0
    for p in pages:
        pdf = page_pdf(repo, p, cache)
        t_hit, t_tot = score(tesseract_page(pdf, cache), vocab)
        btxt, err = bsb_hocr(bsb_id, int(p) + offset, cache)
        b_hit, b_tot = score(btxt, vocab) if btxt else (0, 0)
        tt += t_tot; th += t_hit; bt += b_tot; bh += b_hit
        t_r = 100 * t_hit / t_tot if t_tot else 0
        b_r = 100 * b_hit / b_tot if b_tot else 0
        rows.append({"repo_page": f"{repo}-{p}", "bsb_page": int(p) + offset,
                     "tesseract_tokens": t_tot, "tesseract_valid": t_hit,
                     "tesseract_rate_pct": round(t_r, 1),
                     "bsb_hocr_tokens": b_tot, "bsb_hocr_valid": b_hit,
                     "bsb_hocr_rate_pct": round(b_r, 1), "error": err})
        print(f"{repo}-{p:<7}{int(p)+offset:>5} | {t_tot:>9}{t_hit:>5}{t_r:>7.1f}% | "
              f"{b_tot:>8}{b_hit:>5}{b_r:>7.1f}%")
    print("-" * 68)
    T = 100 * th / tt if tt else 0
    B = 100 * bh / bt if bt else 0
    print(f"{'TOTAL':<13}{'':>5} | {tt:>9}{th:>5}{T:>7.1f}% | {bt:>8}{bh:>5}{B:>7.1f}%")
    print(f"\nBSB hOCR is {B/T:.1f}x the local tesseract rate over {len(pages)} pages, "
          f"and recovers {bt/tt:.2f}x as many tokens.")

    out = outdir / "data" / "pwg_scan_index_tracker" / "kosa_ocr_pilot.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        fh.write(f"# TOTAL\t\t{tt}\t{th}\t{round(T,1)}\t{bt}\t{bh}\t{round(B,1)}\t\n")
        fh.write(f"# measured {date.today().isoformat()}; reference vocab {len(vocab)} "
                 f"SLP1 tokens; control {round(100*c_hit/c_tot,1)}%\n")
    print(f"\nWrote {out}")

    if args.sweep:
        print("\nparameter sweep on 3 pages (is the low rate the material or the settings?)")
        for psm in ("6", "4", "11"):
            for dpi in (300, 400):
                h = t = 0
                for p in pages[:3]:
                    a, b = score(tesseract_page(page_pdf(repo, p, cache), cache,
                                                dpi=dpi, psm=psm), vocab)
                    h += a; t += b
                print(f"  psm={psm} dpi={dpi}: {h}/{t} = {100*h/t if t else 0:.1f}%")


if __name__ == "__main__":
    main()
