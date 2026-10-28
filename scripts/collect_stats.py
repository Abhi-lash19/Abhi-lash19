"""Collect public-only GitHub data. Standard library; fail without replacing good data."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER = "Abhi-lash19"

def get(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme", "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urlopen(Request("https://api.github.com" + path, headers=headers), timeout=40) as response:
        return json.load(response)

def collect():
    repos, page = [], 1
    while True:
        batch = get(f"/users/{USER}/repos?type=owner&sort=full_name&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Expected repository list")
        repos.extend(r for r in batch if not r["private"] and r["owner"]["login"].casefold() == USER.casefold())
        if len(batch) < 100:
            break
        page += 1
    if not repos or len({r['id'] for r in repos}) != len(repos):
        raise ValueError("Empty or duplicate repository response; retaining prior snapshot")
    records = []
    for r in sorted(repos, key=lambda r: r["name"].lower()):
        project = not r["fork"] and r["name"].casefold() != USER.casefold()
        languages = get(f"/repos/{USER}/{r['name']}/languages") if project else {}
        if not isinstance(languages, dict) or any(type(n) is not int or n < 0 for n in languages.values()):
            raise ValueError("Invalid language bytes")
        records.append({"name": r["name"], "url": r["html_url"], "fork": r["fork"], "archived": r["archived"], "primary_language": r["language"], "project": project, "language_bytes": languages})
    result = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "source": f"https://api.github.com/users/{USER}/repos", "scope": "Owned public repositories; project repositories exclude forks and the profile repository. Archived repositories remain included.", "repositories": records}
    target = ROOT / "data/github-stats.json"
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    temporary.replace(target)
    print(f"Collected {len(records)} public repositories; {sum(r['project'] for r in records)} project repositories")

if __name__ == '__main__':
    collect()
