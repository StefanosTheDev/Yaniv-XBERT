"""
Re-bakes /public/assets/images/people/board/*.png so each portrait matches the
editorial halftone treatment baked into /public/assets/images/people/leaders/*.

For each input photo we:
  1. Square-crop on the head/shoulders.
  2. Estimate the (typically light) studio background and softly key it out to
     a black void.
  3. Convert the keyed portrait to high-contrast B&W.
  4. Composite the portrait over a pre-rendered editorial canvas containing a
     pseudo-code block on the right and a constellation network graph on the
     left, both drawn at low opacity in dim grey.
  5. Apply an ordered-dither halftone screen across the whole frame.
  6. Add subtle film grain and a faint vignette.

Originals are read from /scripts/_board_originals/ and the processed PNGs
overwrite the canonical files in /public/assets/images/people/board/.
"""

from __future__ import annotations

import io
import math
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

_rembg_imports_available = True
try:
    pass  # imported lazily inside _get_rembg_session so U2NET_HOME is set first
except Exception:  # pragma: no cover - dependency optional during edits
    _rembg_imports_available = False

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_board_originals"
OUT_DIR = ROOT / "public/assets/images/people/board"
SIZE = 512

# Keep the rembg model cache inside the workspace so the script doesn't need
# write access to the user's home directory (which is sandboxed here).
_U2NET_CACHE = ROOT / ".u2net-cache"
_U2NET_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("U2NET_HOME", str(_U2NET_CACHE))

CODE_LINES = [
    "for step in steps:",
    "    model = 'gpt-4.1'",
    "    top_p = 0.92",
    "    loss.backward()",
    "",
    "def rerank(query):",
    "    h = encode(query)",
    "    scores = w @ h",
    "    return softmax(scores)",
    "",
    "while True:",
    "    batch = next(loader)",
    "    pred = model(batch)",
    "    loss = ce(pred, y)",
    "    loss.backward()",
    "    optim.step()",
    "    sched.step()",
    "",
    "if __name__ == '__main__':",
    "    serve(port=8080)",
    "",
    "# vector index",
    "index.search(q, k=8)",
    "query_emb = embed(q)",
    "top_k = 16",
    "",
    "log.info('latency')",
    "cost = 0.91",
]


def square_crop_head(img: Image.Image) -> Image.Image:
    """Naive fallback square crop — used only when no alpha mask is available."""
    w, h = img.size
    s = min(w, h)
    x = max(0, (w - s) // 2)
    if h >= w:
        y = max(0, int((h - s) * 0.18))
    else:
        y = max(0, (h - s) // 2)
    return img.crop((x, y, x + s, y + s))


def compute_subject_placement(
    src: Image.Image,
    alpha: Image.Image,
    target_head_frac: float = 0.40,
    target_head_top_frac: float = 0.16,
) -> tuple[Image.Image, Image.Image, int, int]:
    """Scale the source + alpha so the subject's *head* occupies a target
    fraction of the canvas width, and return them along with the (x, y) paste
    offsets that put the head at a consistent vertical position.

    This is what gives every portrait the same head-and-shoulders framing
    regardless of how the original was shot — tight head-shot (Tomas) or
    full-torso (Hari). Target framing is calibrated against
    leaders/tomas-gorny.png and leaders/marco-burgarello.png, where the head
    occupies ~40% of frame width with ~16% negative space above the hair.
    """
    w, h = src.size
    a = np.asarray(alpha)
    if a.ndim == 3:
        a = a[..., 0]
    mask = a > 96
    if not mask.any():
        # No mask — fall back to centred fit.
        scale = SIZE / float(min(w, h))
        sw, sh = int(round(w * scale)), int(round(h * scale))
        src_r = src.resize((sw, sh), Image.LANCZOS)
        alpha_r = alpha.resize((sw, sh), Image.LANCZOS)
        return src_r, alpha_r, (SIZE - sw) // 2, (SIZE - sh) // 2

    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    top = int(np.argmax(rows))
    bottom = int(len(rows) - 1 - np.argmax(rows[::-1]))
    left = int(np.argmax(cols))
    right = int(len(cols) - 1 - np.argmax(cols[::-1]))

    bbox_h = max(1, bottom - top)
    bbox_cx = (left + right) // 2

    # Head width sampled at ~28% from the top of the subject bbox (eye line).
    sample_y = min(h - 1, top + int(bbox_h * 0.28))
    head_width = int(mask[sample_y].sum())
    if head_width < 30:
        # Fall back to bbox width (handles weirdly-cropped sources).
        head_width = max(1, right - left) // 2

    # Scale so the head reaches target_head_frac of the canvas width.
    target_px = SIZE * target_head_frac
    scale = target_px / float(head_width)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    src_r = src.resize((new_w, new_h), Image.LANCZOS)
    alpha_r = alpha.resize((new_w, new_h), Image.LANCZOS)

    # Paste so the head sits at a fixed vertical position.
    new_top = int(round(top * scale))
    new_cx = int(round(bbox_cx * scale))
    paste_x = SIZE // 2 - new_cx
    paste_y = int(round(SIZE * target_head_top_frac)) - new_top

    return src_r, alpha_r, paste_x, paste_y


_REMBG_SESSION = None
_REMBG_REMOVE = None


def _get_rembg_session():
    global _REMBG_SESSION, _REMBG_REMOVE
    if _REMBG_SESSION is None:
        # Imported lazily so U2NET_HOME (set above) is in effect when rembg
        # initialises pooch and downloads the model.
        from rembg import new_session, remove as rembg_remove

        _REMBG_REMOVE = rembg_remove
        # u2net_human_seg is tuned for portraits and produces cleaner masks
        # than the default u2net for studio headshots.
        _REMBG_SESSION = new_session("u2net_human_seg")
    return _REMBG_SESSION, _REMBG_REMOVE


def rembg_alpha(img: Image.Image) -> Image.Image:
    """Run rembg on the source portrait and return the resulting alpha channel
    as a single-channel L image (255 = subject, 0 = background)."""
    session, remove = _get_rembg_session()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    out_bytes = remove(buf.getvalue(), session=session)
    cutout = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    alpha = cutout.split()[3]
    # Soft erode + blur for clean fringe.
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.2))
    return alpha


def to_swarm_bw(img: Image.Image) -> Image.Image:
    """B&W base plate. We keep tonal range present (no blown highlights,
    no full crushed blacks on the skin) so the halftone screen applied
    afterwards has gradient to work with — matching the dot variation
    visible in leaders/tomas-gorny.png and leaders/marco-burgarello.png."""
    g = img.convert("L")
    g = ImageOps.autocontrast(g, cutoff=2)
    arr = np.asarray(g, dtype=np.float32) / 255.0

    # Moderate S-curve: shadows crushed enough that clothing reads as black,
    # highlights lifted but never clipped, midtones full of skin shape.
    arr = np.where(
        arr < 0.5,
        (arr * 2.0) ** 1.80 / 2.0,
        1.0 - ((1.0 - arr) * 2.0) ** 1.40 / 2.0,
    )

    # Soft shadow toe: anything below 0.10 → black so dark clothing/hair
    # blend with the background.
    floor = 0.10
    arr = np.where(arr < floor, 0.0, (arr - floor) / (1.0 - floor))

    # Slight midtone darkening for richer skin.
    arr = np.power(arr, 1.10)
    arr = arr * 0.94

    arr = np.clip(arr, 0, 1)
    arr = (arr * 255.0).astype(np.uint8)
    return Image.fromarray(arr)


def add_side_lighting(
    img: Image.Image, side: str = "right", strength: float = 0.18
) -> Image.Image:
    """Subtle horizontal gradient vignette to simulate directional studio
    lighting — darkens one side of the frame more than the other so faces
    feel sculpted instead of evenly lit. Strength is intentionally low so
    it reads as ambience, not a heavy effect."""
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    xx = np.arange(w, dtype=np.float32)[None, :]
    if side == "right":
        t = xx / max(1.0, w - 1)
    else:
        t = (w - 1 - xx) / max(1.0, w - 1)
    t = np.power(t, 1.6)
    mask = 1.0 - t * strength
    mask = np.broadcast_to(mask, (h, w))
    arr = arr * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode=img.mode)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Courier New.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render_editorial_canvas(seed: int) -> Image.Image:
    """Editorial canvas matching the leaders/* halftoned bg: not pure black
    (which would halftone to a flat dense dot field) but a dark grey field
    so the screen produces ~70% density dots, with brighter code +
    constellation overlays that read as lower-density 'open' text after the
    screen is applied."""
    rng = random.Random(seed)
    # Dark grey background — gives halftone a gradient to work with.
    canvas = Image.new("RGB", (SIZE, SIZE), (28, 28, 28))
    draw = ImageDraw.Draw(canvas, "RGBA")

    code_font = load_font(10)
    line_h = 13
    code_ink = (170, 180, 196)

    # Sparse code lines scattered along the right edge.
    code_x = int(SIZE * 0.78)
    for i, line in enumerate(CODE_LINES[:26]):
        y = 12 + i * line_h
        if y > SIZE - 16:
            break
        draw.text(
            (code_x + rng.randint(-1, 1), y),
            line,
            font=code_font,
            fill=(*code_ink, rng.randint(110, 145)),
        )

    # A few faint code lines top-left.
    tl_lines = [
        "import torch",
        "from xb import",
        "  encode(batch)",
    ]
    for i, line in enumerate(tl_lines):
        draw.text(
            (10, 12 + i * line_h),
            line,
            font=code_font,
            fill=(*code_ink, rng.randint(95, 130)),
        )

    # Sparse constellation graph: small dots with thin connecting lines on
    # the left side, brighter than before so they survive the halftone screen.
    n_nodes = 16
    nodes: list[tuple[int, int]] = []
    region_x = (10, int(SIZE * 0.32))
    region_y = (int(SIZE * 0.50), SIZE - 14)
    for _ in range(n_nodes):
        nodes.append((rng.randint(*region_x), rng.randint(*region_y)))
    for i, (ax, ay) in enumerate(nodes):
        for j in range(i + 1, n_nodes):
            bx, by = nodes[j]
            d = math.hypot(ax - bx, ay - by)
            if d < 90 and rng.random() < 0.45:
                draw.line(
                    [(ax, ay), (bx, by)], fill=(150, 160, 178, 95), width=1
                )
    label_font = load_font(9)
    for x, y in nodes:
        draw.ellipse(
            [x - 1, y - 1, x + 1, y + 1],
            fill=(190, 200, 216, 160),
        )
        if rng.random() < 0.30:
            label = rng.choice(["0x7F4A", "0.91", "n=5", "0xB2C1"])
            draw.text(
                (x + 4, y - 5),
                label,
                font=label_font,
                fill=(170, 178, 194, 130),
            )

    return canvas


def true_halftone(
    gray: Image.Image,
    cell_size: int = 3,
    dot_max_factor: float = 1.45,
    edge_softness: float = 0.7,
) -> Image.Image:
    """True halftone dot screen with anti-aliased edges.

    For each cell we compute the average luminance and draw a circular dot
    whose radius scales with darkness (white = no dot, black = full dot),
    matching the look of leaders/* portraits. Soft edge transition keeps tonal
    gradients smooth rather than producing a noisy 1-bit dither.
    """
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    h, w = arr.shape

    ph = (cell_size - h % cell_size) % cell_size
    pw = (cell_size - w % cell_size) % cell_size
    arr_p = np.pad(arr, ((0, ph), (0, pw)), mode="edge")
    H, W = arr_p.shape

    avgs = arr_p.reshape(H // cell_size, cell_size, W // cell_size, cell_size).mean(
        axis=(1, 3)
    )
    avg_per_pixel = np.kron(avgs, np.ones((cell_size, cell_size), dtype=np.float32))

    yy, xx = np.mgrid[0:H, 0:W]
    ly = (yy % cell_size).astype(np.float32)
    lx = (xx % cell_size).astype(np.float32)
    center = (cell_size - 1) / 2.0
    dist = np.sqrt((ly - center) ** 2 + (lx - center) ** 2)

    darkness = 1.0 - avg_per_pixel
    max_r = (cell_size / 2.0) * dot_max_factor
    r = darkness * max_r

    # Soft anti-aliased edge: smooth transition over `edge_softness` pixels.
    inside_amount = np.clip(
        (r - dist + edge_softness / 2.0) / max(edge_softness, 1e-3), 0.0, 1.0
    )
    out = 1.0 - inside_amount  # 1 = white (no dot), 0 = black (inside dot)

    out_u8 = (out[:h, :w] * 255.0).astype(np.uint8)
    return Image.fromarray(out_u8)


def add_film_grain(img: Image.Image, amount: float = 6.0, seed: int = 0) -> Image.Image:
    rng = np.random.default_rng(seed)
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    noise = rng.normal(0.0, amount, arr.shape[:2])
    noise = np.repeat(noise[:, :, None], 3, axis=2)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def add_vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = h / 2.0, w / 2.0
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    d = d / d.max()
    mask = 1.0 - np.clip((d - 0.55) / 0.55, 0, 1) * strength
    arr = arr * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode=img.mode)


def add_bottom_fade(img: Image.Image, strength: float = 0.55) -> Image.Image:
    """Darken the lower portion of the frame so clothing fades into the black
    background, matching the swarm/* studio look where shoulders blend with
    the void rather than reading as a separate silhouette."""
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    yy = np.arange(h, dtype=np.float32)[:, None]
    # Fade kicks in around the lower 40% of the frame and ramps to full
    # darkening at the bottom. Smoothstep transition keeps the boundary
    # invisible.
    start, end = h * 0.55, h * 0.98
    t = np.clip((yy - start) / max(1.0, end - start), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)  # smoothstep
    mask = 1.0 - t * strength
    arr = arr * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode=img.mode)


def process_one(path: Path, out_path: Path) -> None:
    """Bake one board portrait to match the /leaders/* editorial halftone
    treatment: head-and-shoulders B&W subject on a black studio void with
    faint code + constellation overlays, then a uniform halftone dot screen
    applied across the whole frame.

    Subject is rescaled (not just cropped) onto a 512x512 black canvas so the
    head occupies ~40% of the frame width regardless of how tightly the
    original was shot — that's how leaders/tomas-gorny.png is framed.
    """
    src = Image.open(path).convert("RGB")
    full_alpha = rembg_alpha(src)

    # Place the subject on a SIZE x SIZE black canvas with consistent head
    # size and headroom, scaling up or down as needed.
    src_r, alpha_r, paste_x, paste_y = compute_subject_placement(
        src,
        full_alpha,
        target_head_frac=0.46,
        target_head_top_frac=0.15,
    )
    alpha_r = alpha_r.filter(ImageFilter.GaussianBlur(radius=1.2))
    bw = to_swarm_bw(src_r)

    # Editorial canvas: black with very faint code + constellation.
    seed = sum(ord(c) for c in path.name)
    canvas_grey = render_editorial_canvas(seed).convert("L")

    # Composite the subject onto the canvas as a single grayscale plate.
    composite_grey = canvas_grey.copy()
    composite_grey.paste(bw, (paste_x, paste_y), alpha_r)

    # Apply the halftone screen *uniformly* across the entire frame — subject
    # and background alike — exactly the way leaders/tomas-gorny.png renders.
    halftone = true_halftone(
        composite_grey,
        cell_size=3,
        dot_max_factor=1.45,
        edge_softness=0.7,
    )

    # Light vignette + gentle bottom fade so clothing blends into the studio
    # background, subtle side lighting, then a touch of film grain.
    rng = random.Random(seed)
    light_side = rng.choice(["left", "right"])
    final = Image.merge("RGB", (halftone,) * 3)
    final = add_side_lighting(final, side=light_side, strength=0.12)
    final = add_vignette(final, strength=0.18)
    final = add_bottom_fade(final, strength=0.30)
    final = add_film_grain(final, amount=2.5, seed=seed)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, format="PNG", optimize=True)
    print(f"  -> wrote {out_path.relative_to(ROOT)} ({out_path.stat().st_size // 1024} KB)")


def main() -> None:
    if not SRC_DIR.exists():
        raise SystemExit(f"missing source dir: {SRC_DIR}")
    files = sorted(p for p in SRC_DIR.glob("*.png"))
    if not files:
        raise SystemExit(f"no PNGs in {SRC_DIR}")
    print(f"Re-baking {len(files)} board portraits from {SRC_DIR}")
    for p in files:
        out = OUT_DIR / p.name
        process_one(p, out)
    print("Done.")


if __name__ == "__main__":
    main()
