# Artwork and asset maintenance

The reference was used for visual direction: midnight navy, mint/cyan/lilac accents, cinematic environments, illuminated cards, compact charts, and a matching footer. None of its sample metrics or incorrect project descriptions were copied.

## Sources

- `assets/art/`: eight original AI-generated concept illustrations, optimized to JPEG and committed as reusable source artwork. These are not screenshots, deployed interfaces, or portraits of the owner. The user requested this artwork for the profile.
- `assets/hero.svg`, `hero-mobile.svg`, `footer.svg`: self-contained SVG compositions with embedded local JPEG data, vector typography, and decorative framing.
- `assets/projects/`: twelve independently linked card assets. Six use concept paintings; six use vector motifs. They are separate components rather than a screenshot of the README. All card descriptions also appear as selectable native Markdown inside expandable sections, and complete descriptions are supplied in image alt text.
- `assets/portrait-placeholder.svg`: a generic neutral silhouette, because no authorized portrait was present in the profile repository or its Git history. Replacing this source with an authorized image and rebuilding updates the banner. No account avatar was modified.
- `assets/icons/`: Devicon v2.17.0 icons, distributed under the included MIT license. Brand trademarks remain with their owners. The download script records the exact source paths; the README does not depend on a third-party badge service.
- `assets/stats/`: deterministic SVG charts from the committed API snapshot. See METRICS.md.
- `assets/snake.svg`: the existing animated output asset from `origin/output` commit `d50b1c0`, dated 2026-10-28. Only palette variables and an opaque background were changed. Original grid cells and movement keyframes are preserved.
- `assets/snake-static.svg`: the same captured grid with animation disabled, selected for reduced-motion preferences. This snapshot does not automatically refresh.

## Rebuild

```sh
python scripts/build_profile.py
python scripts/validate_profile.py
python -m unittest discover -s tests
```

The rebuild uses only Python's standard library and the committed sources. No image-generation API, Node package, font download, or private credentials are needed. System font fallbacks are Segoe UI and Arial. `data/projects.json` is the editable content source; edit prose/layout in `scripts/build_profile.py`, not the generated README.

`scripts/prepare_art.cjs` is the optional one-time import/optimization utility. It uses Sharp and the generated filenames from this task. It is **not** part of a normal rebuild; the optimized source paintings are already committed. `scripts/prepare_snake.py` can refresh the bundled snapshot from a freshly fetched `origin/output` branch. It preserves the actual contribution data; it never synthesizes a heatmap.

## Generation specification

Shared project-card direction: premium cinematic conceptual illustration, landscape 3:2, midnight navy, detailed editorial art, atmospheric lighting, no numeric data, interface claims, logos, or text. Card typography is generated separately in SVG.

| Source | Subject and palette |
| --- | --- |
| Hero | Night-time developer studio, anonymous person seen from behind, twin monitors, city window, moonlight, plants, amber lamp; dark left-side negative space; mint/cyan/blue. |
| BountyDesk | Violet compass, magnifying glass, and ticket-like artifacts on an explorer's desk: discovery and evaluation. |
| Chitragupta | Emerald luminous book in a library with connected floating paper leaves: knowledge and research. |
| Renzo | Blue astrolabe, documents, and a distant doorway: career direction. |
| ScribeAI | Cyan fountain pen drawing a light ribbon across paper: creative writing. |
| CoreGPT | Violet/blue layered glass network sculpture: transformer building blocks, not a literal architecture diagram. |
| GitInsight Engine | Cyan crystal observatory and a constellation of connected points: exploring repository data. |
| Footer | Moonlit mountain valley, stars, pine silhouettes, and an anonymous seated figure viewed from behind; blue-purple with a warm distant horizon. |

The committed paintings make layout builds reproducible. Re-running a generative model from the prompt would produce a new interpretation, not a byte-identical image.

## GitHub compromises

GitHub controls the surrounding page, native heading typography, spacing, and theme. The dark illustrated components remain dark on light GitHub; surrounding selectable prose follows GitHub's theme. No page-level CSS or JavaScript is included in README markup.

Rounded cards and custom typography live inside individual SVG images. Consequently their visible text cannot be selected directly in an image; the adjacent expandable descriptions supply selectable equivalents. Every card is a separate repository link. Native text is used for the introduction, mindset, workflow, Learning Lab, source links, and contact links.

Fixed intrinsic card widths with GitHub's normal max-width behavior allow cards to wrap from two columns to one. The hero also uses a mobile-specific source through `<picture>`. No unsupported flex/grid/hover CSS is needed. Dark cards have opaque backgrounds for light-theme contrast.

The live snake still points at the existing output URL. Its new palette takes effect only after the reviewed workflow runs. The local preview uses the recolored bundled animation to show the intended result. The fallback is available in an expandable section rather than an unsupported JavaScript image-error handler.
