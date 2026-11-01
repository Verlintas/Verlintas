#!/usr/bin/env python3
"""Generate the animated SVG art for the profile README.

Everything on the profile — hero, terminal, stack board, project cards and
dividers — is drawn from this one script so the red/black design system stays
consistent. Run: python3 scripts/build_profile_assets.py
"""
import json
import os
import random
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "assets"))

# ---------------------------------------------------------------- design system
BG = "#050507"          # page black
PANEL = "#0a0a0e"       # card / window fill
PANEL_2 = "#0d0d12"     # raised fill
BORDER = "#2a1116"      # hairline border (red-black)
BORDER_SOFT = "#1b0d11" # quieter border
RED = "#ff2d3d"         # primary accent
RED_SOFT = "#ff5563"    # text accent
RED_DIM = "#8f1622"     # deep accent
TEXT = "#f2f2f5"        # primary text
MUTED = "#9a9aa3"       # secondary text
DIM = "#5f5f6a"         # tertiary text
SANS = "-apple-system,'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'SF Mono','Cascadia Code','JetBrains Mono',Consolas,monospace"


def esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def svg_open(width, height, label):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" aria-label="%s">'
        % (width, height, width, height, esc(label))
    )


def common_defs():
    return f'''<defs>
<radialGradient id="gGlow" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="{RED}" stop-opacity="0.55"/>
<stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="gTitle" x1="0" y1="0" x2="1" y2="0">
<stop offset="0%" stop-color="#ffffff"/>
<stop offset="45%" stop-color="{RED}"/>
<stop offset="55%" stop-color="{RED}"/>
<stop offset="100%" stop-color="#ffffff"/>
</linearGradient>
<linearGradient id="gLine" x1="0" y1="0" x2="1" y2="0">
<stop offset="0%" stop-color="{RED}" stop-opacity="0"/>
<stop offset="50%" stop-color="{RED}" stop-opacity="1"/>
<stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="gCard" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="{PANEL}"/>
<stop offset="100%" stop-color="{PANEL_2}"/>
</linearGradient>
<filter id="fBlur" x="-40%" y="-40%" width="180%" height="180%">
<feGaussianBlur stdDeviation="7"/>
</filter>
<filter id="fSoft" x="-40%" y="-40%" width="180%" height="180%">
<feGaussianBlur stdDeviation="2.4"/>
</filter>
</defs>'''


def grid(width, height, step=40, opacity="0.03"):
    parts = ['<g stroke="#ffffff" stroke-opacity="%s">' % opacity]
    for x in range(0, width + 1, step):
        parts.append('<line x1="%d" y1="0" x2="%d" y2="%d"/>' % (x, x, height))
    for y in range(0, height + 1, step):
        parts.append('<line x1="0" y1="%d" x2="%d" y2="%d"/>' % (y, width, y))
    parts.append("</g>")
    return "".join(parts)


def brackets(width, height, pad=18, size=13, color=RED_DIM):
    p = pad
    s = size
    return (
        '<g fill="none" stroke="%s" stroke-width="1.2" opacity="0.9">'
        '<path d="M%d %d V%d H%d"/>'
        '<path d="M%d %d V%d H%d"/>'
        '<path d="M%d %d V%d H%d"/>'
        '<path d="M%d %d V%d H%d"/>'
        "</g>"
    ) % (
        color,
        p, p + s, p, p + s,
        width - p - s, p, width - p, p + s,
        p, height - p - s, p, height - p,
        width - p - s, height - p, width - p, height - p - s,
    )


def hero():
    width, height = 1200, 360
    random.seed(11)
    parts = [svg_open(width, height, "Verlintas — full-stack and AI developer"), common_defs()]

    parts.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, BG))
    parts.append(grid(width, height))

    # ambient red glows
    parts.append('<ellipse cx="190" cy="40" rx="430" ry="250" fill="url(#gGlow)" opacity="0.45"/>')
    parts.append('<ellipse cx="1010" cy="330" rx="420" ry="240" fill="url(#gGlow)" opacity="0.32"/>')

    # diagonal light sweep
    parts.append(
        '<g transform="rotate(16 600 180)" opacity="0.09">'
        '<rect x="-700" y="-500" width="190" height="1200" fill="%s">'
        '<animate attributeName="x" values="-800;1500" dur="9s" repeatCount="indefinite"/>'
        "</rect></g>" % RED
    )

    # drifting particles
    for i in range(16):
        x = random.randint(30, width - 30)
        y = random.randint(26, height - 30)
        r = random.choice([1, 1, 1.5, 2])
        dur = random.uniform(3.0, 7.0)
        begin = random.uniform(0, 3)
        parts.append(
            '<circle cx="%d" cy="%d" r="%s" fill="%s">'
            '<animate attributeName="opacity" values="0.04;0.65;0.04" dur="%.1fs" '
            'begin="%.1fs" repeatCount="indefinite"/>'
            '<animate attributeName="cy" values="%d;%d;%d" dur="%.1fs" begin="%.1fs" repeatCount="indefinite"/>'
            "</circle>"
            % (x, y, r, RED_SOFT, dur, begin, y, y - random.randint(6, 16), y, dur * 1.4, begin)
        )

    parts.append(brackets(width, height))

    # title with glow copy
    parts.append(
        '<text x="600" y="182" text-anchor="middle" font-family="%s" font-size="96" '
        'font-weight="700" letter-spacing="12" fill="%s" opacity="0.55" filter="url(#fBlur)">VERLINTAS</text>'
        % (SANS, RED)
    )
    parts.append(
        '<text x="600" y="182" text-anchor="middle" font-family="%s" font-size="96" '
        'font-weight="700" letter-spacing="12" fill="url(#gTitle)">VERLINTAS</text>' % SANS
    )

    parts.append(
        '<text x="600" y="228" text-anchor="middle" font-family="%s" font-size="13" '
        'letter-spacing="7" fill="%s">FULL-STACK &amp; AI DEVELOPER</text>' % (MONO, RED_SOFT)
    )
    parts.append(
        '<text x="600" y="256" text-anchor="middle" font-family="%s" font-size="10.5" '
        'letter-spacing="3.5" fill="%s">ANDROID · KOTLIN MULTIPLATFORM · AI AGENTS · SECURITY TOOLS</text>'
        % (MONO, MUTED)
    )

    # bottom meta
    parts.append(
        '<circle cx="70" cy="326" r="3.4" fill="%s">'
        '<animate attributeName="opacity" values="1;0.15;1" dur="1.8s" repeatCount="indefinite"/>'
        "</circle>" % RED
    )
    parts.append(
        '<text x="84" y="330" font-family="%s" font-size="10" letter-spacing="2.6" fill="%s">'
        "BEIJING, CN · BORN 2010</text>" % (MONO, DIM)
    )
    parts.append(
        '<text x="1130" y="330" text-anchor="end" font-family="%s" font-size="10" '
        'letter-spacing="2.6" fill="%s">JUST FOR FUN.</text>' % (MONO, DIM)
    )

    # moving light along the bottom edge
    parts.append('<rect x="0" y="359" width="%d" height="1" fill="%s"/>' % (width, BORDER))
    parts.append(
        '<rect x="-200" y="358" width="180" height="2" fill="url(#gLine)">'
        '<animate attributeName="x" values="-220;1220" dur="6s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append("</svg>")
    return "".join(parts)


def terminal():
    width, height = 1200, 360
    x0, y0, w, h = 40, 20, 1120, 320
    lines = [
        ("cmd", "~ $ whoami"),
        ("out", "Verlintas — full-stack & AI developer"),
        ("out", "born 2010 · Beijing, CN · offline-first at heart"),
        ("gap", ""),
        ("cmd", "~ $ cat focus.txt"),
        ("out", "Android · Kotlin Multiplatform · AI agents"),
        ("out", "security & privacy tooling · just for fun"),
        ("gap", ""),
        ("cmd", '~ $ echo "less noise, more signal"'),
        ("out", "less noise, more signal"),
    ]
    base_y = 100
    line_h = 22

    parts = [svg_open(width, height, "Terminal — whoami, focus, less noise more signal"), common_defs()]
    parts.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, BG))

    # window glow + body
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="16" fill="%s" opacity="0.6" filter="url(#fSoft)"/>'
                 % (x0, y0 + 4, w, h, RED_DIM))
    parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="16" fill="url(#gCard)" stroke="%s"/>'
                 % (x0, y0, w, h, BORDER))

    # title bar
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>' % (x0, y0 + 36, x0 + w, y0 + 36, BORDER))
    dots = [(66, RED, 1.0), (88, "#5a1a1f", 0.95), (110, "#3a3a40", 0.9)]
    for cx, color, op in dots:
        parts.append('<circle cx="%d" cy="%d" r="4.6" fill="%s" opacity="%s"/>' % (cx, y0 + 18, color, op))
    parts.append('<text x="134" y="%d" font-family="%s" font-size="11" letter-spacing="1.4" fill="%s">'
                 "verlintas@dev — zsh</text>" % (y0 + 22, MONO, DIM))
    parts.append('<text x="%d" y="%d" text-anchor="end" font-family="%s" font-size="9.5" '
                 'letter-spacing="2" fill="%s">01 / WHOAMI</text>' % (x0 + w - 22, y0 + 22, MONO, DIM))

    # body lines (fade + slide in, then freeze)
    for i, (kind, text) in enumerate(lines):
        y = base_y + i * line_h
        begin = 0.35 + i * 0.5
        if kind == "gap":
            continue
        if kind == "cmd":
            prompt, _, rest = text.partition(" ")
            body = (
                '<text x="72" y="%d" font-family="%s" font-size="13.5">'
                '<tspan fill="%s">%s</tspan><tspan fill="%s"> %s</tspan></text>'
                % (y, MONO, RED_SOFT, esc(prompt), TEXT, esc(rest))
            )
        else:
            body = '<text x="72" y="%d" font-family="%s" font-size="13.5" fill="%s">%s</text>' % (
                y, MONO, MUTED, esc(text)
            )
        parts.append(
            '<g opacity="0" transform="translate(0,6)">'
            '<animate attributeName="opacity" to="1" begin="%.2fs" dur="0.28s" fill="freeze"/>'
            '<animateTransform attributeName="transform" type="translate" values="0 6;0 0" '
            'begin="%.2fs" dur="0.28s" fill="freeze"/>%s</g>' % (begin, begin, body)
        )

    # blinking cursor on the last prompt line
    cursor_y = base_y + len(lines) * line_h - 6
    parts.append('<text x="72" y="%d" font-family="%s" font-size="13.5" fill="%s">~ $</text>'
                 % (cursor_y, MONO, RED_SOFT))
    parts.append(
        '<rect x="112" y="%d" width="8" height="15" fill="%s">'
        '<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.5;0.55;0.95;1" '
        'dur="1.1s" repeatCount="indefinite"/></rect>' % (cursor_y - 12, RED)
    )

    # scanline
    parts.append(
        '<rect x="%d" y="%d" width="%d" height="1.5" fill="url(#gLine)" opacity="0.16">'
        '<animate attributeName="y" values="%d;%d" dur="5.5s" repeatCount="indefinite"/></rect>'
        % (x0 + 20, y0 + 50, w - 40, y0 + 50, y0 + h - 12)
    )

    parts.append(brackets(width, height, pad=14, size=12))
    parts.append("</svg>")
    return "".join(parts)


def chip_width(text):
    return 14 + 10 + len(text) * 6.6 + 14


def chip(x, y, text, dot_color=RED):
    pad_l, pad_r, height = 14, 14, 30
    dot = 10
    width = chip_width(text)
    parts = [
        "<g>"
        '<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="15" fill="%s" stroke="%s"/>'
        '<circle cx="%.1f" cy="%d" r="2.6" fill="%s"/>'
        '<text x="%.1f" y="%d" font-family="%s" font-size="11.5" fill="%s">%s</text>'
        "</g>"
        % (
            x, y, width, height, PANEL_2, BORDER_SOFT,
            x + pad_l + 3, y + height / 2, dot_color,
            x + pad_l + dot + 2, y + 19.5, MONO, TEXT, esc(text),
        )
    ]
    return "".join(parts), width


BRAND = {
    "Kotlin": "#7F52FF", "Swift": "#FA7343", "Rust": "#DEA584", "TypeScript": "#3178C6",
    "Python": "#3776AB", "C / NDK": "#A8B9CC", "Shell": "#4EAA25",
    "Android": "#3DDC84", "Kotlin Multiplatform": "#7F52FF", "Jetpack Compose": "#4285F4",
    "Compose Multiplatform": "#4285F4", "SwiftUI": "#0D84F4", "Gradle / AGP": "#03A9F4",
    "LLM Agents": "#FF6F00", "MCP": "#FF6F00", "On-device Inference": "#00BFA5",
    "APK Static Analysis": "#00C2A8", "TLS Fingerprinting": "#00A1D6",
    "adb / Shizuku": "#3DDC84", "Accessibility Automation": "#FFB300",
    "E2EE": "#8E44AD", "SMB2 / WebDAV": "#546E7A", "DLNA / Cast": "#00ACC1",
    "Keystore Crypto": "#FF7043", "Media3 / libVLC": "#FF8A65",
}

STACK_GROUPS = [
    ("LANGUAGES", ["Kotlin", "Swift", "Rust", "TypeScript", "Python", "C / NDK", "Shell"]),
    ("PLATFORMS", ["Android", "Kotlin Multiplatform", "Jetpack Compose", "Compose Multiplatform", "SwiftUI", "Gradle / AGP"]),
    ("SYSTEMS & SECURITY", [
        "LLM Agents", "MCP", "On-device Inference", "APK Static Analysis", "TLS Fingerprinting",
        "adb / Shizuku", "Accessibility Automation", "E2EE", "SMB2 / WebDAV", "DLNA / Cast",
        "Keystore Crypto", "Media3 / libVLC",
    ]),
]


def stack():
    width = 1200
    start_x, max_x = 70, 1130
    rows = []
    y = 100
    last_chip_top = 0
    for label, items in STACK_GROUPS:
        rows.append(("label", label, y))
        cx, cy = start_x, y + 12
        for item in items:
            cw = chip_width(item)
            if cx + cw > max_x:
                cx = start_x
                cy += 40
            rows.append(("chip", item, cx, cy))
            cx += cw + 10
        last_chip_top = cy
        y = cy + 64
    height = last_chip_top + 30 + 26 + 8

    parts = [svg_open(width, height, "Stack — languages, platforms, systems and security"), common_defs()]
    parts.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, BG))
    parts.append('<rect x="40" y="18" width="1120" height="%d" rx="16" fill="%s" stroke="%s"/>'
                 % (height - 26, PANEL, BORDER))
    parts.append('<rect x="58" y="18" width="300" height="1.2" fill="url(#gLine)" opacity="0.6"/>')
    parts.append('<text x="70" y="54" font-family="%s" font-size="10" letter-spacing="4.5" fill="%s">02 / STACK</text>'
                 % (MONO, RED))
    parts.append('<text x="1130" y="54" text-anchor="end" font-family="%s" font-size="9" letter-spacing="2" fill="%s">'
                 "TOOLS OF THE TRADE</text>" % (MONO, DIM))

    for row in rows:
        if row[0] == "label":
            parts.append('<text x="70" y="%d" font-family="%s" font-size="10" letter-spacing="4.5" fill="%s">%s</text>'
                         % (row[2], MONO, RED, esc(row[1])))
        else:
            rendered, _ = chip(row[2], row[3], row[1], BRAND.get(row[1], RED))
            parts.append(rendered)

    parts.append("</svg>")
    return "".join(parts)


PROJECTS = [
    ("01", "NOIR", "Verlintas/NOIR", "155", ["Kotlin", "KMP", "TUI"],
     ["Android privacy audit over adb:", "permissions, endpoints, data flows —", "reversible fixes."]),
    ("02", "BetterAIChat", "Verlintas/BetterAIChat", "124", ["Kotlin", "Compose", "AI"],
     ["Native Android agent with your own", "API keys, Shizuku shell, device", "tools and voice."]),
    ("03", "NovaBAIC", "Verlintas/NovaBAIC", "23", ["Kotlin", "AI", "MCP"],
     ["Local-first agent: 57 device tools,", "biomimetic memory, MCP — no", "GMS required."]),
    ("04", "Syna-NUSV", "NUSV/Syna-NUSV", "22", ["Kotlin", "KMP", "E2EE"],
     ["Offline-first LAN messenger:", "end-to-end encrypted, self-hosted,", "with a tamper shield."]),
    ("05", "OpenVisum", "Verlintas/OpenVisum", "1", ["Kotlin", "Compose", "libVLC"],
     ["libVLC video player: every format,", "auto subtitles and audio tracks,", "DLNA casting, 9 themes."]),
    ("06", "VerlinPark", "Verlintas/VerlinPark", "1", ["Rust", "macOS", "Agents"],
     ["Native macOS agentic development", "environment for running and", "supervising agent teams."]),
]


def fetch_stars(repos):
    """Live star counts at build time; falls back to the curated numbers."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return {}
    stars = {}
    for repo in repos:
        try:
            request = urllib.request.Request(
                "https://api.github.com/repos/" + repo,
                headers={"Authorization": "Bearer " + token, "User-Agent": "profile-art"},
            )
            with urllib.request.urlopen(request, timeout=8) as resp:
                stars[repo] = json.loads(resp.read().decode()).get("stargazers_count")
        except Exception:
            continue
    return stars


def projects():
    width = 1200
    card_w, card_h = 360, 216
    gap_x, gap_y = 20, 22
    x0, y0 = 40, 84
    height = y0 + 2 * card_h + gap_y + 24
    live = fetch_stars([p[2] for p in PROJECTS])

    parts = [svg_open(width, height, "Projects — NOIR, BetterAIChat, NovaBAIC, Syna, OpenVisum, VerlinPark"),
             common_defs()]
    parts.append('<rect width="%d" height="%d" fill="%s"/>' % (width, height, BG))
    parts.append('<text x="70" y="52" font-family="%s" font-size="10" letter-spacing="4.5" fill="%s">03 / PROJECTS</text>'
                 % (MONO, RED))
    parts.append('<text x="1130" y="52" text-anchor="end" font-family="%s" font-size="9" letter-spacing="2" fill="%s">'
                 "PINNED · STARS LIVE</text>" % (MONO, DIM))

    for i, (index, name, repo, fallback, tags, desc) in enumerate(PROJECTS):
        stars = str(live.get(repo) if live.get(repo) is not None else fallback)
        col, row = i % 3, i // 3
        x = x0 + col * (card_w + gap_x)
        y = y0 + row * (card_h + gap_y)
        parts.append(
            '<ellipse cx="%d" cy="%d" rx="150" ry="90" fill="url(#gGlow)" opacity="0.10">'
            '<animate attributeName="opacity" values="0.06;0.16;0.06" dur="%.1fs" begin="%.1fs" repeatCount="indefinite"/>'
            "</ellipse>"
            % (x + 70, y + 40, 6 + (i % 3), i * 0.7)
        )
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="url(#gCard)" stroke="%s"/>'
                     % (x, y, card_w, card_h, BORDER))
        parts.append('<rect x="%d" y="%d" width="%d" height="1.2" fill="url(#gLine)" opacity="0.55"/>'
                     % (x + 18, y, card_w - 36))
        parts.append('<text x="%d" y="%d" text-anchor="end" font-family="%s" font-size="10" '
                     'letter-spacing="2" fill="%s">%s</text>' % (x + card_w - 20, y + 32, MONO, DIM, index))
        parts.append('<text x="%d" y="%d" font-family="%s" font-size="19.5" font-weight="600" fill="%s">%s</text>'
                     % (x + 22, y + 46, SANS, TEXT, esc(name)))
        parts.append('<text x="%d" y="%d" font-family="%s" font-size="10.5" letter-spacing="1.5" fill="%s">★ %s</text>'
                     % (x + 22, y + 68, MONO, RED_SOFT, stars))
        for j, line in enumerate(desc):
            parts.append('<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s">%s</text>'
                         % (x + 22, y + 102 + j * 19, SANS, MUTED, esc(line)))
        parts.append('<text x="%d" y="%d" font-family="%s" font-size="9.2" letter-spacing="1.6" fill="%s">%s</text>'
                     % (x + 22, y + card_h - 18, MONO, DIM, " · ".join(t.upper() for t in tags)))
        parts.append('<text x="%d" y="%d" text-anchor="end" font-family="%s" font-size="12" fill="%s">↗</text>'
                     % (x + card_w - 22, y + card_h - 18, MONO, RED_DIM))

    parts.append("</svg>")
    return "".join(parts)


def divider():
    width, height = 1200, 22
    parts = [svg_open(width, height, "divider"), common_defs()]
    parts.append('<line x1="0" y1="11" x2="%d" y2="11" stroke="%s"/>' % (width, BORDER))
    parts.append(
        '<rect x="-240" y="10" width="240" height="2" fill="url(#gLine)">'
        '<animate attributeName="x" values="-240;1200" dur="7s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append(
        '<circle cx="0" cy="11" r="2.2" fill="%s">'
        '<animate attributeName="cx" values="0;1200" dur="7s" repeatCount="indefinite"/>'
        "</circle>" % RED
    )
    parts.append("</svg>")
    return "".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    assets = {
        "hero.svg": hero(),
        "terminal.svg": terminal(),
        "stack.svg": stack(),
        "projects.svg": projects(),
        "divider.svg": divider(),
    }
    for name, content in assets.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote %s (%d bytes)" % (path, len(content)))


if __name__ == "__main__":
    main()
