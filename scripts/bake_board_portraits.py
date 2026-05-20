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

    # Estimate the head width by sampling mask widths at several positions
    # in the very top of the bbox (top 5-18%). For both head-shots (where
    # the head fills the bbox tightly) and full-body shots (where the
    # head sits at the very top of a much taller bbox), this range
    # consistently lands on the head/face rather than on shoulders or
    # torso below. Taking the max of the samples recovers the widest
    # point of the head (cheekbone / forehead) for either layout.
    sample_widths: list[int] = []
    for frac in (0.05, 0.08, 0.11, 0.14, 0.18):
        sy = min(h - 1, top + int(bbox_h * frac))
        sw = int(mask[sy].sum())
        if sw > 10:
            sample_widths.append(sw)
    if sample_widths:
        head_width = max(sample_widths)
    else:
        head_width = bbox_w // 2
    if head_width < 30:
        head_width = bbox_w // 2  # fallback heuristic

    # Crop square ≈ 2.5x head width gives head ~40% of frame width with
    # full shoulders and clear headroom — matches the framing of
    # /leaders/tomas-gorny.png, /leaders/marco-burgarello.png, and
    # /swarm/swarm-04.png. We keep a modest floor of 50% of the source's
    # smaller dimension so that small full-body sources still get a
    # head-focused crop instead of being forced to include the torso.
    crop_size = int(head_width * 2.5)
    crop_size = max(crop_size, int(min(w, h) * 0.50))
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


def to_swarm_bw(
    img: Image.Image,
    *,
    shadow_floor: float = 0.15,
    midtone_power: float = 1.18,
    brightness: float = 0.92,
    shadow_curve: float = 2.00,
    highlight_curve: float = 1.55,
    pre_lift: float = 0.0,
    highlight_lift: float = 0.0,
) -> Image.Image:
    """B&W portrait matching the /swarm/* and /leaders/* studio look: jet-black
    clothing/shadows that blend into the background, deep skin midtones with
    real bone structure (eye sockets, nose bridge, cheekbones, jawline),
    bright but un-clipped highlights.

    The board defaults aim for the slightly-underexposed editorial feel of
    leaders/tomas-gorny.png and board/tracy-conrad.png (rich midtones,
    deep blacks). Lighter values can be passed for sources that already
    start out with one side of the face in deep shadow (e.g. the
    hospitality and insurance industry sources), where the default
    crushes the dim half of the face into pure black instead of holding
    detail.
    """
    g = img.convert("L")
    g = ImageOps.autocontrast(g, cutoff=2)
    arr = np.asarray(g, dtype=np.float32) / 255.0

    # 0. Optional shadow lift (`pre_lift`) — recovers detail in source
    #    images that have one side of the face in deep shadow (e.g. the
    #    hospitality and insurance industry sources). The lift is
    #    triangular: max amount at pure black, zero at mid-grey, zero
    #    above. This avoids fogging up already-dark midtones in
    #    low-contrast sources (construction's dark wall + dark shirt)
    #    that don't actually need their shadows lifted.
    if pre_lift > 0.0:
        arr = arr + pre_lift * np.maximum(0.0, 1.0 - 2.0 * arr)

    # 1. S-curve. The shadow half is steeper than the highlight half so
    #    clothing reads as black while highlights stay un-clipped. The
    #    `shadow_curve` exponent controls how aggressively the shadow
    #    side is crushed — softer values (e.g. 1.6) preserve midtone
    #    detail in the dim half of a directionally-lit face.
    arr = np.where(
        arr < 0.5,
        (arr * 2.0) ** shadow_curve / 2.0,
        1.0 - ((1.0 - arr) * 2.0) ** highlight_curve / 2.0,
    )

    # 2. Hard shadow toe: anything below `shadow_floor` luminance goes to
    #    true black so clothing/shadows blend into the studio bg.
    arr = np.where(arr < shadow_floor, 0.0, (arr - shadow_floor) / (1.0 - shadow_floor))

    # 3. Pull skin tones down — power > 1 darkens midtones more than
    #    extremes, giving skin the rich mid-grey look of swarm-26 instead
    #    of pale. Pass `midtone_power=1.0` to disable.
    if midtone_power != 1.0:
        arr = np.power(arr, midtone_power)

    # 4. Global brightness scale — final touch so the overall plate
    #    matches the editorial feel of the reference photos.
    arr = arr * brightness

    # 5. Optional highlight lift — pushes the brightest tones (anything
    #    above ~0.7 luminance) up toward pure white. Used for the
    #    customer industry portraits where source white shirts appear
    #    grey/dirty after the curve, which makes the subject look
    #    discoloured against the deep-black studio bg.
    if highlight_lift > 0.0:
        t_h = np.clip((arr - 0.65) / 0.35, 0.0, 1.0)
        t_h = t_h * t_h * (3.0 - 2.0 * t_h)  # smoothstep
        arr = arr + highlight_lift * t_h * (1.0 - arr)

    arr = np.clip(arr, 0, 1)
    arr = (arr * 255.0).astype(np.uint8)
    return Image.fromarray(arr)


def apply_halftone(
    img: Image.Image,
    *,
    cell_size: int = 5,
    blend: float = 0.45,
    contrast: float = 1.0,
) -> Image.Image:
    """Apply a halftone dot-screen overlay to a B&W image, matching the
    printed-newsprint look of leaders/tomas-gorny.png and the swarm/* set.

    For each ``cell_size`` × ``cell_size`` cell of the input, a dot is drawn
    whose radius scales with the cell's mean *darkness* (dark cells get
    big dots, bright cells get small dots). The dot pattern is then blended
    on top of the underlying continuous-tone image at ``blend`` strength so
    the face still reads cleanly through the dots — exactly the editorial
    look of the leader/swarm portraits.

    ``contrast`` (>1) amplifies the size variation so highlights pop more.
    """
    arr = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    h, w = arr.shape

    # Local luminance via box-blur over each cell.
    blurred = img.convert("L").filter(ImageFilter.BoxBlur(max(1, cell_size // 2)))
    cell_lum = np.asarray(blurred, dtype=np.float32) / 255.0
    if contrast != 1.0:
        cell_lum = np.clip(0.5 + (cell_lum - 0.5) * contrast, 0.0, 1.0)

    # Distance from each pixel to its cell-center.
    yy, xx = np.mgrid[0:h, 0:w]
    cy = (yy // cell_size) * cell_size + (cell_size - 1) / 2.0
    cx = (xx // cell_size) * cell_size + (cell_size - 1) / 2.0
    dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)

    # Dot radius scales with darkness; the sqrt(2)/2 cap lets adjacent
    # dots just touch at their corners when the local area is fully black.
    radius_max = cell_size / np.sqrt(2.0)
    radius = radius_max * np.power(np.clip(1.0 - cell_lum, 0.0, 1.0), 0.7)
    halftone = np.where(dist <= radius, 0.0, 1.0)  # 0 inside dot, 1 outside

    # Blend the halftone overlay on top of the continuous-tone source so
    # the face/eyes stay legible. blend=1.0 → pure halftone, 0.0 → no effect.
    out = arr * (1.0 - blend) + halftone * blend
    return Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8))


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


def render_editorial_canvas(
    seed: int,
    *,
    overlay_scale: float = 1.0,
) -> Image.Image:
    """Black canvas with very faint pseudo-code and a small constellation
    graph, matching the /swarm/* portraits' background presence: visible
    only when you look closely, never competing with the subject.

    ``overlay_scale`` linearly attenuates every alpha used for code text and
    constellation marks. The default (1.0) reproduces the board portrait
    overlay density used on /leadership; the customer industry baker uses a
    lower value so the overlays read as a faint trace rather than legible
    code, matching swarm-31.png and swarm-34.png.
    """
    rng = random.Random(seed)
    canvas = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    code_font = load_font(10)
    line_h = 13
    code_ink = (130, 140, 156)

    # Pillow's ImageDraw.text/line/ellipse don't honour the alpha channel
    # of the `fill` colour for text glyph rendering — the alpha controls
    # antialiasing only and the RGB is always drawn at full intensity. To
    # get true "very faint" overlays we instead pre-scale the ink colour
    # itself by the requested opacity (0-255) and draw without alpha. The
    # bg is solid black, so an ink of e.g. (18, 19, 21) reads as a dim
    # grey on the canvas.
    def _ink(rgb: tuple[int, int, int], opacity: int) -> tuple[int, int, int]:
        op = max(0, min(255, int(opacity * overlay_scale)))
        return tuple(max(0, min(255, int(c * op / 255))) for c in rgb)

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
            fill=_ink(code_ink, rng.randint(35, 55)),
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
            fill=_ink(code_ink, rng.randint(28, 42)),
        )

    # Sparse constellation graph: small dots with thin connecting lines, kept
    # very dim so they sit behind the portrait rather than next to it.
    n_nodes = 14
    nodes: list[tuple[int, int]] = []
    region_x = (10, int(SIZE * 0.30))
    region_y = (int(SIZE * 0.55), SIZE - 14)
    for _ in range(n_nodes):
        nodes.append((rng.randint(*region_x), rng.randint(*region_y)))
    line_color = _ink((110, 118, 134), 35)
    dot_color = _ink((150, 158, 174), 80)
    label_color = _ink((120, 128, 144), 55)
    for i, (ax, ay) in enumerate(nodes):
        for j in range(i + 1, n_nodes):
            bx, by = nodes[j]
            d = math.hypot(ax - bx, ay - by)
            if d < 80 and rng.random() < 0.4:
                draw.line([(ax, ay), (bx, by)], fill=line_color, width=1)
    label_font = load_font(9)
    for x, y in nodes:
        draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=dot_color)
        if rng.random() < 0.25:
            label = rng.choice(["0x7F4A", "0.91", "n=5"])
            draw.text((x + 4, y - 5), label, font=label_font, fill=label_color)

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


def add_bottom_fade(img: Image.Image, strength: float = 0.50) -> Image.Image:
    """Gently subdue the lower portion of the frame so clothing blends
    naturally into the studio background — matching the smooth,
    stripe-free fade seen in swarm/swarm-22.png and leaders/tomas-gorny.png.

    The fade is a single smooth ramp that extends past the bottom edge,
    so there's no flat 'floor zone' at the bottom of the frame that would
    show up as a horizontal black stripe when the subject has bright
    clothing.
    """
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    yy = np.arange(h, dtype=np.float32)[:, None]
    # End point is set beyond the bottom edge so the fade never plateaus
    # inside the visible frame — the lower edge gets a continuous ramp,
    # not a hard floor.
    start, end = h * 0.42, h * 1.20
    t = np.clip((yy - start) / max(1.0, end - start), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)  # smoothstep
    mask = 1.0 - t * strength
    arr = arr * mask[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode=img.mode)


def process_one(
    path: Path,
    out_path: Path,
    *,
    bottom_dissolve_strength: float = 0.85,
    bottom_dissolve_start: float = 0.62,
    bottom_dissolve_end: float = 1.05,
    bottom_fade_strength: float = 0.22,
    vignette_strength: float = 0.28,
    side_lighting_strength: float = 0.20,
    bw_brightness: float = 0.92,
    bw_midtone_power: float = 1.18,
    bw_shadow_floor: float = 0.15,
    bw_shadow_curve: float = 2.00,
    bw_highlight_curve: float = 1.55,
    bw_pre_lift: float = 0.0,
    bw_highlight_lift: float = 0.0,
    min_source_size: int = 0,
    overlay_scale: float = 1.0,
    film_grain_amount: float = 3.0,
    halftone_blend: float = 0.0,
    halftone_cell: int = 5,
    halftone_contrast: float = 1.0,
) -> None:
    """Bake one portrait to match the /swarm/* editorial style: smooth
    continuous-tone B&W subject on a black studio background with very faint
    code/constellation overlays. No halftone.

    All visual-tuning knobs are exposed as keyword-only arguments so other
    bakers (e.g. customer industry portraits) can tone down the dissolve
    and overlay density when they're processing source photos with bright
    clothing or busy backgrounds, without affecting the canonical board
    look used on /leadership.
    """
    # rembg mask on the full-resolution source for the cleanest cutout.
    src = Image.open(path).convert("RGB")

    # If the source is small (some customer industry sources are only
    # 158-225px on the smaller dimension), upscale it before any
    # processing so the final 512x512 frame doesn't have to magnify
    # 3-5x at the very end and produce a visibly pixelated face.
    # LANCZOS gives the smoothest upscale for portrait detail.
    if min_source_size > 0:
        sw, sh = src.size
        smin = min(sw, sh)
        if smin < min_source_size:
            scale = min_source_size / float(smin)
            new_size = (int(round(sw * scale)), int(round(sh * scale)))
            src = src.resize(new_size, Image.LANCZOS)

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

    # Vertical alpha gradient: dissolve the subject smoothly into the
    # studio background toward the bottom of the frame. Without this the
    # silhouette ends in a hard horizontal edge against the (slightly
    # darker) faded bg, which reads as a visible "dark stripe" — most
    # noticeably for subjects with bright clothing (Bob, Tracy, Stephen).
    # With it, the silhouette dissolves naturally like the references
    # (leaders/tomas-gorny.png, swarm/swarm-22.png).
    alpha_arr = np.asarray(alpha, dtype=np.float32) / 255.0
    yy_a = np.arange(alpha_arr.shape[0], dtype=np.float32)[:, None]
    fade_start_y = SIZE * bottom_dissolve_start
    fade_end_y = SIZE * bottom_dissolve_end
    t_a = np.clip((yy_a - fade_start_y) / max(1.0, fade_end_y - fade_start_y), 0.0, 1.0)
    t_a = t_a * t_a * (3.0 - 2.0 * t_a)  # smoothstep
    alpha_arr = alpha_arr * (1.0 - t_a * bottom_dissolve_strength)
    alpha = Image.fromarray(np.clip(alpha_arr * 255.0, 0, 255).astype(np.uint8), "L")

    # Smooth B&W subject. No halftone, no shadow lift.
    bw = to_swarm_bw(
        src,
        shadow_floor=bw_shadow_floor,
        midtone_power=bw_midtone_power,
        brightness=bw_brightness,
        shadow_curve=bw_shadow_curve,
        highlight_curve=bw_highlight_curve,
        pre_lift=bw_pre_lift,
        highlight_lift=bw_highlight_lift,
    )

    # Optional halftone dot-screen overlay. Matches the
    # printed-newsprint look of the AI-generated leaders/* and
    # swarm/* portraits. ``halftone_blend`` of 0 = continuous tone
    # (board look), ~0.4-0.5 = leaders look (dots clearly visible
    # but face still fully readable through them).
    if halftone_blend > 0.0:
        bw = apply_halftone(
            bw,
            cell_size=halftone_cell,
            blend=halftone_blend,
            contrast=halftone_contrast,
        )

    # Editorial canvas: black with very faint code + constellation.
    seed = sum(ord(c) for c in path.name)
    canvas_grey = render_editorial_canvas(seed, overlay_scale=overlay_scale).convert("L")

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
    final = add_side_lighting(final, side=light_side, strength=side_lighting_strength)
    final = add_vignette(final, strength=vignette_strength)
    final = add_bottom_fade(final, strength=bottom_fade_strength)
    final = add_film_grain(final, amount=film_grain_amount, seed=seed)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, format="PNG", optimize=True)
    print(f"  -> wrote {out_path.relative_to(ROOT)} ({out_path.stat().st_size // 1024} KB)")


def bake_directory(
    src_dir: Path, out_dir: Path, label: str = "portraits", **process_kwargs
) -> None:
    """Bake every image in ``src_dir`` into the output directory using the
    same swarm-style editorial treatment. Used by both this script (board
    portraits) and ``bake_industry_portraits.py`` (customer industry
    portraits). Extra keyword arguments are forwarded to ``process_one``
    so callers can adjust the visual treatment per-baker (e.g. softer
    bottom dissolve and fainter overlays for the industry portraits)."""
    if not src_dir.exists():
        raise SystemExit(f"missing source dir: {src_dir}")
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp")
    files: list[Path] = []
    for pat in patterns:
        files.extend(src_dir.glob(pat))
    files = sorted(files)
    if not files:
        raise SystemExit(f"no images in {src_dir}")
    print(f"Re-baking {len(files)} {label} from {src_dir}")
    for p in files:
        out = out_dir / (p.stem + ".png")
        process_one(p, out, **process_kwargs)
    print("Done.")


def main() -> None:
    # The board portraits target the leaders/* aesthetic — visible code and
    # constellation overlays sitting in the bg so the page reads as
    # editorial-tech, not just a clean studio portrait. We pre-scale the
    # overlay alpha generously so the canvas's intentionally low base
    # alphas (28-80) read as clearly visible after Pillow's RGB-only ink
    # path bottoms out at 100% — matching the look the user has approved.
    bake_directory(SRC_DIR, OUT_DIR, label="board portraits", overlay_scale=3.0)


if __name__ == "__main__":
    main()
