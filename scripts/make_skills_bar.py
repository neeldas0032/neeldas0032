#!/usr/bin/env python3
"""Render rect-based skill bar panel SVG (hacker green, two-column layout).
STATIC=1 for frozen frame.
"""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "skills-bar.svg"
STATIC = os.environ.get("STATIC") == "1"

BG     = "#000000"
BORDER = "#003300"
BARCLR = "#001100"
NEON   = "#39ff14"
GREEN  = "#00cc00"
DIM    = "#006600"
DIMMER = "#002800"
W      = 860
PAD    = 22
BAR_H  = 30
LINE   = 26
FONT   = 13
BARPX  = 170  # progress bar pixel width
BARHT  = 9

SKILLS = [
    ("Data Engineering", [
        ("Python",          88),
        ("SQL",             85),
        ("Apache Airflow",  65),
        ("Apache Spark",    60),
        ("dbt",             55),
    ]),
    ("Analytics & Viz", [
        ("Pandas / NumPy",  90),
        ("Tableau",         75),
        ("Power BI",        65),
        ("Matplotlib",      70),
    ]),
    ("Machine Learning", [
        ("PyTorch",         70),
        ("scikit-learn",    75),
        ("FastAPI",         72),
        ("Computer Vision", 60),
    ]),
]

def bar_svg(bx, y, pct):
    filled = int(BARPX * pct / 100)
    return (
        f'<rect x="{bx}" y="{y-BARHT}" width="{BARPX}" height="{BARHT}" rx="2" fill="{DIMMER}"/>'
        f'<rect x="{bx}" y="{y-BARHT}" width="{filled}" height="{BARHT}" rx="2" fill="{NEON}"/>'
        f'<text x="{bx+BARPX+6}" y="{y}" font-size="11" fill="{DIM}">{pct}%</text>'
    )

def render_col(cats, x_off):
    parts = []
    y = BAR_H + 38
    bx = x_off + 155
    for cat, skills in cats:
        parts.append(
            f'<text x="{x_off}" y="{y}" font-size="{FONT-1}" fill="{DIM}" font-weight="700"># {cat}</text>'
        )
        y += LINE - 2
        for i, (skill, pct) in enumerate(skills):
            delay = 0.15 + i * 0.09
            anim_attr = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
            parts.append(
                f'<g class="sk"{anim_attr}>'
                f'<text x="{x_off}" y="{y}" font-size="{FONT}" fill="{GREEN}">{skill}</text>'
                + bar_svg(bx, y, pct) +
                f'</g>'
            )
            y += LINE
        y += 10
    return parts, y

def build():
    left_parts,  left_h  = render_col(SKILLS[:2], PAD)
    right_parts, right_h = render_col(SKILLS[2:], PAD + W//2)
    H = max(left_h, right_h) + PAD

    div_x = W // 2
    divider = (f'<line x1="{div_x}" y1="{BAR_H+10}" x2="{div_x}" y2="{H-PAD}" '
               f'stroke="{DIMMER}" stroke-width="1" stroke-dasharray="4,4"/>')

    dots = "".join(
        f'<circle cx="{PAD+8+j*16}" cy="{BAR_H/2}" r="5" fill="{c}"/>'
        for j, c in enumerate(["#ff5f56","#ffbd2e","#27c93f"])
    )
    prompt = (f'<text x="{PAD}" y="20" font-size="12" font-weight="600">'
              f'<tspan fill="{NEON}">neel@github</tspan>'
              f'<tspan fill="{DIM}"> ~ $ </tspan>'
              f'<tspan fill="{GREEN}">cat skills.txt</tspan></text>')

    css = "" if STATIC else """
  <style>
    .sk { opacity:0; animation: grow .45s ease forwards; }
    @keyframes grow { from { opacity:0; } to { opacity:1; } }
  </style>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">{css}
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{BAR_H}" rx="10" fill="{BARCLR}"/>
  <rect x="0.5" y="{BAR_H-10}" width="{W-1}" height="10" fill="{BARCLR}"/>
  {dots}
  <text x="{W/2}" y="{BAR_H/2+4}" fill="{DIM}" font-size="11" text-anchor="middle">~/skills</text>
  {prompt}
  {divider}
  {''.join(left_parts)}
  {''.join(right_parts)}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{H})")

if __name__ == "__main__":
    build()
