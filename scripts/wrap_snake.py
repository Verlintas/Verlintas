#!/usr/bin/env python3
"""Wrap the snk contribution-snake SVG in the profile's dark card frame.

The snake generator emits a transparent SVG; this adds the same panel fill,
rounded corners and hairline border the other profile art uses.
Usage: python3 scripts/wrap_snake.py dist/github-snake.svg
"""
import re
import sys

BG = "#0a0a0e"
BORDER = "#2a1116"


def main(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    root_match = re.search(r"<svg[^>]*>", text)
    if not root_match:
        raise SystemExit("no <svg> element in %s" % path)
    root = root_match.group(0)

    view_box = re.search(r'viewBox="([-0-9.]+) ([-0-9.]+) ([0-9.]+) ([0-9.]+)"', root)
    if view_box:
        min_x, min_y, width, height = (float(value) for value in view_box.groups())
    else:
        width_match = re.search(r'width="([0-9.]+)"', root)
        height_match = re.search(r'height="([0-9.]+)"', root)
        if not (width_match and height_match):
            raise SystemExit("cannot determine size in %s" % path)
        min_x, min_y = 0.0, 0.0
        width = float(width_match.group(1))
        height = float(height_match.group(1))

    background = '<rect x="%g" y="%g" width="%g" height="%g" rx="14" fill="%s"/>' % (
        min_x, min_y, width, height, BG)
    border = (
        '<rect x="%g" y="%g" width="%g" height="%g" rx="14" fill="none" stroke="%s"/>'
        % (min_x + 0.6, min_y + 0.6, width - 1.2, height - 1.2, BORDER)
    )
    text = text.replace(root, root + background, 1)
    text = text.replace("</svg>", border + "</svg>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrapped %s (%gx%g at %g,%g)" % (path, width, height, min_x, min_y))


if __name__ == "__main__":
    main(sys.argv[1])
