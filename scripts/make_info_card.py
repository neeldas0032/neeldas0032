#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG (violet terminal theme).

Rows fade + slide in on a stagger. STATIC=1 emits a frozen frame for previews.
Edit ROWS below to change the content.
"""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

BG = "#000000"
BORDER = "#003300"
BAR = "#001100"
KEY = "#39ff14"
VAL = "#00cc00"
DIM = "#006600"
ACCENT = "#39ff14"

TITLE = "neel@github"
ROWS = [
    ("Role",   "Data Engineer · Data Analyst · Data Scientist"),
    ("Now",    "Data Engineer Intern @ DevPhoenix Technologies"),
    ("Edu",    "B.Tech CSE (AI/ML) @ Brainware University"),
    ("Club",   "Vice President, Tech Club"),
    ("Live",   "CodebaseGPT — codebasegpt.in"),
    ("Stack",  "Python · SQL · PyTorch · FastAPI · Airflow"),
    ("Focus",  "pipelines -> insight -> models"),
    ("Loc",    "Kolkata, India"),
]
# neofetch color blocks (two rows of 8) in a violet-leaning palette
BLOCKS = ["#001100", "#002200", "#003300", "#006600",
          "#009900", "#00cc00", "#00ff00", "#39ff14"]

W = 520
PAD = 18
BAR_H = 30
LINE = 26
START_Y = BAR_H + 34
H = START_Y + len(ROWS) * LINE + 46


def anim(i):
    if STATIC:
        return "", ""
    delay = 0.15 + i * 0.09
    return ' class="row"', f' style="animation-delay:{delay:.2f}s"'


def build():
    dots = "".join(
        f'<circle cx="{PAD+8+i*16}" cy="{BAR_H/2}" r="5" fill="{c}"/>'
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"])
    )
    prompt_cls, prompt_st = anim(0)
    parts = [
        f'<g{prompt_cls}{prompt_st}><text x="{PAD}" y="{START_Y}" font-size="12.5">'
        f'<tspan fill="{ACCENT}" font-weight="700">{TITLE}</tspan>'
        f'<tspan fill="{DIM}"> ~ $ </tspan>'
        f'<tspan fill="{VAL}">neofetch</tspan></text></g>'
    ]
    y = START_Y + LINE + 2
    for i, (k, v) in enumerate(ROWS):
        cls, st = anim(i + 1)
        parts.append(
            f'<g{cls}{st}><text x="{PAD}" y="{y}" font-size="12.5">'
            f'<tspan fill="{KEY}" font-weight="700">{k:<6}</tspan>'
            f'<tspan fill="{DIM}"> : </tspan>'
            f'<tspan fill="{VAL}">{v}</tspan></text></g>'
        )
        y += LINE

    # color blocks
    by = y + 6
    blocks = []
    for i, c in enumerate(BLOCKS):
        blocks.append(f'<rect x="{PAD + i*16}" y="{by}" width="13" height="13" rx="2" fill="{c}"/>')
    bcls, bst = anim(len(ROWS) + 1)
    blocks_g = f'<g{bcls}{bst}>{"".join(blocks)}</g>'

    css = "" if STATIC else """
  <style>
    .row { opacity: 0; animation: slide .5s ease forwards; }
    @keyframes slide { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
  </style>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">{css}
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{BAR_H}" rx="10" fill="{BAR}"/>
  <rect x="0.5" y="{BAR_H-10}" width="{W-1}" height="10" fill="{BAR}"/>
  {dots}
  <text x="{W/2}" y="{BAR_H/2+4}" fill="{DIM}" font-size="11" text-anchor="middle">{TITLE}: ~</text>
  {''.join(parts)}
  {blocks_g}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    build()
