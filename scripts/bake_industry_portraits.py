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
    # Industry sources differ from the board headshots in two ways that
    # require softer settings for a swarm-31 / swarm-34 / leaders look:
    #
    #   * The subjects often wear bright clothing (white shirts, light
    #     jackets) and full bodies are visible. The board's aggressive
    #     bottom alpha-dissolve (0.85) eats into bright shirts and leaves
    #     an empty bottom; we soften it dramatically and start the
    #     dissolve later in the frame so clothing stays visible to the
    #     edge.
    #   * Some sources are already shot against dark walls or dim
    #     environments, so the board's `brightness=0.92` global scale
    #     crushes them into the background. We lift the brightness and
    #     ease the midtone curve to keep skin tones legible.
    #
    # The overlay scale is also lowered so the code/constellation reads as
    # a faint trace rather than legible code, matching swarm-31.png and
    # swarm-34.png which are the only members of the page that the user
    # has already approved at rest.
    bake.bake_directory(
        SRC_DIR,
        OUT_DIR,
        label="industry portraits",
        bottom_dissolve_strength=0.40,
        bottom_dissolve_start=0.78,
        bottom_dissolve_end=1.10,
        bottom_fade_strength=0.10,
        vignette_strength=0.18,
        # The customer industry source photos already carry natural
        # directional studio lighting (the hospitality and insurance
        # subjects in particular have one side of the face in shadow in
        # the original); adding a synthetic side-light on top would
        # crush the dim half to black. Disable it.
        side_lighting_strength=0.0,
        # Move closer to the board look (deeper blacks, sharper
        # bone-structure midtones, the look of board/karen-walker.png
        # and board/hari.png) while keeping a small shadow-lift so
        # the dim half of the hospitality face still holds. The big
        # change vs the previous bake is restoring contrast: we use
        # a near-board shadow curve (1.95) and shadow floor (0.10)
        # so the construction portrait — whose source is
        # low-contrast and was reading as a washed-out fog — now
        # has real blacks and sharper face shape.
        #
        # The triangular pre_lift is kept small (0.10) so it lifts
        # only the deepest shadows on the dim half of a directional
        # face without flattening already-low-contrast sources.
        #
        # highlight_lift is bumped to 0.35 to push the brightest
        # tones (white shirts on insurance, healthcare, real-estate)
        # cleanly to white against the deep-black bg, so they no
        # longer read as a discoloured grey patch.
        #
        # min_source_size=500 pre-upscales the smallest sources
        # (183-225px) before any cropping so the final 512x512
        # frame doesn't have to magnify ~3x and produce a pixelated
        # face on construction.
        bw_pre_lift=0.10,
        bw_shadow_curve=1.95,
        bw_highlight_curve=1.55,
        # Lower the highlight-lift threshold so the smoothstep
        # reaches into the upper midtones (everything above ~0.50
        # luminance), enough to flatten the fold/wrinkle shadows in
        # insurance's white t-shirt while still leaving skin
        # midtones (typically below 0.50 on the shadow side of a
        # face) untouched.
        bw_highlight_lift=0.55,
        bw_highlight_lift_threshold=0.50,
        bw_brightness=0.95,
        bw_midtone_power=1.15,
        bw_shadow_floor=0.10,
        min_source_size=500,
        # Industry sources have noisier rembg masks than the board
        # studio shots: small selfies (insurance) leak hedge/wall
        # pixels into the subject's t-shirt area, and dark hair on a
        # dim wall (construction) leaves a bright halo around the
        # head. Extra erosion passes pull the mask in a few pixels
        # so those edge-pixel artefacts are dropped, then the
        # Gaussian re-softens the boundary so the cutout still
        # blends cleanly into the bg.
        mask_extra_erode=2,
        overlay_scale=0.18,
        film_grain_amount=2.5,
    )


if __name__ == "__main__":
    main()
