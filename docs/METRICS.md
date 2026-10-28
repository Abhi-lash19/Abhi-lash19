# Metric definitions

The README shows a **saved snapshot**, with its UTC collection date printed in the charts. It is not a live productivity dashboard.

| Panel | Source and meaning |
| --- | --- |
| Public repositories | All owned public repositories returned by the paginated `GET /users/Abhi-lash19/repos?type=owner` API. Includes this profile, forks, and archived repositories if present. |
| Project repositories | The same set excluding forks and the username/profile repository. This is an explicit counting rule, not a claim that every repository is an original or completed product. |
| Languages by code volume | Sum of `GET /repos/Abhi-lash19/{repo}/languages` byte counts across public project repositories. Each percentage divides that language's byte sum by all reported bytes. Four leading languages are shown; Other combines the remainder. |
| Repositories by language | One `language` value from GitHub repository metadata per public project. Missing values are counted as Unclassified. These are counts, not percentages. |
| Project categories | Reviewed classifications in `data/projects.json`, intersected with the current public project set. Every public project is counted once. New unreviewed projects become Unclassified. |

Private repositories are excluded from all statistics, including the featured BountyDesk and Chitragupta projects. Category labels describe intent, not completion or proficiency. The language API reports GitHub's detected bytes, which can include markup, notebooks, generated code, and tutorial material. It does not establish authorship or experience. Kagaya's primary language is JavaScript in GitHub metadata even though its application source uses TypeScript; the chart preserves the API result. Percentages are rounded independently to one decimal place.

## Reproduce and refresh

```sh
python scripts/collect_stats.py
python scripts/build_profile.py --stats-only
python scripts/validate_profile.py
```

Python 3.10+ and its standard library are sufficient. `GITHUB_TOKEN` is optional for rate limits and is only read from the environment. The collector paginates, explicitly excludes nonpublic data, validates every language response, and writes the snapshot only after the entire collection succeeds. A failed request must not become an invented zero. Review and commit the changed snapshot and SVGs together on a working branch.

Raw values are in [github-stats.json](../data/github-stats.json); reconciled totals are in [stats-summary.json](../data/stats-summary.json).

## Existing automation

The existing `metrics.yml` and `3d-chart.yml` generators, schedules, output locations, and options are retained. Action references are now pinned, write permissions are limited to the publishing jobs, and each workflow serializes its own runs. Separate concurrency groups avoid one generator canceling another generator's pending run. Recent output was inspected, and successful historical metrics/snake runs were observed. Those legacy panels are not embedded in this redesign: they include measures outside this brief and do not share the documented scope above. The new snapshot deliberately does not silently combine their values with the custom charts.

GitInsight Engine's language service aggregates the same REST byte endpoint, but its repository discovery currently asks for the first 100 GraphQL repositories without pagination or a public-only filter, and returns an empty list after an API failure. Reusing that output directly would obscure the denominator and error state. The small collector here makes both explicit without adding a service or dependency.

The contribution snake continues to update through the existing daily workflow and `output` branch. Its squares represent the contribution calendar supplied to Platane/snk, not total commits. No commit totals, stars, followers, rankings, or productivity scores are displayed.
