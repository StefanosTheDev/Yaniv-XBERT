#!/usr/bin/env python3
"""Replace the 40 placeholder swarm dots with <img> tags pointing at the
processed portraits. Operates on both the canonical legacy index and the
mirrored root index so both stay in sync.

Idempotent: a second run is a no-op because the placeholder marker (an
<i class="ri-user-fill"> child) is gone after the first pass.
"""

from __future__ import annotations

import sys
from pathlib import Path


PLACEHOLDER = '<span class="ai-team-dot"><i class="ri-user-fill"></i></span>'


def build_dot(idx: int) -> str:
    return (
        f'<span class="ai-team-dot">'
        f'<img src="/assets/images/people/swarm/swarm-{idx:02d}.png" '
        f'alt="" loading="lazy" decoding="async">'
        f'</span>'
    )


def swap(file_path: Path) -> int:
    text = file_path.read_text()
    count = text.count(PLACEHOLDER)
    if count == 0:
        print(f"{file_path}: no placeholders found (already swapped?)")
        return 0
    if count != 40:
        print(
            f"{file_path}: expected 40 placeholders, found {count}; aborting",
            file=sys.stderr,
        )
        return 1

    out_parts: list[str] = []
    cursor = 0
    for i in range(1, 41):
        pos = text.index(PLACEHOLDER, cursor)
        out_parts.append(text[cursor:pos])
        out_parts.append(build_dot(i))
        cursor = pos + len(PLACEHOLDER)
    out_parts.append(text[cursor:])

    file_path.write_text("".join(out_parts))
    print(f"{file_path}: swapped 40 placeholders")
    return 0


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = repo_root.parent

    targets = [
        repo_root / "components" / "legacy" / "index.html",
        workspace_root / "index.html",
    ]

    rc = 0
    for t in targets:
        if not t.exists():
            print(f"missing: {t}", file=sys.stderr)
            rc = 1
            continue
        rc |= swap(t)
    return rc


if __name__ == "__main__":
    sys.exit(main())
