"""Verify GitHub-supported markup with a neutral fixture; never send profile content."""
import json
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
fixture='''<picture>
<source media="(max-width: 600px)" srcset="assets/hero-mobile.svg" />
<source media="(prefers-reduced-motion: reduce)" srcset="assets/snake.svg#reduced-motion" />
<img src="assets/hero.svg" width="100%" alt="Neutral illustration" />
</picture>
<h2>Example heading</h2>
<table><tr><td width="50%" valign="top"><p>Selectable description</p><a href="https://github.com">Example link</a></td><td width="50%">Second cell</td></tr></table>
<details><summary>Fallback</summary><img src="assets/snake.svg" alt="Example animation" /></details>
'''
payload={'text':fixture,'mode':'gfm'}
request=Request('https://api.github.com/markdown',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Accept':'application/vnd.github+json','User-Agent':'profile-preview'},method='POST')
with urlopen(request,timeout=45) as response:html=response.read().decode()
(ROOT/'.preview').mkdir(exist_ok=True)
(ROOT/'.preview/github-rendered.html').write_text(html,encoding='utf-8')
assert '<picture>' in html and '<source' in html
assert 'prefers-reduced-motion: reduce' in html
assert 'assets/snake.svg#reduced-motion' in html
assert '<table' in html
assert 'assets/hero.svg' in html
print('PASS: GitHub Markdown API retained neutral-fixture picture/source, reduced-motion selection, tables, local SVG references, headings, and links. The profile content was not submitted; this does not verify the published profile or image proxy.')
