# Profile redesign review

Prepared on branch `codex/cinematic-profile` from `33f932e`. Changes are local, uncommitted, and unpushed; the default branch and live profile have not been changed.

## What changed

- Cinematic night-studio hero with a separate mobile composition and a neutral portrait placeholder.
- First-person introduction, builder's mindset, and Idea → Research → Design → Build → Verify → Improve workflow.
- Six illustrated featured cards, six compact secondary cards, and seven Learning Lab links. Kagaya is correctly identified as a feature-flag project. Private projects are explicitly labeled.
- Local technology icons and real public-data charts, with definitions and accessible values. Snapshot: 18 public repositories, 17 public project repositories.
- Existing animated snake reused, including its original contribution geometry and motion; invalid color syntax fixed, mint palette added, reduced-motion and bundled fallback assets provided.
- Matching mountain footer and verified existing contact destinations.
- Existing output workflows preserved with SHA pins, job-level write permissions, timeouts, and per-workflow concurrency. No new external service or secret was added.

## Preview

- [Desktop, dark theme](previews/desktop.jpg): 1024-pixel viewport with a 920-pixel outer README panel and 854-pixel content area.
- [Mobile, dark theme](previews/mobile.jpg): 390-pixel viewport; cards wrap into one column.
- [Desktop, light theme](previews/light.jpg): dark components remain readable against native light-theme text.

These are **local browser previews**, using Marked 17.0.5 and github-markdown-css 5.8.1. They are not screenshots of a published GitHub profile. The preview uses the mint bundled snake to demonstrate the post-merge palette. The README itself continues to reference the existing live output URL.

## Actual validation

| Check | Result |
| --- | --- |
| Local asset/reference validation | Passed: 26 README images, 54 unique references, no missing local files or image alt text. |
| SVG checks | Parsed successfully, no scripts or foreignObject, embedded raster/icon dependencies are self-contained, each SVG under 1 MB. |
| Desktop/mobile/light browser rendering | No broken images or horizontal page overflow at 1024/390/1024 pixels. |
| Visual inspection | Desktop composition, mobile hero/card readability, and light-theme contrast inspected; table-based first draft replaced after review. |
| Animated snake | Browser observed changing snake transform over 1.8 seconds, 107 running SVG animations, and fill `rgb(104, 239, 181)`. |
| Reduced motion | Browser selected `snake-static.svg` when `prefers-reduced-motion: reduce` was enabled. |
| Public links | 21 HTTP URLs returned 200, including all 17 public project repositories, profile, portfolio, LinkedIn, and live snake asset. Two private repository links require access and were inspected through the authenticated connector. |
| Metrics | Public/project counts, category totals, primary-language counts, and language-byte sums reconcile to the raw snapshot. |
| Collector tests | Three passing tests: pagination beyond 100 repositories, private/foreign exclusion and fork/profile handling, preservation of the last good snapshot after a failed language request. |
| Reproducibility | Rebuilding from committed artwork and data produced byte-identical README and SVG outputs. |
| Workflow syntax | All three workflow YAML files parsed successfully. Action refs resolve to GitHub commit SHAs. |
| Whitespace | `git diff --check` passed. |
| GitHub markup compatibility | A neutral fixture sent to GitHub's Markdown API retained picture/source, media queries, tables, details, headings, links, and local SVG references. |

The full-README Markdown API request was rejected by automatic approval review because the payload included private-project metadata and personal contact information. It was **not submitted**. A separate neutral fixture was used instead. This check does not test GitHub's image proxy or the final live profile.

Existing historical metrics and snake runs were successful. The modified workflows have **not** been run on GitHub in this task. The live snake will adopt its new palette on the first successful run after merge. Scheduled custom-chart refresh is intentionally not enabled: the charts are reviewed, dated snapshots refreshed by the documented script; existing legacy metrics and 3D automation continue separately.

## Review and merge

1. Review README.md, these screenshots, the file list, and the Codex change view. Check the project labels, neutral portrait, private links, and chart scope.
2. Optionally rerun the local checks:

   ```sh
   python scripts/validate_profile.py
   python -m unittest discover -s tests
   git diff --check
   ```

3. When satisfied, commit and push the working branch:

   ```sh
   git add README.md assets data docs scripts tests .github/workflows .gitignore
   git commit -m "Redesign profile with cinematic artwork and verified project data"
   git push -u origin codex/cinematic-profile
   ```

4. Open a pull request from `codex/cinematic-profile` to `main`, review the rendered README on that branch, then merge it yourself.
5. After merge, verify the profile on GitHub and the first scheduled/manual Snake, Metrics, and 3D workflow runs. Check the live snake color and that the shared output branch still contains the other generated files.

## Maintaining previews

`scripts/preview.cjs` needs Marked and Playwright, and `scripts/prepare_art.cjs` needs Sharp. Those packages were already available in this environment; no dependencies were installed. For another machine, use your existing compatible packages via NODE_PATH or install them in a separate tooling environment. Set PROFILE_BROWSER to an installed browser executable if Playwright has no bundled browser. Run `scripts/fetch_design_resources.py` only if re-vendoring icons or obtaining the preview stylesheet; normal generation and validation are offline.

See [ASSETS.md](ASSETS.md) for the rendering tradeoffs, [METRICS.md](METRICS.md) for sources, [PROJECT_RESEARCH.md](PROJECT_RESEARCH.md) for project evidence, and [FILES.md](FILES.md) for the complete change inventory.
