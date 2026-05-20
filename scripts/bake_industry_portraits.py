"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial style as the board portraits on /leadership.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Reuses the proven processing pipeline from bake_board_portraits.py via
its `bake_directory` helper with the EXACT same parameters the board
baker uses. The only override is `overlay_scale=3.0` (which the board
baker also uses) so the editorial code + constellation overlays read
clearly behind the subject.
"""

from __future__ import annotations

from pathlib import Path

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"


def main() -> None:
    # Same call signature as bake_board_portraits.py main() — we want
    # industry portraits to come out of the same pipeline as the board
    # portraits so the two image sets stay visually consistent on the
    # leadership and our-customers-preview pages.
    bake.bake_directory(
        SRC_DIR,
        OUT_DIR,
        label="industry portraits",
        overlay_scale=3.0,
    )


if __name__ == "__main__":
    main()
