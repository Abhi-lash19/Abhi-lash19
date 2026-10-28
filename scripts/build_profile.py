"""Rebuild README and self-contained SVG panels from reviewed data; no dependencies."""
import argparse
import base64
from collections import Counter
from html import escape as e
import json
import math
from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
COLORS = ['#68efb5', '#43b5ff', '#ad8dff', '#ffcd71', '#fa818e', '#71dcdf', '#98a8be']

def text(x, y, value, size=18, color='#d9e5f2', weight=400, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{e(str(value))}</text>'

def rect(x, y, w, h, color, radius=12, stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}"/>'

def svg(w, h, body, title, desc=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{e(title)}</title><desc id="desc">{e(desc)}</desc><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#091a28"/><stop offset="1" stop-color="#060d17"/></linearGradient><linearGradient id="accent"><stop stop-color="#68efb5"/><stop offset="1" stop-color="#549aff"/></linearGradient></defs><g font-family="Segoe UI,Arial,sans-serif">{body}</g></svg>\n'

def panel(w, h):
    return rect(1, 1, w-2, h-2, 'url(#bg)', 16, '#233a4d')

def write(name, value):
    target = A / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding='utf-8')

def embedded(path, x, y, w, h, fit='xMidYMid slice'):
    ext = path.suffix
    mime = 'image/jpeg' if ext == '.jpg' else 'image/svg+xml'
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" href="data:{mime};base64,{data}"/>'

def stats():
    data = json.loads((ROOT / 'data/github-stats.json').read_text())
    projects = json.loads((ROOT / 'data/projects.json').read_text(encoding='utf-8'))
    repos = data['repositories']
    selected = [r for r in repos if r['project']]
    langs, counts = Counter(), Counter()
    for r in selected:
        langs.update(r['language_bytes'])
        counts[r['primary_language'] or 'Unclassified'] += 1
    date = data['generated_at'][:10]
    summary = [(len(repos), 'Public repositories', 'Owned public repositories'), (len(selected), 'Project repositories', 'Excludes forks + profile')]
    for i, (value, label, note) in enumerate(summary):
        body = panel(420, 116) + rect(20, 22, 3, 70, COLORS[i], 1)
        body += text(40, 62, value, 40, COLORS[i], 700) + text(112, 46, label, 21, '#f1f7ff', 600) + text(112, 76, note, 14, '#a5bbcf')
        write(f'stats/summary-{i}.svg', svg(420, 116, body, f'{value} {label}', note + '; ' + date))
    total = sum(langs.values())
    top = langs.most_common(4)
    remainder = total - sum(n for _, n in top)
    if remainder:
        top.append(('Other', remainder))
    body = panel(440, 300) + text(24, 35, 'Languages by code volume', 22, '#f1f7ff', 600)
    body += text(24, 60, 'Share of GitHub-reported language bytes', 14, '#9cb2c6')
    offset, circumference = 0, 2*math.pi*65
    for i, (name, n) in enumerate(top):
        length = n/total*circumference
        body += f'<circle cx="104" cy="161" r="65" fill="none" stroke="{COLORS[i]}" stroke-width="22" stroke-dasharray="{length} {circumference-length}" stroke-dashoffset="{-offset}" transform="rotate(-90 104 161)"/>'
        offset += length
        body += rect(203, 100+i*29, 8, 8, COLORS[i], 3) + text(222, 109+i*29, name, 15) + text(414, 109+i*29, f'{100*n/total:.1f}%', 15, '#d9e5f2', extra='text-anchor="end"')
    body += text(104, 158, f'{total/1000000:.2f} MB', 19, '#f1f7ff', 600, 'text-anchor="middle"') + text(104, 179, 'reported code', 12, '#9cb2c6', extra='text-anchor="middle"')
    body += text(24, 274, f'{len(selected)} public projects · {date}', 13, '#8ca6bb')
    write('stats/languages.svg', svg(440, 300, body, 'Language share by bytes', '; '.join(f'{k}: {v} bytes' for k,v in langs.most_common())))
    body = panel(440, 300) + text(24, 35, 'Repositories by language', 22, '#f1f7ff', 600) + text(24, 60, 'One primary language per public project', 14, '#9cb2c6')
    for i, (name,n) in enumerate(counts.most_common()):
        y=82+i*25
        body += text(24,y+13,name,15) + rect(153,y,220,11,'#172b3e',5) + rect(153,y,220*n/max(counts.values()),11,COLORS[i%7],5) + text(410,y+12,n,15,extra='text-anchor="end"')
    body += text(24, 274, f'{len(selected)} public projects · counts, not percentages', 13, '#8ca6bb')
    write('stats/repositories.svg', svg(440, 300, body, 'Repository counts by primary language', '; '.join(f'{k}: {v}' for k,v in counts.most_common())))
    classification = {p['repo']:p['category'] for p in projects}
    categories = Counter(classification.get(r['name'],'Unclassified') for r in selected)
    body = panel(440, 260) + text(24,35,'What I’m building',22,'#f1f7ff',600) + text(24,60,'Reviewed categories of public projects',14,'#9cb2c6')
    for i,(name,n) in enumerate(categories.most_common()):
        y=93+i*40
        body += text(24,y,name,17) + rect(177,y-12,190,13,'#172b3e',6) + rect(177,y-12,190*n/len(selected),13,COLORS[i%7],6) + text(411,y,n,17,extra='text-anchor="end"')
    body += text(24,235,'Private projects excluded · editorial classification',13,'#8ca6bb')
    write('stats/categories.svg',svg(440,260,body,'Project category counts','; '.join(f'{k}: {v}' for k,v in categories.items())))
    body=panel(440,260)+text(24,35,'Behind the numbers',22,'#f1f7ff',600)
    for i,line in enumerate(['Public GitHub REST API data.', 'Every chart has a defined scope.', 'Bytes describe code, not proficiency.', 'Project counts include learning work.', 'No commit totals or productivity scores.']):
        body+=text(24,80+i*29,line,16,'#b8ccdd')
    body+=text(24,235,'Snapshot: '+date+' UTC',14,'#68efb5')
    write('stats/sources.svg',svg(440,260,body,'How to read these charts'))
    (ROOT/'data/stats-summary.json').write_text(json.dumps({'public_repositories':len(repos),'project_repositories':len(selected),'language_bytes':dict(langs.most_common()),'repositories_by_primary_language':dict(counts.most_common()),'project_categories':dict(categories)},indent=2)+'\n')

def design():
    # No real portrait was found. This neutral silhouette is explicitly a placeholder.
    portrait = '<circle cx="80" cy="80" r="75" fill="#0d1d2b" stroke="url(#accent)" stroke-width="3"/><circle cx="80" cy="64" r="23" fill="#617d90"/><path d="M36 130C37 90 123 90 124 130" fill="#617d90"/>'
    write('portrait-placeholder.svg',svg(160,160,portrait,'Neutral portrait placeholder','A generic silhouette, not a likeness of Abhilash.'))
    for mobile,w,h in [(False,1440,540),(True,680,600)]:
        b=embedded(A/'art/hero.jpg',0,0,w,h)
        if mobile:
            b+=rect(0,0,w,h,'#06101b',0).replace('fill="#06101b"','fill="#06101b" opacity="0.60"')
            x,y=38,210
        else:
            b+='<defs><linearGradient id="shade"><stop stop-color="#06101b" stop-opacity=".98"/><stop offset=".55" stop-color="#06101b" stop-opacity=".75"/><stop offset="1" stop-color="#06101b" stop-opacity="0"/></linearGradient></defs>'+rect(0,0,w,h,'url(#shade)',0)
            x,y=54,230
        b+=embedded(A/'portrait-placeholder.svg',x,34,90,90)
        b+=text(x+112,69,'ABHILASH KUMAR GIRI',mobile and 20 or 24,'#f1f7ff',600)+text(x+112,100,'@Abhi-lash19  /  Backend + Cloud',18,'#a8c4d9')
        b+=text(x,y-49,'$ whoami',20,'#68efb5',extra='font-family="Consolas,monospace"')
        b+=text(x,y+15,'I build things',mobile and 49 or 64,'#f5f8ff',700)
        b+=text(x,y+86,'to understand things.',mobile and 49 or 64,'#68efb5',700)
        b+=text(x,y+143,'Useful tools. Small experiments. Real learning.',mobile and 23 or 25,'#c2d6e8')
        for i,word in enumerate(['BACKEND','CLOUD','AI TOOLS']):
            xx=x+i*166
            b+=rect(xx,y+183,148,38,'#0b2130',19,'#2f5866')+text(xx+74,y+208,word,15,'#a7dfdf',600,'text-anchor="middle"')
        b+=rect(1,1,w-2,h-2,'none',20,'#2c4d61')
        write('hero-mobile.svg' if mobile else 'hero.svg',svg(w,h,b,'I build things to understand things.','Abhilash Kumar Giri. Backend and cloud developer. Night-time studio illustration; neutral portrait placeholder.'))
    b=embedded(A/'art/footer.jpg',0,0,1440,340)+rect(0,0,1440,340,'#060e19',0).replace('fill="#060e19"','fill="#060e19" opacity=".25"')
    b+=text(52,138,'Better tools. Brighter ideas.',49,'#f1f7ff',700)+text(52,190,'One useful thing at a time.',30,'#8bf1c0')+text(52,280,'STAY CURIOUS  /  KEEP BUILDING',17,'#a7bed2',600)
    write('footer.svg',svg(1440,340,b,'Better tools. Brighter ideas. One useful thing at a time.'))
    groups=[('languages','Languages',[('python','Python'),('typescript','TypeScript'),('javascript','JavaScript'),('java','Java')]),('backend','Backend and APIs',[('nodejs','Node.js'),('fastapi','FastAPI'),('graphql','GraphQL'),('postgresql','Postgres')]),('cloud','Cloud and DevOps',[('amazonwebservices','AWS'),('docker','Docker'),('kubernetes','Kubernetes'),('terraform','Terraform')]),('ai','AI and Data',[('pytorch','PyTorch'),('sqlite','SQLite'),('python','Python'),('postgresql','Postgres')])]
    for slug,title,icons in groups:
        b=panel(440,145)+text(24,36,title,22,'#f1f7ff',600)
        for i,(name,label) in enumerate(icons):
            x=30+i*105
            b+=embedded(A/f'icons/{name}.svg',x+12,58,40,40,'xMidYMid meet')+text(x+32,123,label,14,'#b7cddd',extra='text-anchor="middle"')
        write(f'tech/{slug}.svg',svg(440,145,b,title,', '.join(label for _,label in icons)))

def readme():
    projects=json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))
    def pair_images(paths, folder, alts):
        return '<p align="center">\n'+'\n'.join(f'  <img src="assets/{folder}/{p}.svg" width="420" alt="{e(alt,quote=True)}" />' for p,alt in zip(paths,alts))+'\n</p>\n\n'
    def section(slug,title):
        return f'\n<h2>{title}</h2>\n\n'
    # Native headings and text remain selectable and follow GitHub's theme.
    content='''<!-- Generated by scripts/build_profile.py. Edit data/projects.json or the generator. -->
<picture>
  <source media="(max-width: 600px)" srcset="assets/hero-mobile.svg" />
  <img src="assets/hero.svg" width="100%" alt="Abhilash Kumar Giri: I build things to understand things. A cinematic night-time coding studio with a neutral portrait placeholder." />
</picture>

<h1>Abhilash Kumar Giri</h1>

I’m a backend and cloud developer who learns by building real things. Right now, I’m exploring AI-assisted software engineering, coding agents, and useful personal tools. Most of my GitHub is personal work, engineering experiments, and learning projects. I’m still early in contributing to open source.

<p><a href="https://github.com/Abhi-lash19">GitHub</a> · <a href="https://abhi-lash19.github.io/3d-portfolio/">Portfolio</a> · <a href="https://linkedin.com/in/abhilash-giri">LinkedIn</a> · <a href="mailto:abhilashkumargiri63@gmail.com">Email</a></p>

'''
    content+=pair_images(['summary-0','summary-1'],'stats',['Public repository count; includes this profile repository.','Public project repository count; excludes forks and this profile.'])
    content+='''<h2>A builder's mindset</h2>

I like turning ideas and everyday problems into working tools. Implementing a concept helps me see what I understand and what I still need to learn. Before I build, I research existing solutions and decide what is actually worth making.

I’m curious about how AI coding tools can help me work better. Requirements, understanding the code, testing, and verification still matter. I care more about learning something real and getting useful software working than collecting badges.

<h3>How I build</h3>

<p><strong>Idea → Research → Design → Build → Verify → Improve</strong></p>

'''
    for group,title in [('featured','✦ Featured projects'),('more','◇ More to explore')]:
        content+=section(group,title)
        if group=='featured':
            content+='Personal tools and experiments from my workbench. The artwork is conceptual, not a product screenshot. **Private** repositories require access; **WIP** means work in progress.\n\n'
        content+='<p align="center">\n'
        subset=[p for p in projects if p['group']==group]
        for p in subset:
            link='https://github.com/Abhi-lash19/'+p['repo']
            alt=f'{p["name"]} | {p["label"]}. {p["description"]} Stack: '+', '.join(p['tags'])+'. Conceptual artwork.'
            content+=f'  <a href="{link}"><img src="assets/projects/{p["slug"]}.svg" width="420" alt="{e(alt,quote=True)}" /></a>\n'
        content+='</p>\n\n<details>\n<summary>Read project descriptions and technology details</summary>\n\n'
        for p in subset:
            content+=f'**[{p["name"]}](https://github.com/Abhi-lash19/{p["repo"]})** · {p["label"]}\n\n{p["description"]} *'+', '.join(p['tags'])+'.*\n\n'
        content+='</details>\n\n'
    content+=section('lab','⟡ Learning Lab')+'Earlier backend, cloud, deployment, and browser projects. These are learning work, not claims of production services.\n\n'
    for p in projects:
        if p['group']=='lab':
            content+=f'- **[{p["name"]}](https://github.com/Abhi-lash19/{p["repo"]})** · {p["description"]}'+(' *'+p['label']+'.*' if 'Tutorial' in p['label'] or 'assignment' in p['label'] else '')+'\n'
    content+=section('tech','⌘ Technology stack')+'Tools I use and explore, with different levels of familiarity. The stack reflects these repositories, not equal expertise in everything shown.\n\n'
    content+=pair_images(['languages','backend','cloud','ai'],'tech',['Languages: Python, TypeScript, JavaScript, Java.','Backend and APIs: Node.js, FastAPI, GraphQL, PostgreSQL.','Cloud and DevOps: AWS, Docker, Kubernetes, Terraform.','AI and Data: PyTorch, SQLite, Python, PostgreSQL.'])
    content+=section('insights','▥ GitHub insights')+'These panels use a saved public GitHub API snapshot. Language bytes measure the code GitHub detects, not skill or time spent.\n\n'
    content+=pair_images(['languages','repositories','categories','sources'],'stats',['Language percentages by GitHub-reported code bytes, across public project repositories.','Counts of public project repositories by GitHub primary language.','Reviewed public project categories; private projects excluded.','Metric definitions and snapshot date.'])
    content+='[Sources, definitions, and limitations](docs/METRICS.md) · [Raw snapshot](data/github-stats.json) · [Accessible chart values](data/stats-summary.json)\n'
    content+=section('snake','↝ Contribution journey')+'''An animated snake moving through my actual GitHub contribution grid. A small reminder to keep showing up and learning.

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/snake-static.svg" />
  <img src="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg" width="100%" alt="Animated snake consuming Abhilash’s GitHub contribution squares. Updated by the existing daily workflow." />
</picture>

<details>
<summary>Snake snapshot and animation fallback</summary>

The live image above comes from the existing output branch. If that image is unavailable, this bundled animated snapshot remains available. The snapshot is dated in the asset notes and is not a live activity report.

<img src="assets/snake.svg" width="100%" alt="Bundled animated contribution snake snapshot, recolored mint." />

</details>

<h2>Let’s connect</h2>

I’m happy to talk about a useful tool, a backend problem, or something you’re learning. Better tools and a little more understanding: that’s what I’m working toward.

<p><a href="https://github.com/Abhi-lash19">GitHub ↗</a> &nbsp; · &nbsp; <a href="https://abhi-lash19.github.io/3d-portfolio/">Portfolio ↗</a> &nbsp; · &nbsp; <a href="https://linkedin.com/in/abhilash-giri">LinkedIn ↗</a> &nbsp; · &nbsp; <a href="mailto:abhilashkumargiri63@gmail.com">Email ↗</a></p>

<img src="assets/footer.svg" width="100%" alt="Better tools. Brighter ideas. One useful thing at a time. A quiet mountain valley beneath the stars." />
'''
    (ROOT/'README.md').write_text(content,encoding='utf-8')

def project_cards():
    projects=json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))
    for p in projects[:12]:
        featured=p['group']=='featured'
        w,h=800,620 if featured else 390
        b=panel(w,h)
        if featured:
            b+=f'<defs><clipPath id="art"><rect x="2" y="2" width="796" height="278" rx="15"/></clipPath><linearGradient id="fade" x2="0" y2="1"><stop stop-color="#06101b" stop-opacity="0"/><stop offset="1" stop-color="#06101b"/></linearGradient></defs><g clip-path="url(#art)">'+embedded(A/f'art/{p["slug"]}.jpg',2,2,796,278)+'</g>'+rect(2,188,796,94,'url(#fade)',0)
            y=305
        else:
            c=p['color']
            b+=rect(28,26,56,56,'#102333',14,c)+text(56,64,{'vera':'>_','kagaya':'⚑','edututor':'?','express':'{ }','portfolio':'◉','monitorpro':'⌁'}[p['slug']],28,c,600,'text-anchor="middle"')
            for j in range(8):
                xx=485+j*35; yy=52+math.sin(j+len(p['name']))*21
                b+=f'<circle cx="{xx}" cy="{yy}" r="5" fill="{c}" opacity=".65"/>'
                if j<7:b+=f'<path d="M {xx} {yy} L {xx+35} {52+math.sin(j+1+len(p["name"]))*21}" stroke="{c}" opacity=".4" fill="none"/>'
            y=115
        b+=text(28,y,p['name'],36,'#f2f7ff',650)
        b+=text(28,y+36,p['label'].upper(),20,p['color'],600,extra='letter-spacing="1"')
        lines=textwrap.wrap(p['description'],width=53)
        for i,line in enumerate(lines):b+=text(28,y+80+i*34,line,27,'#c4d5e5')
        tag_y=h-106
        xx=28
        for label in p['tags']:
            tw=32+len(label)*13
            b+=rect(xx,tag_y,tw,36,'#0c2130',9,'#294759')+text(xx+16,tag_y+25,label,22,'#b9dfe5')
            xx+=tw+12
        b+=text(28,h-28,'PRIVATE REPOSITORY · ACCESS REQUIRED' if p['private'] else 'EXPLORE REPOSITORY',19,p['color'],600,extra='letter-spacing="1"')+text(w-34,h-28,'↗',28,p['color'],extra='text-anchor="end"')
        b+=rect(1,1,w-2,h-2,'none',16,p['color']).replace('stroke="'+p['color']+'"','stroke="'+p['color']+'" stroke-opacity=".5"')
        write(f'projects/{p["slug"]}.svg',svg(w,h,b,p['name'],p['label']+'. '+p['description']+' Conceptual artwork, not a screenshot.'))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stats-only',action='store_true')
    args=parser.parse_args()
    stats()
    if not args.stats_only:
        design()
        project_cards()
        readme()
    print('Profile assets generated')
