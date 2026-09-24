#!/usr/bin/env python3
"""Generate a GitHub-style contribution heatmap SVG for the profile README.

Why self-hosted: the native contribution graph is not shown on GitHub mobile,
and third-party card services are unreliable from some networks. This script
runs in Actions with the built-in token, commits the SVG next to the README,
so the image is served from GitHub itself.

Usage: python3 scripts/build_contribution_heatmap.py
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

LOGIN = "Verlintas"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "contrib-heatmap.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""

# GitHub dark-mode green scale
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
TEXT = "#8b949e"


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def fetch(tok):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={
            "Authorization": "Bearer " + tok,
            "Content-Type": "application/json",
            "User-Agent": "profile-heatmap-builder",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    if "errors" in data:
        raise RuntimeError(data["errors"])
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal


def level(count):
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 6:
        return 2
    if count <= 9:
        return 3
    return 4


def month_starts(weeks):
    """Index of weeks where the month changes, for the month labels."""
    marks = []
    last_month = None
    for i, week in enumerate(weeks):
        days = week["contributionDays"]
        if not days:
            continue
        first = days[0]["date"]  # YYYY-MM-DD
        month = first[5:7]
        if month != last_month:
            marks.append((i, first))
            last_month = month
    return marks


def build_svg(cal):
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    cell, gap = 11, 3
    left, top = 32, 22
    width = left + len(weeks) * (cell + gap) + 6
    height = top + 7 * (cell + gap) + 22
    parts = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" aria-label="%d contributions in the last year">'
        % (width, height, width, height, total)
    )
    parts.append(
        '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:10px;fill:%s}</style>'
        % TEXT
    )

    # month labels
    for i, first in month_starts(weeks):
        if i == 0:
            continue
        name = datetime.strptime(first, "%Y-%m-%d").strftime("%b")
        x = left + i * (cell + gap)
        parts.append('<text x="%d" y="12">%s</text>' % (x, name))

    # weekday labels (Mon/Wed/Fri)
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = top + row * (cell + gap) + cell - 2
        parts.append('<text x="0" y="%d">%s</text>' % (y, label))

    # cells
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            row = day["weekday"]
            x = left + wi * (cell + gap)
            y = top + row * (cell + gap)
            color = LEVELS[level(day["contributionCount"])]
            parts.append(
                '<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s">'
                "<title>%s: %d</title></rect>"
                % (x, y, cell, cell, color, day["date"], day["contributionCount"])
            )

    # footer: total + legend
    fy = top + 7 * (cell + gap) + 12
    parts.append('<text x="%d" y="%d">%d contributions in the last year</text>' % (left, fy, total))
    lx = width - 6 - 5 * (cell + 2) - 30
    parts.append('<text x="%d" y="%d">Less</text>' % (lx - 26, fy))
    for li, color in enumerate(LEVELS):
        parts.append(
            '<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s"/>'
            % (lx + li * (cell + 2), fy - 9, cell - 1, cell - 1, color)
        )
    parts.append('<text x="%d" y="%d">More</text>' % (lx + 5 * (cell + 2) + 4, fy))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    tok = token()
    if not tok:
        print("no token available", file=sys.stderr)
        return 1
    cal = fetch(tok)
    svg = build_svg(cal)
    old = ""
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = f.read()
    if old == svg:
        print("no change")
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("heatmap updated:", cal["totalContributions"], "contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
