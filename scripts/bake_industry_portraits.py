"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial style as the board portraits on /leadership.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Why the staging step:

The board sources arrive as evenly-lit professional studio shots, so the
canonical bake pipeline (in bake_board_portraits.py) — same call this
script makes — produces clean editorial portraits. The industry sources
are casual / press-style photos with heavy directional lighting (one
side of the face in deep shadow, e.g. hospitality, insurance,
healthcare). Feeding those straight into the same bake pipeline
preserves the harsh shadow because the curve is tuned for already-
balanced inputs.

To avoid touching the board pipeline at all (so /leadership stays
exactly as-is) we instead pre-stage each industry original: autocontrast
to normalize the histogram and a shadow-lift gamma to bring the dark
side of faces up close to the bright side. The staged copies look like
board sources — evenly lit, mid-bright skin — and the EXACT same
`bake_directory(..., overlay_scale=3.0)` call we use for the boards
then produces output that matches the board grid.

We never modify the originals on disk; staging goes to a temp dir.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"


def even_lighting(img: Image.Image) -> Image.Image:
    """Normalize, shadow-lift, and brighten the source so it enters the
    bake looking like a board studio shot.

    Board sources sit at very high luminance (skin ~200/255) because
    they're shot in even studio light. The bake's tonal curve assumes
    that — `bw_brightness=0.92` then lands skin at ~184 in output, the
    bright editorial look that matches /leadership.

    Industry sources are casual / press-style: skin sits at 140-180,
    one side often deep in shadow. Without compensation, that 0.92
    multiplier lands skin at ~140 — visibly darker than the board grid.

    Three-step normalization:
      1. autocontrast (1% cutoff) — snap to full 0..255 range.
      2. luminance-dependent shadow lift — raise the dark half of
         directionally-lit faces (hospitality, healthcare, insurance)
         toward the bright half. Highlights are left alone so white
         shirts and hair specular survive intact.
      3. global midtone gamma — bring overall skin brightness up to
         the ~200 board target so the bake's `0.92` brightness
         multiplier produces output that sits next to the boards
         without looking dim.
    """
    rgb = img.convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=1)

    arr = np.asarray(rgb, dtype=np.float32) / 255.0
    lum = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]

    # Step 2: shadow lift. Mask peaks at 1.0 for very dark pixels and
    # falls to 0 by mid-grey. ^1.2 keeps the lift concentrated in true
    # shadows so we don't muddy the midtones.
    shadow_mask = np.clip(1.0 - lum / 0.6, 0.0, 1.0) ** 1.2
    lift = 0.32 * shadow_mask  # max +82/255 lift in deepest shadows
    arr = np.clip(arr + lift[..., None], 0.0, 1.0)

    # Step 3: midtone gamma to brighten overall. gamma<1 lifts midtones
    # while leaving 0 at 0 and 1 at 1 — won't blow highlights or muddy
    # blacks.
    arr = np.power(arr, 0.78)

    return Image.fromarray((arr * 255.0).astype(np.uint8))


def stage_sources(src_dir: Path, dest: Path) -> None:
    """Copy and pre-condition every source from ``src_dir`` into ``dest``.
    Resulting files have the same filenames so ``bake_directory`` writes
    canonical output names (industry-healthcare.png, …)."""
    dest.mkdir(parents=True, exist_ok=True)
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    files: list[Path] = []
    for pat in patterns:
        files.extend(src_dir.glob(pat))
    files = sorted(files)
    for p in files:
        staged = even_lighting(Image.open(p))
        staged.save(dest / (p.stem + ".png"), "PNG")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="industry-staging-") as td:
        staging = Path(td)
        stage_sources(SRC_DIR, staging)

        # Same call signature as bake_board_portraits.py main() — we want
        # industry portraits to come out of the same pipeline as the
        # board portraits so the two image sets stay visually consistent
        # on the leadership and our-customers-preview pages.
        bake.bake_directory(
            staging,
            OUT_DIR,
            label="industry portraits",
            overlay_scale=3.0,
        )


if __name__ == "__main__":
    main()
