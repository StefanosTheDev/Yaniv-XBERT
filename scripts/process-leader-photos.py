#!/usr/bin/env python3
"""
Process leadership portraits into the homepage's editorial B&W style.

NOTE: The portraits currently shipping under
public/assets/images/people/leaders/ are AI-generated (not the output of
this script) so they more closely match the hand-crafted look of
public/assets/images/people/person-01.png. This script is kept as a
reproducible, deterministic fallback in case we need to regenerate from
the source photos without an image model in the loop, or to onboard
additional leaders quickly.

Mirrors the look of public/assets/images/people/person-01.png at a
"clean B&W with vignette and accent bar" level (no halftone, no code-text
overlay, no glitch bands):
  - tight square head-and-shoulders crop
  - heavy grayscale + crushed blacks (S-curve)
  - radial vignette darkening the background to near-black
  - fine film grain
  - tiny brand-orange accent bar in the bottom-right corner

Inputs are the user-supplied source photos cached under the workspace
.cursor projects assets folder; outputs are written into the Next.js
public/ tree so they ship with the build.

Idempotent: re-running overwrites the outputs in place. Tweak the tuning
constants near the top to iterate on the look without touching markup.
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageOps


OUTPUT_SIZE = 512
ACCENT_RGB = (230, 106, 44)  # ~ #E66A2C, matches the orange accent bar
ACCENT_HEIGHT_PX = 6
ACCENT_WIDTH_FRAC = 0.30
GRAIN_BLEND = 0.12
VIGNETTE_STRENGTH = 0.85
CONTRAST_BOOST = 1.18
BRIGHTNESS_TRIM = 0.92
RANDOM_SEED = 20260515  # deterministic grain across runs


@dataclass(frozen=True)
class Job:
    src: Path
    dst: Path
    # Vertical bias for the square crop, 0.0 = top, 0.5 = center, 1.0 = bottom.
    # Faces tend to sit in the upper half so we lean upward by default.
    crop_bias_y: float = 0.4


def square_crop(img: Image.Image, bias_y: float) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    if w >= h:
        left = (w - side) // 2
        top = 0
    else:
        left = 0
        # Bias the crop window toward the top so we keep the face, not the chest.
        max_top = h - side
        top = int(max_top * bias_y)
    return img.crop((left, top, left + side, top + side))


def s_curve_lut() -> list[int]:
    """Custom contrast curve: crush blacks, gently lift highlights."""
    points = [(0, 0), (40, 12), (90, 60), (140, 150), (200, 220), (255, 255)]
    lut: list[int] = []
    for i in range(256):
        for j in range(len(points) - 1):
            x0, y0 = points[j]
            x1, y1 = points[j + 1]
            if x0 <= i <= x1:
                t = 0.0 if x1 == x0 else (i - x0) / (x1 - x0)
                lut.append(int(round(y0 + (y1 - y0) * t)))
                break
    return lut


def radial_vignette_mask(size: int, strength: float) -> Image.Image:
    """Build an L-mode mask: bright in the center, dark at the corners."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    center = size / 2
    max_r = (size / 2) * 1.42  # corner distance
    steps = 64
    for i in range(steps, 0, -1):
        r = max_r * (i / steps)
        # Inner pixels stay bright (255); outer pixels fall off.
        falloff = 1.0 - (i / steps) ** 2
        value = int(round(255 * (1.0 - strength * (1.0 - falloff))))
        bbox = (center - r, center - r, center + r, center + r)
        draw.ellipse(bbox, fill=value)
    return mask


def grain_layer(size: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    pixel_count = size * size
    raw = bytes(rng.randint(80, 200) for _ in range(pixel_count))
    layer_l = Image.frombytes("L", (size, size), raw)
    return Image.merge("RGB", (layer_l, layer_l, layer_l))


def add_accent_bar(img: Image.Image) -> Image.Image:
    w, h = img.size
    bar_w = int(w * ACCENT_WIDTH_FRAC)
    bar_h = ACCENT_HEIGHT_PX
    margin = max(4, int(h * 0.018))
    x1 = w - margin
    y1 = h - margin
    x0 = x1 - bar_w
    y0 = y1 - bar_h
    out = img.copy()
    ImageDraw.Draw(out).rectangle((x0, y0, x1, y1), fill=ACCENT_RGB)
    return out


def process(job: Job) -> None:
    if not job.src.exists():
        raise FileNotFoundError(f"source not found: {job.src}")

    img = Image.open(job.src).convert("RGB")
    img = ImageOps.exif_transpose(img)

    img = square_crop(img, job.crop_bias_y)
    img = img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)

    gray = ImageOps.grayscale(img)
    gray = gray.point(s_curve_lut())
    gray = ImageEnhance.Contrast(gray).enhance(CONTRAST_BOOST)
    gray = ImageEnhance.Brightness(gray).enhance(BRIGHTNESS_TRIM)

    rgb = Image.merge("RGB", (gray, gray, gray))

    vignette = radial_vignette_mask(OUTPUT_SIZE, VIGNETTE_STRENGTH)
    vignette_rgb = Image.merge("RGB", (vignette, vignette, vignette))
    rgb = ImageChops.multiply(rgb, vignette_rgb)

    grain = grain_layer(OUTPUT_SIZE, RANDOM_SEED + hash(job.dst.name) % 1000)
    rgb = Image.blend(rgb, grain, GRAIN_BLEND)

    rgb = add_accent_bar(rgb)

    job.dst.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(job.dst, "PNG", optimize=True)
    print(f"wrote {job.dst}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_root = Path(
        os.environ.get(
            "LEADER_PHOTO_SRC",
            "/Users/yanivmasjedi/.cursor/projects/Users-yanivmasjedi-Desktop-XBert-Project/assets",
        )
    )
    dst_root = repo_root / "public" / "assets" / "images" / "people" / "leaders"

    jobs = [
        Job(
            src=src_root / "image-fa60f667-ef22-41f5-aa9b-9cbd50fb41b3.png",
            dst=dst_root / "tomas-gorny.png",
            crop_bias_y=0.0,
        ),
        Job(
            src=src_root / "image-9b99ab39-bbd2-42b7-946f-05b5abf4a683.png",
            dst=dst_root / "ran-ezerzer.png",
            crop_bias_y=0.0,
        ),
        Job(
            src=src_root / "image-da76843c-dc3a-47e4-a5e3-9feb117e8fec.png",
            dst=dst_root / "marco-burgarello.png",
            crop_bias_y=0.0,
        ),
    ]

    for job in jobs:
        process(job)

    return 0


if __name__ == "__main__":
    sys.exit(main())
