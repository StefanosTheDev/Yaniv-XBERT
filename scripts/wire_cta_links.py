"""
Wire every "Get a Demo" and "Start Free Trial" CTA across the legacy
HTML pages (and any TSX/JSX components) the same way the top nav wires
them:

    Get a Demo      ->  href="/demo"                              (internal)
    Start Free Trial->  href="https://www.nextiva.com/join"
                        + target="_blank" + rel="noopener noreferrer"
    Free 14-Day Trial -> same as Start Free Trial (it's the same CTA
                         used on pricing cards)

The script only touches anchors whose href is currently '#', so it is
idempotent: running it twice is a no-op, and any links that already
have a real target (Free Trial in the nav, /demo links in the auth
pages, etc.) are left untouched.

Run:
  python3 scripts/wire_cta_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to scan. We keep this list explicit so the script never
# accidentally rewrites generated files, lockfiles, or transcripts.
TARGET_GLOBS = [
    "components/legacy/*.html",
    "components/*.tsx",
    "app/**/*.tsx",
]

DEMO_HREF = "/demo"
FREE_TRIAL_HREF = "https://www.nextiva.com/join"
FREE_TRIAL_EXTRAS = ' target="_blank" rel="noopener noreferrer"'

# Each entry: (label_regex, replacement_href, extra_attrs_after_class_value)
# We match anchors that:
#   - currently have href="#"
#   - have any class attribute (we keep whatever classes were there)
#   - render exactly one of these visible labels
#
# We do not touch anchors that already point somewhere real. That keeps
# the replacement idempotent and prevents stomping on already-wired
# CTAs (the top-nav buttons, the auth foot links, etc.).
LABEL_RULES = [
    # Demo CTAs (any case variant)
    (r"Get [Aa] Demo", DEMO_HREF, ""),
    (r"Get a demo", DEMO_HREF, ""),
    # Free trial CTAs
    (r"Start Free Trial", FREE_TRIAL_HREF, FREE_TRIAL_EXTRAS),
    (r"Start free trial", FREE_TRIAL_HREF, FREE_TRIAL_EXTRAS),
    (r"Free 14-Day Trial", FREE_TRIAL_HREF, FREE_TRIAL_EXTRAS),
]


def rewrite(content: str) -> tuple[str, int]:
    """Return ``(rewritten_content, changes)``."""
    total = 0

    for label_re, href, extras in LABEL_RULES:
        # Match: <a href="#" class="..."[ optional attrs ]>LABEL</a>
        # We keep whatever class string + extra attrs the anchor already
        # carried, only changing href and (for Free Trial) appending
        # target/rel after the class attribute.
        pattern = re.compile(
            r'<a\s+href="#"\s+class="([^"]*)"([^>]*)>\s*('
            + label_re
            + r")\s*</a>",
            flags=re.IGNORECASE,
        )

        def _repl(m: re.Match) -> str:
            nonlocal total
            total += 1
            classes = m.group(1)
            existing_attrs = m.group(2)
            label = m.group(3)
            attr_tail = existing_attrs
            if extras and "target=" not in existing_attrs:
                attr_tail = existing_attrs + extras
            return (
                f'<a href="{href}" class="{classes}"{attr_tail}>{label}</a>'
            )

        content = pattern.sub(_repl, content)

    return content, total


def main() -> int:
    files: list[Path] = []
    for pat in TARGET_GLOBS:
        files.extend(ROOT.glob(pat))
    files = sorted(set(files))

    grand_total = 0
    touched_files = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        updated, changes = rewrite(original)
        if changes and updated != original:
            path.write_text(updated, encoding="utf-8")
            grand_total += changes
            touched_files += 1
            print(f"  {path.relative_to(ROOT)}: {changes} link(s) wired")

    print(f"\nWired {grand_total} link(s) across {touched_files} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
