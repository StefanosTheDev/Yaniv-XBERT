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


def head_focused_crop_box(
    alpha: Image.Image, img_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    """Compute a head-and-shoulders square crop box from the rembg alpha mask.

    Sizes the crop relative to the subject's *head width* (sampled at eye
    level via the mask) so framing is consistent regardless of whether the
    source is a tight head-shot (Tomas) or a full-torso photo (Hari).
    Target framing matches /leaders/tomas-gorny.png and /swarm/swarm-04.png:
    head occupies ~40% of the frame width with ~14% headroom and full
    shoulders/upper chest visible at the bottom.
    """
    w, h = img_size
    a = np.asarray(alpha)
    if a.ndim == 3:
        a = a[..., 0]
    mask = a > 96
    if not mask.any():
        s = min(w, h)
        x = max(0, (w - s) // 2)
        y = max(0, int((h - s) * 0.18)) if h >= w else max(0, (h - s) // 2)
        return (x, y, x + s, y + s)

    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    top = int(np.argmax(rows))
    bottom = int(len(rows) - 1 - np.argmax(rows[::-1]))
    left = int(np.argmax(cols))
    right = int(len(cols) - 1 - np.argmax(cols[::-1]))

    bbox_h = max(1, bottom - top)
    bbox_w = max(1, right - left)
    bbox_cx = (left + right) // 2

    # Sample mask width at ~28% from the top of the bbox — that's near the
    # eye line for a typical portrait, well above the shoulder transition.
    sample_y = min(h - 1, top + int(bbox_h * 0.28))
    head_width = int(mask[sample_y].sum())
    if head_width < 30:
        head_width = bbox_w // 2  # fallback heuristic

    # Crop square ≈ 2.5x head width gives head ~40% of frame width with
    # full shoulders and clear headroom — matches the framing of
    # /leaders/tomas-gorny.png, /leaders/marco-burgarello.png, and
    # /swarm/swarm-04.png.
    crop_size = int(head_width * 2.5)
    # Don't go smaller than 70% of the source's smaller dimension — keeps the
    # crop wide even when the source is already a tight head-shot, so the
    # subject doesn't dominate the frame.
    crop_size = max(crop_size, int(min(w, h) * 0.70))
    crop_size = max(crop_size, 64)
    crop_size = min(crop_size, w, h)

    # Horizontal: centred on subject mid.
    crop_left = max(0, bbox_cx - crop_size // 2)
    crop_right = crop_left + crop_size
    if crop_right > w:
        crop_left = w - crop_size
        crop_right = w

    # Vertical: top of head ~11% below the top of the crop. Slightly
    # tighter headroom than the executive team so the lower portion of
    # the frame has plenty of room for the clothing to fade into black.
    head_top_offset = int(crop_size * 0.11)
    crop_top = max(0, top - head_top_offset)
    crop_bottom = crop_top + crop_size
    if crop_bottom > h:
        crop_top = h - crop_size
        crop_bottom = h

    return (crop_left, crop_top, crop_right, crop_bottom)


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
    """B&W portrait matching the /swarm/* and /leaders/* studio look: jet-black
    clothing/shadows that blend into the background, deep skin midtones with
    real bone structure (eye sockets, nose bridge, cheekbones, jawline),
    bright but un-clipped highlights."""
    g = img.convert("L")
    g = ImageOps.autocontrast(g, cutoff=2)
    arr = np.asarray(g, dtype=np.float32) / 255.0

    # 1. Strong S-curve. Shadows crushed harder so clothing reads as black,
    #    highlights kept moderate so skin doesn't blow out.
    arr = np.where(
        arr < 0.5,
        (arr * 2.0) ** 2.00 / 2.0,
        1.0 - ((1.0 - arr) * 2.0) ** 1.55 / 2.0,
    )

    # 2. Hard shadow toe: anything below 0.15 luminance goes to true black.
    floor = 0.15
    arr = np.where(arr < floor, 0.0, (arr - floor) / (1.0 - floor))

    # 3. Pull skin tones down — power > 1 darkens midtones more than extremes,
    #    giving skin the rich mid-grey look of swarm-26 instead of pale.
    arr = np.power(arr, 1.18)

    # 4. Global brightness scale — final touch so the overall plate matches
    #    the slightly-underexposed editorial feel of the reference photos.
    arr = arr * 0.92

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
    """Black canvas with very faint pseudo-code and a small constellation graph,
    matching the /swarm/* portraits' background presence: visible only when
    you look closely, never competing with the subject."""
    rng = random.Random(seed)
    canvas = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")

    code_font = load_font(10)
    line_h = 13
    code_ink = (130, 140, 156)

    # Sparse code lines scattered along the right edge.
    code_x = int(SIZE * 0.82)
    for i, line in enumerate(CODE_LINES[:24]):
        y = 14 + i * line_h
        if y > SIZE - 16:
            break
        draw.text(
            (code_x + rng.randint(-1, 1), y),
            line,
            font=code_font,
            fill=(*code_ink, rng.randint(35, 55)),
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
            fill=(*code_ink, rng.randint(28, 42)),
        )

    # Sparse constellation graph: small dots with thin connecting lines, kept
    # very dim so they sit behind the portrait rather than next to it.
    n_nodes = 14
    nodes: list[tuple[int, int]] = []
    region_x = (10, int(SIZE * 0.30))
    region_y = (int(SIZE * 0.55), SIZE - 14)
    for _ in range(n_nodes):
        nodes.append((rng.randint(*region_x), rng.randint(*region_y)))
    for i, (ax, ay) in enumerate(nodes):
        for j in range(i + 1, n_nodes):
            bx, by = nodes[j]
            d = math.hypot(ax - bx, ay - by)
            if d < 80 and rng.random() < 0.4:
                draw.line(
                    [(ax, ay), (bx, by)], fill=(110, 118, 134, 35), width=1
                )
    label_font = load_font(9)
    for x, y in nodes:
        draw.ellipse(
            [x - 1, y - 1, x + 1, y + 1],
            fill=(150, 158, 174, 80),
        )
        if rng.random() < 0.25:
            label = rng.choice(["0x7F4A", "0.91", "n=5"])
            draw.text(
                (x + 4, y - 5),
                label,
                font=label_font,
                fill=(120, 128, 144, 55),
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


def add_bottom_fade(
    img: Image.Image, strength: float = 0.65, floor: float = 0.18
) -> Image.Image:
    """Subdue the lower portion of the frame so clothing blends into the
    studio background, but leave a touch of dark-grey tonality and a
    visible floor so editorial overlays (code text, constellation graph)
    stay legible — matching the way leaders/tomas-gorny.png keeps its
    shirt and 'while True:' code readable rather than dropping to a flat
    black void.

    Mask never multiplies below `floor`, so even at the very bottom of
    the frame there is still ~18% of the original luminance preserved.
    """
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    yy = np.arange(h, dtype=np.float32)[:, None]
    start, end = h * 0.50, h * 0.92
    t = np.clip((yy - start) / max(1.0, end - start), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)  # smoothstep
    mask = 1.0 - t * strength
    mask = np.maximum(mask, floor)
    arr = arr * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode=img.mode)


def process_one(path: Path, out_path: Path) -> None:
    """Bake one board portrait to match the /swarm/* editorial style: smooth
    continuous-tone B&W subject on a black studio background with very faint
    code/constellation overlays. No halftone."""
    # rembg mask on the full-resolution source for the cleanest cutout.
    src = Image.open(path).convert("RGB")
    full_alpha = rembg_alpha(src)

    # The board source photos vary wildly: some arrive as tight head-shots
    # (~330x360, head fills the frame) while others are wide torso-and-up
    # shots (Hari at 800x800). To produce consistent executive-team framing
    # — head occupying ~40% of the frame width with full shoulders and clear
    # headroom — we pad the source with black up to the size the
    # head_focused_crop_box function actually needs (~3x the detected head
    # width). Tight head-shots get a lot of padding; wider sources get
    # little or none.
    a = np.asarray(full_alpha)
    if a.ndim == 3:
        a = a[..., 0]
    head_mask = a > 96
    if head_mask.any():
        rows = np.any(head_mask, axis=1)
        cols = np.any(head_mask, axis=0)
        bbox_top = int(np.argmax(rows))
        bbox_bot = int(len(rows) - 1 - np.argmax(rows[::-1]))
        sample_y = min(a.shape[0] - 1, bbox_top + int((bbox_bot - bbox_top) * 0.28))
        sampled = int(head_mask[sample_y].sum())
        bbox_w = int(cols.sum())
        head_w_est = max(sampled, bbox_w // 2, 30)
    else:
        head_w_est = min(src.size) // 3
    target = int(head_w_est * 3.0)
    src_w, src_h = src.size
    pad_w = max(0, (target - src_w) // 2)
    pad_h = max(0, (target - src_h) // 2)
    if pad_w or pad_h:
        padded = Image.new("RGB", (src_w + 2 * pad_w, src_h + 2 * pad_h), (0, 0, 0))
        padded.paste(src, (pad_w, pad_h))
        padded_alpha = Image.new("L", padded.size, 0)
        padded_alpha.paste(full_alpha, (pad_w, pad_h))
        src = padded
        full_alpha = padded_alpha

    # Head-focused square crop driven by the subject mask so every portrait
    # gets the same head-and-shoulders framing regardless of how the source
    # photo was shot.
    box = head_focused_crop_box(full_alpha, src.size)
    src = src.crop(box).resize((SIZE, SIZE), Image.LANCZOS)
    alpha = full_alpha.crop(box).resize((SIZE, SIZE), Image.LANCZOS)
    # Light feather so the silhouette stays crisp like the swarm/* portraits
    # while still blending into the black background without a hard cutout.
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.2))

    # Smooth B&W subject. No halftone, no shadow lift.
    bw = to_swarm_bw(src)

    # Editorial canvas: black with very faint code + constellation.
    seed = sum(ord(c) for c in path.name)
    canvas_grey = render_editorial_canvas(seed).convert("L")

    # Composite the subject onto the canvas as a single grayscale plate.
    composite_grey = canvas_grey.copy()
    composite_grey.paste(bw, (0, 0), alpha)

    # Soft vignette + bottom fade so clothing blends into the studio black,
    # subtle side lighting for sculpted faces, then a touch of film grain.
    # Side alternates per portrait so the page has visual variety like
    # /swarm/* photos rather than every face lit identically.
    rng = random.Random(seed)
    light_side = rng.choice(["left", "right"])
    final = Image.merge("RGB", (composite_grey,) * 3)
    final = add_side_lighting(final, side=light_side, strength=0.20)
    final = add_vignette(final, strength=0.28)
    final = add_bottom_fade(final, strength=0.65, floor=0.18)
    final = add_film_grain(final, amount=3.0, seed=seed)

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
