# Metric definitions

The repository and commit statistics use public GitHub REST API data collected on 2026-10-31. Each Insights graphic displays its collection date.

## Authored commits

The collector enumerates the account’s owned public repositories, excludes forks and pins each default branch to its observed tip SHA. It requests commits filtered by GitHub username and verifies the returned primary author’s numeric GitHub account ID (114879092). Both the repository inventory and filtered histories are paginated in batches of 100. A commit SHA counts once across all histories. The snapshot records the tips, repository counts and month totals. [GitHub commit API](https://docs.github.com/en/rest/commits/commits#list-commits) · [Saved commit evidence](../data/commit-stats.json)

The 2026 total is **379**, using Git author timestamps converted to Asia/Kolkata through the collection time. The monthly average is **37.9**, or 379 divided by the ten calendar months from January through October, including the current month and zero-activity months. The **542 lifetime commits** are the distinct matching commits reachable in the 19 sampled histories through the same cutoff.

This scope includes account-attributed merge commits and the profile repository. It excludes private repositories, forks, other owners’ repositories, unmerged branches, deleted or unreachable history, unlinked author emails and co-author trailers. A matching display name or committer identity alone earns no credit. API failures stop collection before the saved snapshot is replaced.

| Panel | Source and meaning |
| --- | --- |
| Public Repositories | All owned public repositories returned by the paginated `GET /users/Abhi-lash19/repos?type=owner` API. Includes the profile, forks and archived repositories if present. Saved count: 19. |
| Project Repositories | The same set excluding forks and the username/profile repository. This is a counting rule, not a claim of completed or original products. Saved count: 18. |
| Featured Projects | Number of reviewed entries with `group: featured` in `data/projects.json`: 6. This editorial selection includes two explicitly labeled private projects; it is not a public-repository count. |
| Languages / Tools | Number of distinct technology labels actually shown in the six Tech Stack panels: 31. Generated from the shared stack configuration; not an estimate of proficiency. The exact list is in `data/stats-summary.json`. |
| Languages by code volume | Sum of GitHub language byte counts across public project repositories. Each percentage divides a language's bytes by all reported bytes. Four leading languages are shown; Other combines the remainder. |
| Repositories by language | One primary `language` value from GitHub metadata per public project; absent values become Unclassified. All seven categories in the snapshot are shown with real counts. |
| Project categories (JSON only) | Reviewed classifications in `data/projects.json`, intersected with the public project set. Every public project is counted once. Unreviewed projects become Unclassified. |

Private repositories are excluded from all API-derived counts and charts. Their only contribution to the summary is the explicitly editorial Featured Projects selection. Technology panels describe tools represented by the reviewed repositories and existing profile evidence.

Language bytes can include markup, notebooks, generated code and tutorial material; they do not measure skill, time, authorship or experience. Kagaya's primary language is JavaScript in the saved API metadata although its application source uses TypeScript. Percentages are rounded independently to one decimal place. Chart colors map consistently to language names across both charts.

## Reproduce and refresh

```sh
python scripts/collect_stats.py
python scripts/collect_commits.py
python scripts/build_profile.py --stats-only
python scripts/validate_profile.py
```

Python 3.10+ and its standard library are sufficient. `GITHUB_TOKEN` is optional for API limits and is read only from the environment. The existing collector paginates, explicitly excludes private and foreign repositories, validates responses and only replaces the snapshot after a complete successful collection. Review the changed raw data, derived JSON, README and SVGs together on a working branch.

[Raw snapshot](../data/github-stats.json) · [Reconciled totals and chart values](../data/stats-summary.json)

## Automation and future sources

The existing collector, metrics workflow and 3D workflow are preserved. The metrics and 3D panels have a different scope and are not silently combined with these custom charts. Custom chart refresh remains a reviewed snapshot operation.

The existing GitInsight Engine research is in [PROJECT_RESEARCH.md](PROJECT_RESEARCH.md). Its language service uses the same REST byte endpoint, but the inspected repository-discovery implementation reads only the first 100 GraphQL repositories, lacks a public-only filter and returns an empty list after an API failure. It could become a future source after pagination, public scope and failure behavior are verified. This redesign does not replace analytics infrastructure.

The contribution snake continues through the existing daily Platane/snk workflow and `output` branch. The added renderer styles the real calendar without changing its contribution cells or movement path, and produces reduced-motion output from the same data. Calendar squares are not total commit counts. The authored-commit panels use the separate default-branch history collector described above.
