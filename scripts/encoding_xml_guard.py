"""Encoding/XML hygiene guard for dictionary-source change paths (RH5).

Checks a set of files for four hygiene rules the org's dictionary pipeline
depends on ([`../CLAUDE.md`](../CLAUDE.md) "Encoding — BOM is inconsistent,
check before editing" + `SANSKRIT_CONTEXT_PRIMER.md`):

  1. no-bom       -- file does not start with a UTF-8 BOM (EF BB BF), unless
                     explicitly allowlisted (some exports legitimately carry one).
  2. utf8         -- file decodes as UTF-8 without error.
  3. nfc          -- decoded text is already Unicode NFC-normalized (a file
                     that round-trips through NFC unchanged).
  4. xml-parse    -- for `.xml` files only: `xml.etree.ElementTree` can parse it.

This is the "owning tooling repo" pilot named by RH5's acceptance clause (CI
template exists and is piloted on csl-orig OR the owning tooling repo) --
piloted here in csl-observatory rather than csl-orig, per the org rule that
agents never commit to csl-orig directly. The GitHub Actions template for
fanning this out to other repos' dictionary-source change paths is
[`../runbook/templates/encoding-xml-guard.yml`](../runbook/templates/encoding-xml-guard.yml).

Subcommands:
  check <path> [<path> ...]   check each given file; prints one PASS/FAIL line
                               per file per rule that fired, and a final
                               'violations: N' line (CI-friendly, same
                               contract as dict_runbook.py / tooling_runbook.py).
  self-test                   run the guard against runbook/fixtures/encoding_guard/
                               (bundled good + bad fixtures) and assert the bad
                               ones are all caught and the good ones all pass.
"""
import argparse
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BOM = b"\xef\xbb\xbf"

# Files legitimately allowed to carry a BOM (see CLAUDE.md's "BOM is
# inconsistent" note -- some HeadwordLists exports have one, some don't, and
# stripping it silently is explicitly banned). Empty by default in this repo;
# a deploying repo overrides this via --allow-bom.
DEFAULT_BOM_ALLOWLIST = frozenset()


def check_file(path, allow_bom=DEFAULT_BOM_ALLOWLIST):
    """Return a list of (rule, message) violations for one file. Empty = clean."""
    violations = []
    raw = path.read_bytes()

    has_bom = raw.startswith(BOM)
    if has_bom and str(path) not in allow_bom and path.name not in allow_bom:
        violations.append(("no-bom", f"{path}: starts with a UTF-8 BOM"))

    body = raw[len(BOM):] if has_bom else raw
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as e:
        violations.append(("utf8", f"{path}: not valid UTF-8 ({e})"))
        return violations  # NFC/XML checks need decoded text; nothing further to check

    if unicodedata.normalize("NFC", text) != text:
        violations.append(("nfc", f"{path}: not NFC-normalized"))

    if path.suffix.lower() == ".xml":
        try:
            ET.fromstring(raw)
        except ET.ParseError as e:
            violations.append(("xml-parse", f"{path}: XML did not parse ({e})"))

    return violations


def cmd_check(args):
    total = 0
    for p in args.paths:
        path = Path(p)
        if not path.is_file():
            print(f"::error::{path}: not a file")
            total += 1
            continue
        for rule, msg in check_file(path, allow_bom=frozenset(args.allow_bom)):
            print(f"FAIL [{rule}] {msg}")
            total += 1
    if total == 0:
        print(f"encoding-xml-guard clean: {len(args.paths)} file(s) checked, 0 violations")
    print(f"violations: {total}")
    return 0 if total == 0 else 1


def cmd_self_test(args):
    fixtures = Path(__file__).resolve().parent.parent / "runbook" / "fixtures" / "encoding_guard"
    good_dir, bad_dir = fixtures / "good", fixtures / "bad"
    if not good_dir.is_dir() or not bad_dir.is_dir():
        print(f"::error::fixtures not found under {fixtures}")
        return 2

    failures = []
    for p in sorted(good_dir.glob("*")):
        v = check_file(p)
        if v:
            failures.append(f"expected clean, got violations: {p} -> {v}")

    for p in sorted(bad_dir.glob("*")):
        v = check_file(p)
        if not v:
            failures.append(f"expected a violation, got none: {p}")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        print(f"self-test violations: {len(failures)}")
        return 1

    print(f"self-test clean: {len(list(good_dir.glob('*')))} good + "
          f"{len(list(bad_dir.glob('*')))} bad fixture(s) behaved as expected")
    print("violations: 0")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="check given file(s)")
    p_check.add_argument("paths", nargs="+")
    p_check.add_argument("--allow-bom", action="append", default=[],
                          help="path or filename allowed to carry a BOM (repeatable)")
    p_check.set_defaults(func=cmd_check)

    p_self = sub.add_parser("self-test", help="run against bundled fixtures")
    p_self.set_defaults(func=cmd_self_test)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
