#!/usr/bin/env python3
"""OPTIONAL — turn data/source-prepped.png into a self-typing ASCII portrait SVG.

Replaces neel-ascii.svg (the name banner) with a real portrait once you've run
prep_photo.py. Monochrome + high contrast on purpose: rainbow ASCII reads as noise.

    python scripts/make_ascii_svg.py
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source-prepped.png"
OUT = ROOT / "neel-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cso#%@"   # bright (sparse) -> dark (dense); leading space = blank
COLS = 92                  # character grid width
CHAR_ASPECT = 0.52         # glyph height:width for downsampling

BG = "#0d1117"
BORDER = "#241d3a"
INK = "#a678ff"
CHW = 6.6
LH = 7.4
FONT_SIZE = 8
PAD = 18


def to_rows():
    img = Image.open(SRC).convert("L")
    w, h = img.size
    rows = max(1, int(COLS * (h / w) * CHAR_ASPECT))
    small = img.resize((COLS, rows))
    px = np.asarray(small, dtype=np.float32) / 255.0
    lines = []
    for r in range(rows):
        line = "".join(RAMP[min(len(RAMP) - 1, int((1 - px[r, c]) * (len(RAMP) - 1)))]
                        for c in range(COLS))
        lines.append(line.rstrip())
    return lines


def build():
    lines = to_rows()
    width = int(PAD * 2 + COLS * CHW)
    top = PAD + FONT_SIZE
    height = int(top + len(lines) * LH + PAD)

    rows = []
    for i, ln in enumerate(lines):
        y = top + i * LH
        safe = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if STATIC or not ln:
            rows.append(f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{safe}</text>')
        else:
            cid = f"c{i}"
            begin = f"{0.05 + i*0.03:.2f}s"
            w = int(len(ln) * CHW) + 4
            rows.append(
                f'<clipPath id="{cid}"><rect x="{PAD}" y="{y-FONT_SIZE:.1f}" width="0" height="{LH:.1f}">'
                f'<animate attributeName="width" from="0" to="{w}" dur="0.25s" begin="{begin}" fill="freeze"/>'
                f'</rect></clipPath>'
                f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve" clip-path="url(#{cid})">{safe}</text>'
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <g fill="{INK}" font-size="{FONT_SIZE}" font-weight="500">
  {''.join(rows)}
  </g>
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({width}x{height}) from {len(lines)} rows")


if __name__ == "__main__":
    build()
