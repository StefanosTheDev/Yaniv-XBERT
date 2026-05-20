"""
Bakes the customer industry portraits used on /our-customers-preview into
the same editorial swarm-style aesthetic that the board portraits and
public/assets/images/people/swarm/* photos use:

    smooth continuous-tone B&W subject + black studio background +
    head-and-shoulders crop + prominent code/constellation overlays +
    alpha dissolve at the bottom so the silhouette blends into the void.

Originals live in /scripts/_industry_originals/. Outputs overwrite the
canonical paths under /public/assets/images/customers/industry-*.png.

Reuses the proven processing pipeline from bake_board_portraits.py via
its `bake_directory` helper so the two image sets stay visually
consistent.

Tuning history note:

The cleanest face we ever produced for the industry sources was the
a92d464 commit — gentler shadow curves, mild triangular shadow-lift,
slightly brighter midtones than the default board pipeline. That
version's only weakness was very faint overlays (overlay_scale=0.18)
which didn't read on /our-customers-preview at the same level as the
board photos. This file reinstates those face params verbatim and
swaps the overlay scale up to 3.0 to match /leadership.

We deliberately do NOT pre-stage the sources through an even-lighting
pass — when we tried that, it brightened the overall face but added a
hazy/grainy feel that pushed us further away from the bright clean
look the user remembered as "very close".
"""

from __future__ import annotations

from pathlib import Path

import bake_board_portraits as bake


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "scripts/_industry_originals"
OUT_DIR = ROOT / "public/assets/images/customers"


def main() -> None:
    # Industry sources differ from the board headshots in two ways that
    # required softer settings to land on a clean face:
    #
    #   * The subjects often wear bright clothing (white shirts, light
    #     jackets) and full bodies are visible. The board's aggressive
    #     bottom alpha-dissolve (0.85) eats into bright shirts and
    #     leaves an empty bottom; we soften it dramatically and start
    #     the dissolve later in the frame so clothing stays visible to
    #     the edge.
    #   * Some sources are already shot against dark walls or dim
    #     environments, so the board's `brightness=0.92` global scale
    #     crushes them into the background. We lift the brightness a
    #     touch and ease the midtone curve to keep skin tones legible.
    #
    # Everything else (overlays, framing, dissolve mechanics) follows
    # the board pipeline exactly — overlay_scale=3.0 is the same value
    # bake_board_portraits.py main() uses, so /leadership and
    # /our-customers-preview read at the same overlay intensity.
    bake.bake_directory(
        SRC_DIR,
        OUT_DIR,
        label="industry portraits",
        # Softer dissolve so bright shirts (insurance, healthcare,
        # real-estate) stay visible to the bottom edge instead of
        # being eaten by alpha.
        bottom_dissolve_strength=0.40,
        bottom_dissolve_start=0.78,
        bottom_dissolve_end=1.10,
        bottom_fade_strength=0.10,
        vignette_strength=0.18,
        # Industry sources already carry natural directional studio
        # lighting (hospitality and insurance in particular have one
        # side of the face in shadow). Adding a synthetic side-light
        # on top would crush the dim half to black.
        side_lighting_strength=0.0,
        # Gentler shadow curve and a triangular shadow-lift so the
        # dim half of directionally-lit source faces (hospitality,
        # insurance, healthcare) holds detail instead of crushing to
        # black. Triangular lift only touches values below 0.5 so
        # already-dark midtones in low-contrast sources (construction)
        # are left alone and don't fog up.
        bw_pre_lift=0.18,
        bw_shadow_curve=1.75,
        bw_highlight_curve=1.55,
        bw_brightness=0.94,
        bw_midtone_power=1.10,
        bw_shadow_floor=0.06,
        # Match the board's overlay intensity exactly so the two
        # image sets read at the same level on the page.
        overlay_scale=3.0,
        film_grain_amount=2.5,
    )


if __name__ == "__main__":
    main()
