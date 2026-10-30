# Focused cinematic refinement

Refined the existing implementation on `codex/final-cinematic-readme`. No commit, push or merge was performed.

## Changes

- Featured cards now devote 45% of their desktop width to artwork (previously about 37%). Increased card height and content spacing accommodate larger titles, labels and technology tags without removing project facts.
- Kept two featured columns and three secondary columns on desktop. Secondary artwork is slightly taller, with stronger title/body type.
- Added mobile variants for all six secondary projects so they fill the mobile content width instead of staying at 276px. Featured mobile descriptions use 24-unit type and tags use 21-unit type, approximately 13px and 11.5px at a 360px viewport.
- Mobile summary labels now wrap deliberately over two readable lines. Increased mobile technology labels to approximately 12.3px at 360px. Used consistent, compact native Markdown section headings instead of mixed emoji treatments.
- The snake now has a shaded directional head, densely overlapping tapered body, restrained glow and rounded turns. New visual keyframes are derived from the original timed route and stay within four pixels of it. All original activity cells and keyframes remain unchanged.

Hero and footer SVGs, all source/optimized artwork, project records, statistics data, contact/repository destinations and all workflow files are preserved from the start of this refinement. Rebuilds reproduce the changes from source. No packages were installed and production generation remains standard-library Python.

## Previews and comparison

[Desktop](previews/desktop.jpg) · [390px](previews/mobile.jpg) · [360px](previews/mobile-360.jpg) · [Light theme](previews/light.jpg)

[Desktop before/after](previews/desktop-comparison.jpg) · [Mobile before/after](previews/mobile-comparison.jpg)

[Animated snake: full 46.3-second cycle](previews/snake.gif) · [Matched-time snake comparison](previews/snake-comparison.jpg)

The larger artwork, clearer mobile labels and full-width secondary cards are visible in the before/after comparisons. Desktop column counts remain unchanged. The matching snake sequence shows rounded turns, directional eyes, a finer tail and less visual overlap than the prior long, segmented skin. Some tight turns remain because they come from the real calendar route.

## Validation

- Seven unit tests pass, including preservation of contribution cells/original keyframes and the new smoothing-distance bound.
- Desktop, 360px, 390px and light browser previews have no broken images, horizontal page overflow or SVG text outside its viewBox. Browser assertions verify 2/3 desktop columns and one mobile column.
- A full cycle of the actual running SVG was captured in real time: 311 frames over 46.3 seconds. The head moves only 1.57 pixels across the 20ms interval around the loop boundary. The animated GIF and matched-time sequence supplement normal motion checks.
- Reduced-motion embedded screenshots 1.2 seconds apart are pixel-identical; direct reduced-motion and standalone static views report zero animations.
- Asset validation passes for 25 README images and 69 references. Existing public destination URLs are unchanged.
- Hash checks preserve the requested artwork, hero/footer, profile data and workflows. Rebuilding is deterministic; whitespace checks pass.

[Browser results](previews/validation.json) · [Animation results](previews/snake-validation.json) · [Preservation results](previews/refinement-preservation.json)

These are local browser previews using the preserved real contribution snapshot. The published GitHub profile and remote Actions were not changed or rerun. The updated renderer will be used by the existing Snake workflow when these changes are eventually published.

## Repeat the checks

```sh
python scripts/build_profile.py
python scripts/prepare_snake.py
python scripts/validate_profile.py
python -m unittest discover -s tests
node scripts/preview.cjs
node scripts/preview_snake.cjs
python scripts/package_snake_preview.py
git diff --check
```

Browser previews use the existing Playwright/Marked tooling and `PROFILE_BROWSER` when an installed Chromium executable is needed. GIF packaging uses the already-available Pillow library, only as optional preview tooling. A preserved previous snake at `.preview/refinement-before/snake.svg` enables the paired comparison; without it, packaging produces an after-only temporal sheet.
