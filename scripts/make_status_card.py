#!/usr/bin/env python3
"""Render a 'ps aux'-style status card SVG — what Neel is doing right now.

Edit PROCESSES below. STATIC=1 for frozen frame.
"""
import os
from pathlib import Path
from datetime import datetime

OUT = Path(__file__).resolve().parent.parent / "status-card.svg"
STATIC = os.environ.get("STATIC") == "1"

BG     = "#000000"
BORDER = "#003300"
BAR    = "#001100"
NEON   = "#39ff14"
GREEN  = "#00cc00"
DIM    = "#006600"
DIMMER = "#003300"
CYAN   = "#00ffff"
YELLOW = "#ffff00"
W      = 860
PAD    = 22
BAR_H  = 30
LINE   = 24
FONT   = 13

# (PID, USER, CPU%, MEM%, STATUS, COMMAND)
PROCESSES = [
    ("1001", "neel", "92", "4.2", "RUNNING", "data-engineer-intern @ DevPhoenix Technologies"),
    ("1002", "neel", "88", "3.1", "RUNNING", "btech-cse-aiml @ Brainware University [2023-2027]"),
    ("1003", "neel", "95", "5.8", "RUNNING", "building CodebaseGPT → codebasegpt.in [LIVE]"),
    ("1004", "neel", "75", "2.9", "RUNNING", "vp-tech-club @ Brainware University"),
    ("1005", "neel", "60", "2.1", "RUNNING", "upskilling: Airflow · Spark · dbt · System Design"),
    ("1006", "neel", "45", "1.5", "READY",   "open-to-collaborate on data / ML / AI projects"),
    ("1007", "neel", "30", "1.0", "READY",   "gate-da-2027 prep [IIT MTech goal]"),
]

def build():
    y = BAR_H + 32

    # header
    hdr_cols = f'{"PID":<6}{"USER":<8}{"CPU%":<7}{"MEM%":<7}{"STAT":<10}COMMAND'
    hdr_svg = (f'<text x="{PAD}" y="{y}" font-size="{FONT-1}" fill="{DIM}">{hdr_cols}</text>')
    y += LINE

    rows_svg = []
    for i, (pid, user, cpu, mem, stat, cmd) in enumerate(PROCESSES):
        stat_color = NEON if stat == "RUNNING" else CYAN
        delay = 0.1 + i * 0.10
        anim_attr = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'

        # highlight LIVE in command
        cmd_svg = cmd.replace(
            "[LIVE]",
            f'</tspan><tspan fill="{NEON}" font-weight="700">[LIVE]</tspan><tspan fill="{GREEN}">'
        )

        rows_svg.append(
            f'<g class="pr"{anim_attr}>'
            f'<text x="{PAD}" y="{y}" font-size="{FONT}">'
            f'<tspan fill="{DIMMER}">{pid:<6}</tspan>'
            f'<tspan fill="{DIM}">{user:<8}</tspan>'
            f'<tspan fill="{YELLOW}">{cpu:<7}</tspan>'
            f'<tspan fill="{DIM}">{mem:<7}</tspan>'
            f'<tspan fill="{stat_color}" font-weight="700">{stat:<10}</tspan>'
            f'<tspan fill="{GREEN}">{cmd_svg}</tspan>'
            f'</text></g>'
        )
        y += LINE

    H = y + PAD + 10

    dots = "".join(
        f'<circle cx="{PAD+8+j*16}" cy="{BAR_H/2}" r="5" fill="{c}"/>'
        for j, c in enumerate(["#ff5f56","#ffbd2e","#27c93f"])
    )
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    prompt = (f'<text x="{PAD}" y="20" font-size="12" font-weight="600">'
              f'<tspan fill="{NEON}">neel@github</tspan>'
              f'<tspan fill="{DIM}"> ~ $ </tspan>'
              f'<tspan fill="{GREEN}">ps aux | grep neel</tspan>'
              f'<tspan fill="{DIMMER}">  # {now}</tspan></text>')

    css = "" if STATIC else """
  <style>
    .pr { opacity:0; animation: slide .4s ease forwards; }
    @keyframes slide { from { opacity:0; transform:translateX(-10px); } to { opacity:1; transform:translateX(0); } }
  </style>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace">{css}
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{BAR_H}" rx="10" fill="{BAR}"/>
  <rect x="0.5" y="{BAR_H-10}" width="{W-1}" height="10" fill="{BAR}"/>
  {dots}
  <text x="{W/2}" y="{BAR_H/2+4}" fill="{DIM}" font-size="11" text-anchor="middle">neel: ~ (ps)</text>
  {prompt}
  {hdr_svg}
  {''.join(rows_svg)}
</svg>"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{H})")

if __name__ == "__main__":
    build()
