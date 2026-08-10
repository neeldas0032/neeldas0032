#!/usr/bin/env python3
"""Render a terminal-style 'ls -la ~/projects/' projects panel SVG.

Edit PROJECTS list below to change content. STATIC=1 for frozen frame.
"""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "projects-card.svg"
STATIC = os.environ.get("STATIC") == "1"

BG     = "#000000"
BORDER = "#003300"
BAR    = "#001100"
NEON   = "#39ff14"
GREEN  = "#00cc00"
DIM    = "#006600"
DIMMER = "#004400"
W      = 860
PAD    = 22
BAR_H  = 30
LINE   = 24
FONT   = 13

PROJECTS = [
    {
        "name":  "CodebaseGPT",
        "url":   "https://codebasegpt.in",
        "tag":   "LIVE",
        "lang":  "Python",
        "desc":  "Chat with any codebase — ask questions, get answers grounded in the actual repo",
        "stack": "FastAPI · LLMs · Vector DB",
    },
    {
        "name":  "PatternPivot",
        "url":   "https://github.com/neeldas0032/patternpivot",
        "tag":   "B.Tech Project",
        "lang":  "Python",
        "desc":  "Few-shot machine-vision quality inspection for MSMEs — defect detection in <15 min from ~10 photos",
        "stack": "PyTorch · FastAPI · React · Three.js",
    },
]

def anim(i, kind="fade"):
    if STATIC:
        return "", ""
    delay = 0.1 + i * 0.12
    cls = f' class="r{i}"'
    st  = ""
    return cls, st

def build():
    rows_svg = []
    # header row
    hdr = (f'<text x="{PAD}" y="{BAR_H+28}" font-size="{FONT}" fill="{DIM}">'
           f'total {len(PROJECTS)}  &nbsp;&nbsp;'
           f'<tspan fill="{DIMMER}">drwxr-xr-x  name                    lang      description</tspan>'
           f'</text>')
    rows_svg.append(hdr)

    y = BAR_H + 28 + LINE + 6
    for i, p in enumerate(PROJECTS):
        tag_color = NEON if p["tag"] == "LIVE" else "#00aaff"
        # permission string for aesthetic
        perm = "-rwxr-xr-x"
        name_pad = p["name"].ljust(22)
        lang_pad = p["lang"].ljust(8)

        cls, _ = anim(i)
        delay = 0.2 + i * 0.18

        # line 1: ls entry
        anim_attr = "" if STATIC else f' style="animation-delay:{delay}s"'
        rows_svg.append(
            f'<g class="proj"{anim_attr}>'
            f'<text x="{PAD}" y="{y}" font-size="{FONT}">'
            f'<tspan fill="{DIMMER}">{perm}  </tspan>'
            f'<tspan fill="{NEON}" font-weight="700">{name_pad}</tspan>'
            f'<tspan fill="{DIM}">{lang_pad}  </tspan>'
            f'<tspan fill="{GREEN}">{p["desc"]}</tspan>'
            f'</text>'
        )
        y += LINE - 4
        # line 2: stack + tag + url
        rows_svg.append(
            f'<text x="{PAD + 148}" y="{y}" font-size="{FONT-1}">'
            f'<tspan fill="{DIMMER}">↳ </tspan>'
            f'<tspan fill="{DIM}">{p["stack"]}  </tspan>'
            f'<tspan fill="{tag_color}" font-weight="700">[{p["tag"]}]</tspan>'
            f'  <tspan fill="{DIMMER}">{p["url"]}</tspan>'
            f'</text>'
            f'</g>'
        )
        y += LINE + 4

    H = y + PAD
    dots = "".join(
        f'<circle cx="{PAD+8+i*16}" cy="{BAR_H/2}" r="5" fill="{c}"/>'
        for i, c in enumerate(["#ff5f56","#ffbd2e","#27c93f"])
    )
    prompt = (f'<text x="{PAD}" y="20" font-size="12" font-weight="600">'
              f'<tspan fill="{NEON}">neel@github</tspan>'
              f'<tspan fill="{DIM}"> ~ $ </tspan>'
              f'<tspan fill="{GREEN}">ls -la ~/projects/</tspan></text>')

    css = "" if STATIC else """
  <style>
    .proj { opacity: 0; animation: fadein .5s ease forwards; }
    @keyframes fadein { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
  </style>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">{css}
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{BAR_H}" rx="10" fill="{BAR}"/>
  <rect x="0.5" y="{BAR_H-10}" width="{W-1}" height="10" fill="{BAR}"/>
  {dots}
  <text x="{W/2}" y="{BAR_H/2+4}" fill="{DIM}" font-size="11" text-anchor="middle">~/projects</text>
  {prompt}
  {''.join(rows_svg)}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{H})")

if __name__ == "__main__":
    build()
