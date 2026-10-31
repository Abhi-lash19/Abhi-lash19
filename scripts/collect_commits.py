"""Snapshot account-attributed commits on owned public non-fork default branches."""
import json
import re
from datetime import datetime, timedelta, timezone
from itertools import count
from urllib.error import HTTPError
from urllib.parse import quote, urlencode

from collect_stats import ROOT, USER, get

IST = timezone(timedelta(hours=5, minutes=30))
SHA = re.compile(r'[0-9a-f]{40}')


def pages(fetch, path, **query):
    for page in count(1):
        params = urlencode(dict(query, per_page=100, page=page))
        rows = fetch(f'{path}?{params}')
        if not isinstance(rows, list):
            raise ValueError(f'Invalid page for {path}')
        yield from rows
        if len(rows) < 100:
            return


def snapshot(fetch, as_of):
    account = fetch(f'/users/{USER}')
    owner_id = account['id']
    local = as_of.astimezone(IST)
    months = [0] * local.month
    seen = set()
    repositories = []
    for repo in pages(fetch, f'/users/{USER}/repos', type='owner', sort='full_name'):
        if repo['private'] or repo['fork'] or repo['owner']['id'] != owner_id:
            continue
        name = repo['name']
        endpoint = f'/repos/{USER}/{quote(name, safe="")}/commits'
        # Pin the branch before paginating its history so a concurrent push
        # cannot shift commits between pages. Only a confirmed empty repo is zero.
        try:
            head = fetch(endpoint + '?' + urlencode({'sha':repo['default_branch'], 'per_page':1}))
            if not isinstance(head, list) or len(head) != 1:
                raise ValueError(f'Expected one default-branch tip for {name}')
            tip = head[0]['sha']
        except HTTPError as exc:
            if exc.code != 409 or 'Git Repository is empty' not in exc.read().decode():
                raise
            tip = None
        if tip is not None and not SHA.fullmatch(tip):
            raise ValueError('Invalid tip SHA')
        attributed = set()
        for row in pages(fetch, endpoint, sha=tip, author=USER) if tip else ():
            if (row.get('author') or {}).get('id') != owner_id:
                continue
            sha = row['sha']
            if not SHA.fullmatch(sha):
                raise ValueError('Invalid commit SHA')
            authored = datetime.fromisoformat(row['commit']['author']['date'].replace('Z','+00:00'))
            if authored > as_of:
                continue
            attributed.add(sha)
            if sha in seen:
                continue
            seen.add(sha)
            authored = authored.astimezone(IST)
            if authored.year == local.year:
                months[authored.month - 1] += 1
        repositories.append({'name':name, 'branch':repo['default_branch'], 'tip':tip, 'attributed_commits':len(attributed)})
    if not repositories or len({r['name'] for r in repositories}) != len(repositories):
        raise ValueError('Missing or duplicate repository inventory')
    return {'account':USER, 'account_id':owner_id, 'as_of':local.isoformat(timespec='seconds'),
            'timezone':'Asia/Kolkata', 'year':local.year, 'elapsed_calendar_months':local.month,
            'monthly_counts':months, 'year_to_date':sum(months), 'monthly_average':round(sum(months)/local.month, 1),
            'lifetime':len(seen), 'repositories':repositories}


if __name__ == '__main__':
    result = snapshot(get, datetime.now(timezone.utc))
    target = ROOT / 'data/commit-stats.json'
    pending = target.with_suffix('.tmp')
    pending.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    pending.replace(target)
    print(f"{len(result['repositories'])} public repos, {result['year_to_date']} this year, "
          f"{result['monthly_average']} per elapsed month, {result['lifetime']} lifetime")
