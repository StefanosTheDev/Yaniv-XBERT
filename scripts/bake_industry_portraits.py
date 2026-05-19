"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial swarm-style aesthetic that the board portraits and
public/assets/images/people/swarm/* photos use:

    smooth continuous-tone B&W subject + black studio background +
    head-and-shoulders crop + faint code/constellation overlays + alpha
    dissolve at the bottom so the silhouette blends into the void.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Reuses the proven processing pipeline from bake_board_portraits.py via
its `bake_directory` helper so the two image sets stay visually
consistent.
"""

from __future__ import annotations

from pathlib import Path

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"


def main() -> None:
    bake.bake_directory(SRC_DIR, OUT_DIR, label="industry portraits")


if __name__ == "__main__":
    main()
