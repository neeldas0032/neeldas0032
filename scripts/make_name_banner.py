#!/usr/bin/env python3
"""Render an ASCII-art name banner as a self-typing SVG (violet terminal panel).

Uses pyfiglet so no photo is needed — this is the default left panel.
Swap to a real ASCII portrait later with make_ascii_svg.py.
STATIC=1 emits a frozen frame for previews.
"""
import os
from pathlib import Path

import pyfiglet

OUT = Path(__file__).resolve().parent.parent / "neel-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

TEXT = "NEEL"
SUBTITLE = "> data engineer / analyst / scientist"
FONT = "standard"   # try: "slant", "big", "ansi_shadow"

BG = "#000000"
BORDER = "#003300"
INK = "#39ff14"
DIM = "#006600"
CURSOR = "#00ff00"

CHW = 11.2     # generous monospace char width (avoids right-edge clipping)
LH = 21        # line height
PAD = 22
FONT_SIZE = 18


def build():
    art = pyfiglet.figlet_format(TEXT, font=FONT).rstrip("\n")
    lines = art.split("\n")
    # trim fully-blank trailing/leading lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    maxlen = max(len(ln) for ln in lines)

    width = int(PAD * 2 + maxlen * CHW + 8)
    top = PAD + FONT_SIZE
    height = int(top + len(lines) * LH + 40)

    rows = []
    for i, ln in enumerate(lines):
        y = top + i * LH
        safe = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if STATIC:
            rows.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">{safe}</text>')
        else:
            # per-line left-to-right wipe via a clip rect animated with SMIL
            clip_id = f"clip{i}"
            begin = f"{0.12 + i*0.16:.2f}s"
            w = int(len(ln) * CHW) + 4
            rows.append(
                f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{y-FONT_SIZE}" width="0" height="{LH}">'
                f'<animate attributeName="width" from="0" to="{w}" dur="0.5s" begin="{begin}" fill="freeze"/>'
                f'</rect></clipPath>'
                f'<text x="{PAD}" y="{y}" xml:space="preserve" clip-path="url(#{clip_id})">{safe}</text>'
            )

    sub_y = top + len(lines) * LH + 20
    cursor = ""
    if not STATIC:
        cursor = (f'<rect x="{PAD + len(SUBTITLE)*7.4 + 4:.0f}" y="{sub_y-11}" width="8" height="14" fill="{CURSOR}">'
                  f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <g fill="{INK}" font-size="{FONT_SIZE}" font-weight="700">
  {''.join(rows)}
  </g>
  <text x="{PAD}" y="{sub_y}" fill="{DIM}" font-size="13">{SUBTITLE}</text>
  {cursor}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({width}x{height}, font={FONT})")


if __name__ == "__main__":
    build()
