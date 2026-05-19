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
        # Gentler shadow curve, a triangular shadow-lift, and a
        # smoothstep highlight lift so:
        #   * the dim half of directionally-lit source faces
        #     (hospitality, insurance, healthcare) holds detail and
        #     reads as evenly-lit like swarm-31, instead of crushing
        #     to pure black;
        #   * white shirts/highlights (insurance especially) clip to
        #     a clean white instead of the dirty-grey the unlifted
        #     curve produces against the deep-black studio bg;
        #   * already-dark midtones in low-contrast sources
        #     (construction) are left alone — the triangular shadow-
        #     lift is zero above 0.5 luminance so it doesn't fog them.
        bw_pre_lift=0.30,
        bw_shadow_curve=1.65,
        bw_highlight_curve=1.30,
        bw_highlight_lift=0.40,
        bw_brightness=0.96,
        bw_midtone_power=1.05,
        bw_shadow_floor=0.05,
        # Source photos in scripts/_industry_originals/ are between
        # 158x196 (real-estate) and 1024x798 (healthcare). Pre-upscale
        # any source whose smaller dimension is under 600px so the
        # final 512x512 crop never has to magnify more than ~1.5x at
        # the end — eliminates the visible pixelation on construction.
        min_source_size=600,
        overlay_scale=0.18,
        film_grain_amount=2.5,
    )


if __name__ == "__main__":
    main()
