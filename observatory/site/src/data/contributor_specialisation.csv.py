#!/usr/bin/env python3
"""Observable Framework data loader: pass-through copy of the canonical
data/contributor_specialisation.csv (read-only) for the /org-shape page."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[4]
sys.stdout.write((ROOT / 'data' / 'contributor_specialisation.csv').read_text(encoding='utf-8'))
