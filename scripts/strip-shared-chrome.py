#!/usr/bin/env python3
"""
One-shot migration: strip the now-duplicated SVG sprite, <nav>, mobile nav,
and <footer> blocks from each legacy/*.html file. After this runs, the
shared <Nav>, <MobileNav>, <Footer>, and <XBertSvgSprite> React components
in app/layout.tsx are the single source of truth for site-wide chrome.

Run from the project root: `python3 scripts/strip-shared-chrome.py`
This script is idempotent: re-running on already-stripped files is a no-op.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEGACY = REPO / "components" / "legacy"

FILES = [
    "index.html",
    "how-xbert-works.html",
    "integrations.html",
    "security.html",
    "pricing.html",
]

# The first line of the actual page body in each file is one of these.
BODY_START_MARKERS = [
    "    <!-- Page Sections — add here as they are designed -->\n",
    "    <main>\n",
]

FOOTER_START = "    <!-- Footer -->\n"
FOOTER_END = "    </footer>\n"


def strip(path: Path) -> str:
    src = path.read_text()

    # Find where the page body actually begins
    body_start = -1
    for marker in BODY_START_MARKERS:
        idx = src.find(marker)
        if idx != -1:
            body_start = idx
            break
    if body_start == -1:
        return f"{path.name}: no body marker found (already stripped?), skipped"

    # Find the footer block to remove
    footer_start = src.find(FOOTER_START)
    if footer_start == -1:
        return f"{path.name}: no footer marker found (already stripped?), skipped"
    footer_end_idx = src.find(FOOTER_END, footer_start)
    if footer_end_idx == -1:
        return f"{path.name}: malformed footer, skipped"
    footer_end = footer_end_idx + len(FOOTER_END)

    body = src[body_start:footer_start].rstrip()
    after_footer = src[footer_end:]

    # Reassemble: just the body, then any post-footer scripts (e.g. Wistia
    # on the home page), separated by a single blank line.
    new_src = body + "\n"
    if after_footer.strip():
        new_src += "\n" + after_footer.lstrip()

    path.write_text(new_src)
    return f"{path.name}: stripped {body_start} bytes head + {footer_end - footer_start} bytes footer"


def main() -> None:
    for name in FILES:
        path = LEGACY / name
        if not path.exists():
            print(f"{name}: missing")
            continue
        print(strip(path))


if __name__ == "__main__":
    main()
