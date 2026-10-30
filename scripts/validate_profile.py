"""Check local README assets, SVG safety, and metric invariants without network access."""
from collections import Counter
from html.parser import HTMLParser
import json
import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.images=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        assert tag not in {'script','iframe','object','style'},tag
        assert 'style' not in attrs, 'GitHub strips inline styles'
        for key in ('src','srcset','href'):
            if key in attrs:self.refs.append(attrs[key])
        if tag=='img':
            assert attrs.get('alt'), 'Missing alt text'
            self.images.append(attrs)
def main():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    parser=Links();parser.feed(readme)
    refs=parser.refs+re.findall(r'\]\(([^)]+)\)',readme)
    for ref in refs:
        if not ref.startswith(('http','mailto:','#')):
            assert (ROOT/ref).is_file(),ref
    assert 'REPLACE_WITH' not in readme and '—' not in readme
    for file in (ROOT/'assets').rglob('*.svg'):
        xml=ET.parse(file)
        for el in xml.iter():
            tag=el.tag.rsplit('}',1)[-1]
            assert tag not in {'script','foreignObject'},file
            assert not any(k.startswith('on') for k in el.attrib),file
            if tag=='image':assert el.get('href','').startswith('data:'),file
        assert file.stat().st_size < 1_000_000,(file,'SVG too large')
    raw=json.loads((ROOT/'data/github-stats.json').read_text())
    summary=json.loads((ROOT/'data/stats-summary.json').read_text())
    repos=raw['repositories']; project=[r for r in repos if r['project']]
    assert len(repos)==summary['public_repositories']
    assert len(project)==summary['project_repositories']
    assert sum(summary['repositories_by_primary_language'].values())==len(project)
    assert sum(summary['project_categories'].values())==len(project)
    assert sum(summary['language_bytes'].values())==sum(sum(r['language_bytes'].values()) for r in project)
    assert all(not r['fork'] and r['name']!='Abhi-lash19' for r in project)
    projects=json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))
    assert summary['featured_projects']==sum(p['group']=='featured' for p in projects)
    assert summary['languages_tools']==len(set(summary['technology_list']))
    for p in projects:
        if p['private']:
            assert 'href="https://github.com/Abhi-lash19/'+p['repo']+'"' not in readme
    manifest=json.loads((ROOT/'data/artwork.json').read_text())
    assert len(manifest)==13
    for slug,entry in manifest.items():
        original=(ROOT/'assets/source'/entry['filename']).read_bytes()
        assert hashlib.sha256(original).hexdigest()==entry['sha256'],slug
        assert (ROOT/f'assets/art/selected/{slug}.jpg').is_file(),slug
        target=ROOT/('assets/hero.svg' if slug=='hero' else f'assets/projects/{slug}.svg')
        assert 'data:image/jpeg;base64,' in target.read_text(),slug
    assert readme.count('<img src="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg"')==1
    snake=(ROOT/'assets/snake.svg').read_text()
    assert '@keyframes' in snake and '--cs:#68efb5' in snake
    workflow=(ROOT/'.github/workflows/snake.yml').read_text()
    assert 'keep_files: true' in workflow and 'color_snake=#68efb5' in workflow
    assert all(re.search(r'@[a-f0-9]{40}',line) for line in workflow.splitlines() if 'uses:' in line)
    for file in (ROOT/'.github/workflows').glob('*.yml'):
        assert all(re.search(r'@[a-f0-9]{40}',line) for line in file.read_text().splitlines() if 'uses:' in line),file
    print(f'PASS: {len(parser.images)} README images, {len(set(refs))} references, SVG parsing/safety/size, statistics reconciliation, pinned snake workflow and animation source')
if __name__=='__main__':main()
