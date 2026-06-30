#!/usr/bin/env python3
"""Generate the 1200x630 Open Graph / Twitter social card for the CSL Observatory.

Output: src/observatory-card.png (committed; referenced as og:image/twitter:image
in observablehq.config.js). Re-run if the tagline or branding changes.

    python scripts/make_social_card.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

W, H = 1200, 630
BG_TOP = (30, 47, 64)        # deep slate
BG_BOTTOM = (58, 95, 125)    # #3a5f7d theme-color
INK = (244, 247, 250)
MUTED = (181, 197, 212)
ACCENT = (122, 178, 219)

FONTS = Path("C:/Windows/Fonts")
title_font = ImageFont.truetype(str(FONTS / "georgiab.ttf"), 92)
tag_font = ImageFont.truetype(str(FONTS / "georgia.ttf"), 40)
foot_font = ImageFont.truetype(str(FONTS / "arial.ttf"), 28)
url_font = ImageFont.truetype(str(FONTS / "arial.ttf"), 26)

img = Image.new("RGB", (W, H), BG_TOP)
draw = ImageDraw.Draw(img)

# Vertical gradient background.
for y in range(H):
    t = y / (H - 1)
    r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Accent rule, top-left.
draw.rectangle([80, 150, 84, 480], fill=ACCENT)

x = 130
draw.text((x, 150), "CSL Observatory", font=title_font, fill=INK)
draw.text((x, 280), "13 years of the Cologne Digital", font=tag_font, fill=MUTED)
draw.text((x, 332), "Sanskrit Lexicon, measured", font=tag_font, fill=MUTED)

draw.text((x, 430),
          "repository health  ·  sustainability  ·  issue taxonomy  ·  correction metrics",
          font=foot_font, fill=ACCENT)

url = "sanskrit-lexicon.github.io/csl-observatory"
draw.text((x, H - 70), url, font=url_font, fill=MUTED)

out = Path(__file__).resolve().parent.parent / "src" / "observatory-card.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes, {W}x{H})")
