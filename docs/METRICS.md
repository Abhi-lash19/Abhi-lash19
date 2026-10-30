# Metric definitions

The custom charts use the existing **2026-10-28 public GitHub API snapshot**. They are not a live productivity dashboard. A date appears in the charts, the README source link and `data/stats-summary.json`.

| Panel | Source and meaning |
| --- | --- |
| Public Repositories | All owned public repositories returned by the paginated `GET /users/Abhi-lash19/repos?type=owner` API. Includes the profile, forks and archived repositories if present. Saved count: 18. |
| Project Repositories | The same set excluding forks and the username/profile repository. This is a counting rule, not a claim of completed or original products. Saved count: 17. |
| Featured Projects | Number of reviewed entries with `group: featured` in `data/projects.json`: 6. This editorial selection includes two explicitly labeled private projects; it is not a public-repository count. |
| Languages / Tools | Number of distinct technology labels actually shown in the four Tech Stack panels: 14. Generated from the shared stack configuration; not an estimate of proficiency. The exact list is in `data/stats-summary.json`. |
| Languages by code volume | Sum of GitHub language byte counts across public project repositories. Each percentage divides a language's bytes by all reported bytes. Four leading languages are shown; Other combines the remainder. |
| Repositories by language | One primary `language` value from GitHub metadata per public project; absent values become Unclassified. All seven categories in the snapshot are shown with real counts. |
| Project categories (JSON only) | Reviewed classifications in `data/projects.json`, intersected with the public project set. Every public project is counted once. Unreviewed projects become Unclassified. |

Private repositories are excluded from all API-derived counts and charts. Their only contribution to the summary is the explicitly editorial Featured Projects selection. Technology panels describe tools represented by the reviewed repositories and existing profile evidence.

Language bytes can include markup, notebooks, generated code and tutorial material; they do not measure skill, time, authorship or experience. Kagaya's primary language is JavaScript in the saved API metadata although its application source uses TypeScript. Percentages are rounded independently to one decimal place. Chart colors map consistently to language names across both charts.

## Reproduce and refresh

```sh
python scripts/collect_stats.py
python scripts/build_profile.py --stats-only
python scripts/validate_profile.py
```

Python 3.10+ and its standard library are sufficient. `GITHUB_TOKEN` is optional for API limits and is read only from the environment. The existing collector paginates, explicitly excludes private and foreign repositories, validates responses and only replaces the snapshot after a complete successful collection. Review the changed raw data, derived JSON, README and SVGs together on a working branch.

[Raw snapshot](../data/github-stats.json) · [Reconciled totals and chart values](../data/stats-summary.json)

## Automation and future sources

The existing collector, metrics workflow and 3D workflow are preserved. The metrics and 3D panels have a different scope and are not silently combined with these custom charts. Custom chart refresh remains a reviewed snapshot operation.

The existing GitInsight Engine research is in [PROJECT_RESEARCH.md](PROJECT_RESEARCH.md). Its language service uses the same REST byte endpoint, but the inspected repository-discovery implementation reads only the first 100 GraphQL repositories, lacks a public-only filter and returns an empty list after an API failure. It could become a future source after pagination, public scope and failure behavior are verified. This redesign does not replace analytics infrastructure.

The contribution snake continues through the existing daily Platane/snk workflow and `output` branch. The added renderer styles the real calendar without changing its contribution cells or movement path, and produces reduced-motion output from the same data. Calendar squares are not total commit counts. No total commits, stars, followers, rankings or productivity scores are displayed.
