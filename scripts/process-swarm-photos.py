#!/usr/bin/env python3
"""Post-process AI-generated swarm portraits down to a tiny on-page size.

The swarm dots render at 32-40px (mobile/desktop). At ~2x retina that is
80x80, so a 192x192 source is plenty crisp while keeping each PNG tiny.
We also flatten to 8-bit grayscale (the source images are already B&W so
this is lossless visually) and run Pillow's PNG optimizer for ~10-25KB
per file vs. ~500KB raw.

Reads every PNG from scripts/_swarm_raw/ and writes the processed copy
to public/assets/images/people/swarm/ with the same filename. Idempotent
across reruns.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


OUT_SIZE = 192


def process_one(src: Path, dst: Path) -> None:
    img = Image.open(src)
    img = img.convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    img = img.convert("L")
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "PNG", optimize=True)


def main() -> int:
    import os

    repo_root = Path(__file__).resolve().parents[1]
    src_dir = Path(
        os.environ.get(
            "SWARM_SRC",
            "/Users/yanivmasjedi/.cursor/projects/Users-yanivmasjedi-Desktop-XBert-Project/assets",
        )
    )
    dst_dir = repo_root / "public" / "assets" / "images" / "people" / "swarm"

    if not src_dir.exists():
        print(f"missing: {src_dir}", file=sys.stderr)
        return 1

    sources = sorted(
        p for p in src_dir.iterdir()
        if p.suffix.lower() == ".png" and p.name.startswith("swarm-")
    )
    if not sources:
        print(f"no PNGs in {src_dir}", file=sys.stderr)
        return 1

    total_in = 0
    total_out = 0
    for src in sources:
        dst = dst_dir / src.name
        process_one(src, dst)
        size_in = src.stat().st_size
        size_out = dst.stat().st_size
        total_in += size_in
        total_out += size_out
        print(f"{src.name}: {size_in/1024:>5.0f}KB -> {size_out/1024:>4.0f}KB")
    print(
        f"\ntotal: {total_in/1024:.0f}KB -> {total_out/1024:.0f}KB "
        f"({100*total_out/total_in:.0f}%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
