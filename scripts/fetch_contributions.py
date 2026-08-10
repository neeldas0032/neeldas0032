#!/usr/bin/env python3
"""Scrape the public GitHub contribution calendar into data/contributions.json.

No API token required: GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions
"""
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

import requests

USERNAME = "neeldas0032"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-art)"}, timeout=30)
    r.raise_for_status()
    return r.text


def parse(html: str):
    # Each day is a <td ... data-date="YYYY-MM-DD" data-level="0-4" ...>
    cells = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html)
    if not cells:
        # markup order can vary; try the reverse attribute order too
        cells = re.findall(r'data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)
        cells = [(d, lvl) for lvl, d in cells]
    days = [{"date": d, "level": int(lvl)} for d, lvl in cells]
    days.sort(key=lambda x: x["date"])

    total_match = re.search(r"([\d,]+)\s+contributions\s+in the last year", html)
    total = int(total_match.group(1).replace(",", "")) if total_match else sum(1 for d in days if d["level"] > 0)
    return days, total


def streaks(days):
    """Longest and current streak of consecutive days with any contribution."""
    longest = {"len": 0, "start": None, "end": None}
    run_len, run_start = 0, None
    for d in days:
        if d["level"] > 0:
            if run_len == 0:
                run_start = d["date"]
            run_len += 1
            if run_len > longest["len"]:
                longest = {"len": run_len, "start": run_start, "end": d["date"]}
        else:
            run_len, run_start = 0, None

    # Current streak: trailing run, allowed to end today or yesterday
    current = {"len": 0, "start": None, "end": None}
    run_len, run_end = 0, None
    for d in reversed(days):
        if d["level"] > 0:
            run_len += 1
            if run_end is None:
                run_end = d["date"]
            run_start = d["date"]
            current = {"len": run_len, "start": run_start, "end": run_end}
        else:
            # tolerate an empty "today" before breaking the trailing run
            if run_len == 0 and run_end is None:
                continue
            break
    return current, longest


def main():
    html = fetch_html(USERNAME)
    days, total = parse(html)
    if not days:
        print("No contribution cells parsed — aborting.", file=sys.stderr)
        sys.exit(1)
    current, longest = streaks(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total": total,
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT} — {len(days)} days, {total} contributions, "
          f"current streak {current['len']}, longest {longest['len']}")


if __name__ == "__main__":
    main()
