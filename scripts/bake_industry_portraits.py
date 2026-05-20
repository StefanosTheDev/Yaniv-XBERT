"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial swarm-style aesthetic as the board portraits.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Why we pre-upscale through Real-ESRGAN:

The industry sources are press / casual photos at small sizes — several
are below 300px on the long edge (construction 183x275, financial
180x180, insurance 225x225, real-estate 158x196). The board sources
are all 800px+, which is part of why their post-bake faces read crisp.
Without pre-sharpening, no amount of pipeline tuning can restore detail
that isn't in the source — the user has spent two days hitting that
ceiling.

Real-ESRGAN's general x4 model (realesrgan-x4plus, model index 4) is
specifically trained to recover face / hair / texture detail when
upscaling real photos. Running each source through it before the bake
gives the bake a 1200px+ input with realistic facial detail, so the
post-bake face matches the board crispness instead of looking soft.

This requires GPU access (Metal on macOS via NCNN/Vulkan), so the
script must be run outside the sandbox (e.g. directly from a normal
shell). It does NOT touch the original files on disk — sharpening
happens into a temp directory and is consumed only by the bake.

The downstream bake call uses the proven a92d464 face curve plus the
board-level overlay scale (3.0), matching /leadership exactly.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"

# Anything below this on the long edge gets upscaled by Real-ESRGAN
# before the bake. 800 matches the smallest board source.
SHARPEN_THRESHOLD = 800


def sharpen_sources(src_dir: Path, dest_dir: Path) -> None:
    """Copy every source from ``src_dir`` into ``dest_dir``, running each
    through Real-ESRGAN x4 if its long edge is below SHARPEN_THRESHOLD.

    Lazy import: Real-ESRGAN is only loaded for runs that actually need
    it (we don't want to pay the model-load cost on no-op runs)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    files: list[Path] = []
    for pat in patterns:
        files.extend(src_dir.glob(pat))
    files = sorted(files)

    sr = None  # lazy-init
    for p in files:
        img = Image.open(p).convert("RGB")
        long_edge = max(img.size)
        if long_edge >= SHARPEN_THRESHOLD:
            img.save(dest_dir / (p.stem + ".png"), "PNG")
            print(f"  {p.name}: {img.size} (passthrough)")
            continue

        if sr is None:
            try:
                from realesrgan_ncnn_py import Realesrgan  # type: ignore
            except ImportError as exc:
                raise SystemExit(
                    "realesrgan_ncnn_py not installed. Run "
                    "`.venv-img/bin/pip install realesrgan-ncnn-py` first."
                ) from exc

            # model=4 is realesrgan-x4plus, the general-purpose photo
            # model. Better fit for real human portraits than the anime
            # variants.
            sr = Realesrgan(model=4)

        upscaled = sr.process_pil(img)
        # Keep the model's full 4x output — the bake will downscale to
        # its TARGET_SIZE, and we want the most detail possible going
        # in. PNG handles the resulting size fine.
        upscaled.save(dest_dir / (p.stem + ".png"), "PNG")
        print(f"  {p.name}: {img.size} -> {upscaled.size} (sharpened x4)")


def main() -> None:
    print("Sharpening low-resolution industry sources via Real-ESRGAN x4…")
    with tempfile.TemporaryDirectory(prefix="industry-sharp-") as td:
        staging = Path(td)
        sharpen_sources(SRC_DIR, staging)
        print()

        # Industry sources differ from the board headshots in two ways:
        #
        #   * Bright clothing / full bodies are visible. The board's
        #     aggressive bottom alpha-dissolve (0.85) eats into bright
        #     shirts and leaves an empty bottom; we soften it
        #     dramatically and start later in the frame.
        #   * Even after sharpening, sources may carry directional
        #     lighting (one half of face dim). The board's
        #     `brightness=0.92` plus default shadow curve crushes the
        #     dim half. We ease the curve and lift shadows triangularly.
        #
        # Overlays match /leadership (overlay_scale=3.0) so the two
        # image sets read at the same intensity.
        bake.bake_directory(
            staging,
            OUT_DIR,
            label="industry portraits",
            bottom_dissolve_strength=0.40,
            bottom_dissolve_start=0.78,
            bottom_dissolve_end=1.10,
            bottom_fade_strength=0.10,
            vignette_strength=0.18,
            side_lighting_strength=0.0,
            bw_pre_lift=0.18,
            bw_shadow_curve=1.75,
            bw_highlight_curve=1.55,
            bw_brightness=0.94,
            bw_midtone_power=1.10,
            bw_shadow_floor=0.06,
            overlay_scale=3.0,
            film_grain_amount=2.5,
        )


if __name__ == "__main__":
    main()
