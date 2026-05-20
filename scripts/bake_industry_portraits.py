"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial swarm-style aesthetic as the board portraits.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Pipeline:
  1. Real-ESRGAN x4 pre-sharpen (only sources < 800px on the long edge).
  2. Per-image preprocessing (e.g. tight head crop for construction
     where the source has the subject sitting low and small in frame).
  3. Per-image bake parameter overrides (e.g. extra shadow lift for
     hospitality whose source has a heavily-shadowed left half of
     face) layered on top of the shared a92d464-derived face curve.
  4. Standard bake via bake_board_portraits.process_one with
     overlay_scale=3.0 to match /leadership.

Why the per-image overrides:

The board sources were all shot in the same studio. The industry
sources are pulled from press kits, casual selfies, and stock photos —
each has its own quirks (subject position in frame, lighting
direction). Rather than tune the global bake to handle the worst
offender, we keep the global pipeline consistent with the board look
and apply small targeted overrides per offending image.

Setup notes:
  - Adds dependency: realesrgan-ncnn-py
  - Must run outside the Cursor sandbox to access Metal/Vulkan.
  - bake_board_portraits.py is NEVER modified — /leadership renders
    identically.
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"

SHARPEN_THRESHOLD = 800

# Shared bake kwargs — the a92d464 face curve plus board-level overlay
# intensity. Per-image overrides below layer on top of this.
BASE_BAKE_KWARGS: dict = {
    "bottom_dissolve_strength": 0.40,
    "bottom_dissolve_start": 0.78,
    "bottom_dissolve_end": 1.10,
    "bottom_fade_strength": 0.10,
    "vignette_strength": 0.18,
    "side_lighting_strength": 0.0,
    "bw_pre_lift": 0.18,
    "bw_shadow_curve": 1.75,
    "bw_highlight_curve": 1.55,
    "bw_brightness": 0.94,
    "bw_midtone_power": 1.10,
    "bw_shadow_floor": 0.06,
    "overlay_scale": 3.0,
    "film_grain_amount": 2.5,
}

# Per-image tweaks. Keys with leading underscore are NOT passed to
# process_one — they're consumed by this script's preprocessing.
PER_IMAGE: dict[str, dict] = {
    "industry-construction.png": {
        # The construction source has the subject sitting low and small
        # in frame (a small face in the upper-left of an otherwise empty
        # black field). The bake's head_focused_crop centers on the
        # subject's full-body bbox, leaving lots of empty bottom space
        # and a small face. Pre-cropping to a tight head-and-shoulders
        # frame BEFORE the bake's crop logic runs gets the subject to
        # land at board-equivalent head size in the final 512x512.
        "_pre_crop_tight_head": True,
    },
    "industry-hospitality.png": {
        # Source is heavily side-lit — left half of face in deep
        # shadow. Stronger triangular shadow-lift opens the dim half
        # without blowing out the lit side. Slightly higher overall
        # brightness to match the board face level.
        "bw_pre_lift": 0.32,
        "bw_shadow_floor": 0.10,
        "bw_brightness": 0.98,
    },
}


def sharpen_sources(src_dir: Path, dest_dir: Path) -> None:
    """Copy every source from ``src_dir`` into ``dest_dir``, running each
    through Real-ESRGAN x4 if its long edge is below SHARPEN_THRESHOLD."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    files: list[Path] = []
    for pat in patterns:
        files.extend(src_dir.glob(pat))
    files = sorted(files)

    sr = None
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
                    "`.venv-img/bin/pip install realesrgan-ncnn-py`."
                ) from exc
            sr = Realesrgan(model=4)

        upscaled = sr.process_pil(img)
        upscaled.save(dest_dir / (p.stem + ".png"), "PNG")
        print(f"  {p.name}: {img.size} -> {upscaled.size} (sharpened x4)")


def tight_head_crop(img: Image.Image) -> Image.Image:
    """Pre-crop a source so the head fills most of the frame.

    Used for sources where the subject sits small and low in the
    original (currently only construction). Runs rembg, finds the head
    bbox, centers a square around the head + shoulders so the bake's
    own head_focused_crop has a tight frame to work with.

    Result framing:
      - Square 1:1
      - Head occupies ~50% of frame height
      - Top of head ~12% from top of frame
      - Shoulders visible at the bottom

    Padded with black on whatever side the head sits closest to so the
    head ends up centered.
    """
    rgb = img.convert("RGB")

    # Run rembg on the source so we can find the subject mask.
    buf = io.BytesIO()
    rgb.save(buf, format="PNG")
    session, remove = bake._get_rembg_session()
    cutout_bytes = remove(buf.getvalue(), session=session)
    cutout = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
    alpha = cutout.split()[3]
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.2))

    a = np.asarray(alpha)
    mask = a > 96
    if not mask.any():
        return rgb

    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    top = int(np.argmax(rows))
    bottom = int(len(rows) - 1 - np.argmax(rows[::-1]))
    left = int(np.argmax(cols))
    right = int(len(cols) - 1 - np.argmax(cols[::-1]))

    bbox_h = max(1, bottom - top)
    bbox_w = max(1, right - left)

    # Estimate head width by sampling mask at the top of the subject.
    sample_widths: list[int] = []
    for frac in (0.05, 0.08, 0.11, 0.14, 0.18):
        sy = min(rgb.height - 1, top + int(bbox_h * frac))
        sw = int(mask[sy].sum())
        if sw > 10:
            sample_widths.append(sw)
    head_width = max(sample_widths) if sample_widths else bbox_w // 2

    # Find face center horizontally — sample at the top of the head
    # (around 12% down from top of bbox) and use that row's centroid.
    face_y = min(rgb.height - 1, top + int(bbox_h * 0.10))
    face_row = mask[face_y]
    if face_row.any():
        idx = np.where(face_row)[0]
        face_cx = int((idx[0] + idx[-1]) // 2)
    else:
        face_cx = (left + right) // 2

    # Crop ≈ 2.2x head width: head + clear shoulders/upper chest. The
    # bake's own head_focused_crop runs on this output and lands the
    # final framing at ~2.5x head width like the boards. Slightly
    # tighter than 2.5 so any padding the bake adds doesn't push the
    # head too small in the final 512x512.
    crop_size = int(head_width * 2.2)
    crop_size = max(crop_size, 240)

    # Vertical: head_top sits at 9% from top of crop — pulls the head
    # toward the upper-third like the board photos and exposes more
    # shoulders below.
    crop_top = max(0, top - int(crop_size * 0.09))
    crop_bottom = crop_top + crop_size
    # Horizontal: centered on face center.
    crop_left = face_cx - crop_size // 2
    crop_right = crop_left + crop_size

    # Pad with black on any side that goes out of bounds, then crop.
    pad_top = max(0, -crop_top)
    pad_bottom = max(0, crop_bottom - rgb.height)
    pad_left = max(0, -crop_left)
    pad_right = max(0, crop_right - rgb.width)
    if pad_top or pad_bottom or pad_left or pad_right:
        new = Image.new(
            "RGB",
            (rgb.width + pad_left + pad_right, rgb.height + pad_top + pad_bottom),
            (0, 0, 0),
        )
        new.paste(rgb, (pad_left, pad_top))
        rgb = new
        crop_top += pad_top
        crop_bottom += pad_top
        crop_left += pad_left
        crop_right += pad_left

    return rgb.crop((crop_left, crop_top, crop_right, crop_bottom))


def main() -> None:
    print("Sharpening low-resolution industry sources via Real-ESRGAN x4…")
    with tempfile.TemporaryDirectory(prefix="industry-sharp-") as td:
        staging = Path(td)
        sharpen_sources(SRC_DIR, staging)
        print()

        out_files = sorted(staging.glob("*.png"))
        print(f"Re-baking {len(out_files)} industry portraits from {staging}")
        for src_path in out_files:
            name = src_path.name
            override = PER_IMAGE.get(name, {})

            # Per-image preprocessing (consumes underscore-prefixed keys).
            if override.get("_pre_crop_tight_head"):
                tightened = tight_head_crop(Image.open(src_path))
                tight_path = staging / f"_tight_{name}"
                tightened.save(tight_path, "PNG")
                src_path = tight_path
                print(f"  {name}: tight head pre-crop -> {tightened.size}")

            kwargs = dict(BASE_BAKE_KWARGS)
            for k, v in override.items():
                if not k.startswith("_"):
                    kwargs[k] = v

            out_path = OUT_DIR / name
            bake.process_one(src_path, out_path, **kwargs)
        print("Done.")


if __name__ == "__main__":
    main()
