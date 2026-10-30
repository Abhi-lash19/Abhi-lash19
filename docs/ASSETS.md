# Artwork and asset maintenance

The reference sets the navy, mint, cyan and violet direction. The supplied images are the artwork source; no new AI artwork was generated for this revision.

## Source and generated files

- `assets/source/`: all 13 user-supplied JPGs, copied byte for byte from `C:\middlware-workstation`. Original filenames and complete images are preserved. `data/artwork.json` records SHA-256 hashes, dimensions, sizes and the one explicit letterbox crop.
- `assets/art/selected/`: optimized versions for embedding. Total JPEG size fell from 3,095,577 to 1,018,255 bytes (67.1%). Aspect ratios are preserved. Only HERO's existing top/bottom letterbox bars are removed from the optimized derivative; its full original remains available.
- `assets/art/footer.jpg`: the existing mountain artwork, unchanged.
- `assets/hero*.svg`, `mindset*.svg`, `workflow*.svg`, `footer*.svg`: desktop/mobile compositions. The mindset mountains, moon and lightbulb are hand-built vector shapes.
- `assets/projects/`: six horizontal desktop featured cards with 45% artwork, six compact secondary cards, and dedicated mobile compositions for all twelve projects. Every project uses its corresponding supplied JPG. SVG clipping preserves image proportions. Private cards have neither repository links nor exploration arrows.
- `assets/social/`: four separately linked contact assets. Destinations are preserved from the existing README.
- `assets/icons/`: existing Devicon v2.17.0 assets and MIT license. Brand trademarks remain with their owners. No remote icon service is required. Social glyphs and workflow icons are local vector paths.
- `assets/tech/`: four distinct panels plus desktop and mobile arrangements. Python and PostgreSQL appear only once. The 14 distinct labels determine the Languages / Tools summary value.
- `assets/stats/`: four summary cards, responsive arrangements, and two charts. Their source is the existing public API snapshot plus explicitly defined editorial/configuration counts.
- `assets/source/contribution-snake.svg`: genuine Platane/snk output from commit `d50b1c0`, dated 2026-10-28. This is the reproducible input for local previews, not a live contribution calendar.
- `assets/snake.svg` and `snake-static.svg`: local animated/static versions of that recorded calendar. The README points to the daily output-branch animation, not the bundled snapshot.

The prior placeholder portrait, superseded project paintings and unused chart presentation panels were removed after reviewing the new compositions. They remain recoverable from Git history. All supplied originals and the existing footer are retained.

## Rebuild

```sh
python scripts/build_profile.py
python scripts/prepare_snake.py
python scripts/validate_profile.py
python -m unittest discover -s tests
```

Python's standard library is enough for generation and validation. Edit `data/projects.json` for reviewed project prose/stacks and `scripts/build_profile.py` for layout. Do not edit generated SVGs or README markup alone. `--stats-only` also refreshes README alt text and date links to keep them consistent with the charts.

For a repeat import from the preserved originals, use `node scripts/prepare_art.cjs`. To import from another folder, pass its path. Sharp is required only for this import; the script fails before writing anything if any of the 13 expected files is absent. Normal builds use the committed optimized files.

## Snake behavior

The existing daily Platane/snk action still collects real contribution data. The Python postprocessor leaves every calendar cell, activity keyframe and original movement keyframe intact. A symmetric 45ms time filter rounds the drawn skin's corners within four pixels of that real route. Dense samples make a continuous-looking tapered body, while the head rotates along its direction of travel. Mint shading and a restrained glow add depth. Calendar timing remains unchanged; this is a stylized grid-following snake, not the reference's photorealistic free-form serpent.

The postprocessor fails on unexpected input geometry or repeated processing before publication. No contribution activity is synthesized. The workflow publishes both animated and standalone static outputs while retaining other files on the shared `output` branch. The README displays just one primary snake.

A reduced-motion `<picture>` source selects `#reduced-motion` on the same live SVG. Its `:target` style freezes the actual calendar and hides the skin; an internal media query also supports direct SVG viewing. This avoids depending on a new, initially missing remote filename. The new style takes effect after the updated workflow first runs.

## GitHub and accessibility

GitHub controls native heading margins, the surrounding theme and image sizing. No README CSS, JavaScript, React, filters or interactive controls are required. Dark panels remain dark on light GitHub. Two featured columns and three secondary columns wrap naturally; the hero, mindset, workflow, stats and technology arrangements use mobile sources.

Body text, typography and rounded framing inside SVGs cannot be selected as native text. Every README image has descriptive alt text, including project descriptions, privacy labels and stacks. Chart values and definitions are also available as ordinary linked JSON/Markdown. Native public repository anchors remain usable with image loading disabled. There are no duplicate expandable project descriptions; earlier Learning Lab links are retained once in a compact disclosure.

The supplied hero differs from the reference image, including its existing neon lettering. It is preserved as supplied. No invented portrait likeness, synthetic chart, sample repository count or unverified technology stack was copied from the reference.
