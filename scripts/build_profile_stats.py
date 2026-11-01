#!/usr/bin/env python3
"""Render assets/stats.svg — live profile signals in the same design language.

Pulls stars / followers / repos / contributions / language mix from the GitHub
API and draws one card with scripts/build_profile_assets.py's shared palette.
Run: python3 scripts/build_profile_stats.py
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_profile_assets as art  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "assets", "stats.svg"))
LOGIN = "Verlintas"
API = "https://api.github.com"

GQL = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions }
    }
  }
}
"""


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True
    ).stdout.strip()


def req(path, tok, payload=None):
    url = path if path.startswith("http") else API + path
    data = json.dumps(payload).encode() if payload else None
    request = urllib.request.Request(
        url,
        data=data,
        method="POST" if payload else "GET",
        headers={
            "Authorization": "Bearer " + tok,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "profile-stats",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def collect(tok):
    user = req("/users/" + LOGIN, tok)
    repos = req("/users/%s/repos?per_page=100" % LOGIN, tok)
    stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))
    langs = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            data = req("/repos/%s/%s/languages" % (LOGIN, repo["name"]), tok)
        except Exception:
            continue
        for name, size in data.items():
            langs[name] = langs.get(name, 0) + size
    now = datetime.now(timezone.utc)
    data = req(
        "/graphql",
        tok,
        {
            "query": GQL,
            "variables": {
                "login": LOGIN,
                "from": (now - timedelta(days=365)).isoformat(),
                "to": now.isoformat(),
            },
        },
    )
    contrib = data["data"]["user"]["contributionsCollection"]["contributionCalendar"][
        "totalContributions"
    ]
    return {
        "stars": stars,
        "followers": user.get("followers", 0),
        "repos": user.get("public_repos", 0),
        "contrib": contrib,
        "langs": langs,
        "now": now,
    }


def fmt(n):
    return "{:,}".format(int(n))


def render(stats):
    width, height = 1200, 296
    parts = [art.svg_open(width, height, "Live profile signals — stars, followers, repos, contributions, languages")]
    parts.append(art.common_defs())
    parts.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, art.BG))
    parts.append(
        '<rect x="40" y="18" width="1120" height="260" rx="16" fill="%s" stroke="%s"/>'
        % (art.PANEL, art.BORDER)
    )
    parts.append('<rect x="58" y="18" width="300" height="1.2" fill="url(#gLine)" opacity="0.6"/>')

    # header
    parts.append(
        '<circle cx="70" cy="54" r="3.4" fill="%s">'
        '<animate attributeName="opacity" values="1;0.15;1" dur="2s" repeatCount="indefinite"/>'
        "</circle>" % art.RED
    )
    parts.append(
        '<text x="84" y="58" font-family="%s" font-size="10" letter-spacing="4.5" fill="%s">04 / SIGNALS</text>'
        % (art.MONO, art.RED)
    )
    stamp = stats["now"].strftime("%Y-%m-%d")
    parts.append(
        '<text x="1130" y="58" text-anchor="end" font-family="%s" font-size="9" letter-spacing="2" fill="%s">'
        "LIVE · UPDATED %s</text>" % (art.MONO, art.DIM, stamp)
    )

    # four counters
    blocks = [
        (fmt(stats["stars"]), "STARS"),
        (fmt(stats["followers"]), "FOLLOWERS"),
        (fmt(stats["repos"]), "PUBLIC REPOS"),
        (fmt(stats["contrib"]), "CONTRIBUTIONS · 1Y"),
    ]
    starts = [70, 340, 610, 880]
    for (value, label), x in zip(blocks, starts):
        parts.append(
            '<text x="%d" y="132" font-family="%s" font-size="46" font-weight="700" fill="%s" '
            'opacity="0.45" filter="url(#fBlur)">%s</text>' % (x, art.SANS, art.RED, value)
        )
        parts.append(
            '<text x="%d" y="132" font-family="%s" font-size="46" font-weight="700" fill="%s">%s</text>'
            % (x, art.SANS, art.TEXT, value)
        )
        parts.append(
            '<text x="%d" y="156" font-family="%s" font-size="9.5" letter-spacing="3" fill="%s">%s</text>'
            % (x, art.MONO, art.DIM, label)
        )
    # separators
    for x in [320, 590, 860]:
        parts.append('<line x1="%d" y1="96" x2="%d" y2="148" stroke="%s"/>' % (x, x, art.BORDER_SOFT))

    # language mix
    parts.append('<line x1="70" y1="182" x2="1130" y2="182" stroke="%s"/>' % art.BORDER_SOFT)
    parts.append(
        '<text x="70" y="212" font-family="%s" font-size="9.5" letter-spacing="4" fill="%s">LANGUAGES</text>'
        % (art.MONO, art.RED)
    )
    total = sum(stats["langs"].values()) or 1
    top = sorted(stats["langs"].items(), key=lambda kv: kv[1], reverse=True)[:6]
    cx = 70
    for name, size in top:
        pct = "%.1f%%" % (100.0 * size / total)
        parts.append(
            '<text x="%d" y="238" font-family="%s" font-size="11" fill="%s">%s</text>'
            % (cx, art.MONO, art.TEXT, art.esc(name.upper()))
        )
        cx += len(name) * 7.2 + 8
        parts.append(
            '<text x="%d" y="238" font-family="%s" font-size="11" fill="%s">%s</text>'
            % (cx, art.MONO, art.RED_SOFT, pct)
        )
        cx += len(pct) * 7.2 + 22
        if cx > 980:
            break

    parts.append(
        '<text x="1130" y="238" text-anchor="end" font-family="%s" font-size="9" letter-spacing="2" fill="%s">'
        "BY BYTES · PUBLIC REPOS</text>" % (art.MONO, art.DIM)
    )
    parts.append("</svg>")
    return "".join(parts)


def main():
    try:
        stats = collect(token())
        svg = render(stats)
    except Exception as exc:  # best-effort: keep the previous card on failure
        print("stats build failed: %s — leaving stats.svg untouched" % type(exc).__name__)
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote %s (stars=%s followers=%s repos=%s contrib=%s)"
          % (OUT, stats["stars"], stats["followers"], stats["repos"], stats["contrib"]))


if __name__ == "__main__":
    main()
