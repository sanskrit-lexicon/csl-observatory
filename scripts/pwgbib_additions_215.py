# -*- coding: utf-8 -*-
"""Draft [Cologne Addition] pwgbib_input.txt entries for the 215 true-unknown
ls strings of the Andhrabharati-vs-CDSL pwgbib diff (H5465).

Convention (csl-pywork v02 pwgauth readme + pwgbib_input.txt practice):
  4 tab-delimited fields: id <TAB> code <TAB> display <TAB> tooltip.
  Unknown-referent marks, as already used in the c.* append block:
    'X = ? [Cologne Addition]'          code registered, expansion unknown
    'X = X. ? [Cologne Addition]'       full-title identity, referent unverified
    'X = <expansion> [Cologne Addition]' confident expansion (no '?')
  New ids continue the c.NNN append sequence (max existing c.2179 -> c.2180+).

Inputs:
  CDSL pwgbib_input.txt (csl-pywork v02 pwgauth) — id/code universe
  mw/pwg_ls_vs_cdsl_unknown.tsv     — the 215 true unknowns (field 1)
  mw/pwg_ls_taxonomy_draft.tsv      — draft class per string (field 2)

Outputs (data/pwg_scan_index_tracker/andhrabharati_ls_diff/):
  pwgbib_additions_215.txt        the 215 records, ready to append upstream
  pwgbib_additions_215_audit.tsv  id, ls_string, class_draft, kind, tooltip

Conservative by design (MG: repair first, then classify; H5466 deepens):
expansions are written ONLY where standard (Western series/edition names);
Sanskrit full-title strings get the identity+? precedent form; everything
else stays 'X = ?'.
"""
import csv
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent.parent / "data" / "pwg_scan_index_tracker" / "andhrabharati_ls_diff"
BIB_FILE = Path(r"C:\Users\user\Documents\GitHub\csl-pywork\v02\distinctfiles\pwg\pywork\pwgauth\pwgbib_input.txt")
UNKNOWN_TSV = Path(r"C:\Users\user\Documents\mw\pwg_ls_vs_cdsl_unknown.tsv")
TAXONOMY_TSV = Path(r"C:\Users\user\Documents\mw\pwg_ls_taxonomy_draft.tsv")
OUT_TXT = HERE / "pwgbib_additions_215.txt"
OUT_AUDIT = HERE / "pwgbib_additions_215_audit.tsv"

FIRST_C_ID = 2180  # max existing c-number in pwgbib_input.txt is c.2179
TAG = "[Cologne Addition]"

# Confident expansions: standard names of Western series/editions/journals.
CONFIDENT = {
    "Abh. d. Königl. Ak. d. W. zu Berlin":
        "Abhandlungen der Königlichen Akademie der Wissenschaften zu Berlin",
    "Berichte der phil.-hist. Cl. d. k. s. G. d. Ww.":
        "Berichte der philologisch-historischen Classe der Königlichen Sächsischen Gesellschaft der Wissenschaften",
    "Bibl. indica": "Bibliotheca Indica",
    "Bomb.": "Bombay edition",
    "Bomb. Ausg.": "Bombay edition",
    "Bomb. Ausgg.": "Bombay editions",
    "Calc.": "Calcutta edition",
    "Bull. de lʼAcad. Imp. des Sc.":
        "Bulletin de lʼAcadémie Impériale des Sciences de Saint-Pétersbourg",
    "Bull. de lʼAcad. Imp. des Sc. de S.-P.":
        "Bulletin de lʼAcadémie Impériale des Sciences de Saint-Pétersbourg",
    "Bull. de lʼAcad. Imp. des Sc. de St. P.":
        "Bulletin de lʼAcadémie Impériale des Sciences de Saint-Pétersbourg",
    "Bulletin de lʼAcad. Imp. des sc. de St.-Pét.":
        "Bulletin de lʼAcadémie Impériale des Sciences de Saint-Pétersbourg",
    "Asiatischen Museum der Kais. Akad. d. Wiss. in St. Petersburg":
        "Asiatisches Museum der Kaiserlichen Akademie der Wissenschaften zu St. Petersburg",
    "Zeitschrift für vergl. Sprachf.":
        "Zeitschrift für vergleichende Sprachforschung",
    "BUCHANANʼs Handschrr.": "Francis Buchanan (Hamilton), Sanskrit manuscripts",
    "BUCHANANʼs Hdschrr.": "Francis Buchanan (Hamilton), Sanskrit manuscripts",
}

# Plausible readings — always carry the '?' marker.
GUESS = {
    "Bombay 1783 (1861) lithographirten":
        "Bombay edition, 1783, lithographed reprint 1861",
    "2ten VP.": "second recension of the Vishṇupurāṇa",
    "4te RĀJA-TAR.": "fourth recension of the Rājataraṅgiṇī",
    "CHĀNDOGYABHĀṢYA": "Chāndogya-upaniṣad-bhāṣya",
    "Buddh. Trigl.": "Buddhist triglot edition",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.split())


def display(s: str) -> str:
    """Tooltip-title heuristic, conservative: ALL-CAPS alphabetic tokens of
    >2 letters become Capitalised; shorter caps tokens (VS., UP., W.) and
    any token containing lowercase are copied unchanged."""
    out = []
    for tok in s.split(" "):
        core = tok.rstrip(".")
        letters = [c for c in core if c.isalpha()]
        if letters and sum(c.isupper() for c in letters) == len(letters) and len(letters) > 2:
            res = "".join(ch.upper() if i == 0 else (ch.lower() if ch.isalpha() else ch)
                          for i, ch in enumerate(core))
            out.append(res + tok[len(core):])
        else:
            out.append(tok)
    return " ".join(out)


def main() -> None:
    # --- universe of existing ids/codes ----------------------------------
    existing_ids, existing_codes = set(), set()
    max_c = 0
    for line in BIB_FILE.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            existing_ids.add(parts[0])
            existing_codes.add(norm(parts[1]))
            ident = parts[0]
            if ident.startswith("c."):
                num = ident[2:].rstrip("abcdefgh")
                if num.isdigit():
                    max_c = max(max_c, int(num))
    assert max_c == FIRST_C_ID - 1, f"append block moved: max c.{max_c}, expected c.{FIRST_C_ID - 1}"

    # --- inputs -----------------------------------------------------------
    unknowns = [norm(l.split("\t")[0]) for l in UNKNOWN_TSV.read_text("utf-8").splitlines()[1:] if l.strip()]
    taxonomy = {}
    for l in TAXONOMY_TSV.read_text("utf-8").splitlines()[1:]:
        if l.strip():
            p = l.split("\t")
            taxonomy[norm(p[0])] = p[1] if len(p) > 1 else ""

    assert len(unknowns) == 215, f"expected 215 unknowns, got {len(unknowns)}"
    assert len(set(unknowns)) == 215, "duplicate unknowns"

    # --- draft records ------------------------------------------------------
    records, audit, kinds = [], [], {}
    for i, code in enumerate(unknowns):
        assert code not in existing_codes, f"unknown collides with existing code: {code}"
        cid = f"c.{FIRST_C_ID + i}"
        assert cid not in existing_ids, f"id collision: {cid}"
        cls = taxonomy.get(code, "")

        if code in CONFIDENT:
            kind = "confident-expansion"
            tip = f"{code} = {CONFIDENT[code]} {TAG}"
        elif code in GUESS:
            kind = "guess"
            tip = f"{code} = {GUESS[code]} ? {TAG}"
        elif cls in ("book-work", "commentary-of-work") and "." not in code and code.upper() == code:
            kind = "identity-uncertain"
            tip = f"{code} = {code}. ? {TAG}"
        else:
            kind = "unknown"
            tip = f"{code} = ? {TAG}"
        kinds[kind] = kinds.get(kind, 0) + 1

        rec = f"{cid}\t{code}\t{display(code)}\t{tip}"
        assert rec.count("\t") == 3 and "\n" not in rec
        records.append(rec)
        audit.append({"id": cid, "ls_string": code, "class_draft": cls, "kind": kind, "tooltip": tip})

    OUT_TXT.write_text("\n".join(records) + "\n", "utf-8", newline="")
    with OUT_AUDIT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "ls_string", "class_draft", "kind", "tooltip"], delimiter="\t")
        w.writeheader()
        w.writerows(audit)

    print(f"wrote {len(records)} records -> {OUT_TXT.name}")
    print("tooltip kinds:", dict(sorted(kinds.items(), key=lambda x: -x[1])))
    print(f"id range: c.{FIRST_C_ID}..c.{FIRST_C_ID + len(records) - 1}")


if __name__ == "__main__":
    main()
