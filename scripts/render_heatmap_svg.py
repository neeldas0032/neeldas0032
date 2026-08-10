#!/usr/bin/env python3
"""Render data/contributions.json as an animated violet contribution heatmap SVG.

Self-contained: dark terminal panel, month + weekday labels, legend, footer stats.
Boxes reveal on a diagonal wipe via CSS keyframes (plays once on load, then holds).
Set STATIC=1 to emit a frozen frame (useful for local PNG previews).
"""
import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

# violet ramp: empty -> brightest (matches portfolio #915eff)
PALETTE = ["#0d1a0d", "#0a3a0a", "#0d6b0d", "#1db31d", "#39ff14"]
BG = "#000000"
BORDER = "#003300"
TEXT = "#006600"
ACCENT = "#39ff14"
FG = "#00cc00"

CELL = 12
GAP = 3
LEFT = 34
TOP = 40
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def sunday_index(iso):
    wd = datetime.strptime(iso, "%Y-%m-%d").weekday()  # Mon=0..Sun=6
    return (wd + 1) % 7  # Sun=0..Sat=6


def build():
    data = json.loads(DATA.read_text())
    days = data["days"]

    # assign (col, row) with a Sunday-start calendar
    start_offset = sunday_index(days[0]["date"])
    placed = []
    for i, d in enumerate(days):
        idx = i + start_offset
        placed.append((idx // 7, idx % 7, d))  # col, row, day
    weeks = max(p[0] for p in placed) + 1

    width = LEFT + weeks * (CELL + GAP) + 12
    grid_h = TOP + 7 * (CELL + GAP)
    height = grid_h + 54  # room for legend + footer

    rects = []
    month_labels = []
    seen_month = set()
    max_delay = 0.0
    for col, row, d in placed:
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        color = PALETTE[min(d["level"], 4)]
        delay = (col + row) * 0.012  # diagonal wipe
        max_delay = max(max_delay, delay)
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        cls = "" if STATIC else ' class="cell"'
        rects.append(
            f'<rect{cls} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{color}"{style}><title>{d["date"]}: level {d["level"]}</title></rect>'
        )
        mon = int(d["date"][5:7])
        if row == 0 and mon not in seen_month:
            seen_month.add(mon)
            month_labels.append(
                f'<text x="{x}" y="{TOP-9}" fill="{TEXT}" font-size="10">{MONTHS[mon-1]}</text>'
            )

    # weekday labels (Mon / Wed / Fri)
    wd_labels = []
    for lbl, r in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        wy = TOP + r * (CELL + GAP) + CELL - 2
        wd_labels.append(f'<text x="6" y="{wy}" fill="{TEXT}" font-size="9">{lbl}</text>')

    # legend
    ly = grid_h + 14
    lx = width - 12 - 5 * (CELL + GAP) - 34
    legend = [f'<text x="{lx-30}" y="{ly+CELL-2}" fill="{TEXT}" font-size="10">Less</text>']
    for i, c in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + i*(CELL+GAP)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    legend.append(f'<text x="{lx + 5*(CELL+GAP) + 4}" y="{ly+CELL-2}" fill="{TEXT}" font-size="10">More</text>')

    cur = data["current_streak"]["len"]
    lon = data["longest_streak"]["len"]
    footer = (f'<text x="{LEFT}" y="{grid_h+14+CELL-1}" fill="{FG}" font-size="11">'
              f'<tspan fill="{ACCENT}" font-weight="700">{data["total"]}</tspan> contributions in the last year'
              f'  ·  current streak <tspan fill="{ACCENT}" font-weight="700">{cur}</tspan>'
              f'  ·  longest <tspan fill="{ACCENT}" font-weight="700">{lon}</tspan></text>')

    css = "" if STATIC else f"""
  <style>
    .cell {{ opacity: 0; transform-box: fill-box; animation: pop .45s ease forwards; }}
    @keyframes pop {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  </style>"""

    prompt = f'<text x="{LEFT}" y="20" fill="{TEXT}" font-size="12" font-weight="600"><tspan fill="{ACCENT}">neel@github</tspan> ~ $ ./contributions.sh</text>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">{css}
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  {prompt}
  {''.join(month_labels)}
  {''.join(wd_labels)}
  {''.join(rects)}
  {''.join(legend)}
  {footer}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({width}x{height}, {len(placed)} cells)")


if __name__ == "__main__":
    build()
