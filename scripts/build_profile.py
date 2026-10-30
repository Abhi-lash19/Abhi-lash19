"""Build self-contained GitHub README panels from reviewed data and supplied artwork.

Standard library only. Run prepare_art.cjs only when importing new source artwork.
"""
import argparse
import base64
from collections import Counter
from html import escape as e
import json
import math
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'assets'
MINT, CYAN, VIOLET = '#72f1c6', '#6edbff', '#ad8dff'
INK, WHITE, MUTED = '#071321', '#f3f6ff', '#b5c7dd'
LANG_COLORS = {'Python':'#4285ff','JavaScript':'#ffde59','TypeScript':'#67b0ff','HTML':'#f47756','HCL':'#ad80ef','Java':'#e1a85c','CSS':'#76d9c3','Other':'#9da8bb'}
TECH = [
    ('languages','Languages',[('python','Python'),('typescript','TypeScript'),('javascript','JavaScript'),('java','Java')]),
    ('backend','Backend & APIs',[('nodejs','Node.js'),('fastapi','FastAPI'),('graphql','GraphQL'),('postgresql','PostgreSQL')]),
    ('cloud','Cloud & DevOps',[('amazonwebservices','AWS'),('docker','Docker'),('kubernetes','Kubernetes'),('terraform','Terraform')]),
    ('ai','AI & Data',[('pytorch','PyTorch'),('sqlite','SQLite')]),
]
CONTACTS = [('github','GitHub','https://github.com/Abhi-lash19'),('globe','Portfolio','https://abhi-lash19.github.io/3d-portfolio/'),('linkedin','LinkedIn','https://linkedin.com/in/abhilash-giri'),('mail','Email','mailto:abhilashkumargiri63@gmail.com')]
MINDSET = 'Most of my projects begin with a question or a problem. I learn by implementing, breaking things, and figuring them out. AI tools help me move faster, but understanding and verification still matter.'
SUBTITLE = 'Backend and cloud developer exploring AI-assisted engineering, useful personal tools, and learning by building real systems.'
WORKFLOW = [('bulb','Idea','A question or problem'),('search','Research','Explore and plan'),('pen','Design','Shape the approach'),('code','Build','Turn ideas into code'),('check','Verify','Test and validate'),('chart','Improve','Refine and repeat')]


def text(x,y,value,size=18,color=MUTED,weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{e(str(value))}</text>'


def rect(x,y,w,h,color,radius=10,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}"/>'


def svg(w,h,body,title,desc=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{e(title)}</title><desc id="desc">{e(desc)}</desc><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#091c29"/><stop offset=".6" stop-color="#07111e"/><stop offset="1" stop-color="#17162f"/></linearGradient><linearGradient id="accent"><stop stop-color="{MINT}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient><filter id="glow" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="4"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><g font-family="Segoe UI,Arial,sans-serif">{body}</g></svg>\n'''


def panel(w,h):
    return rect(1,1,w-2,h-2,'url(#bg)',10,'#28445e')


def write(name,value):
    target=A/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(value,encoding='utf-8')


def embedded(path,x,y,w,h,fit='xMidYMid slice'):
    mime='image/jpeg' if path.suffix=='.jpg' else 'image/svg+xml'
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" href="data:{mime};base64,{data}"/>'


def art(slug,x,y,w,h,fit='xMidYMid slice'):
    return embedded(A/f'art/selected/{slug}.jpg',x,y,w,h,fit)


def lines(value,x,y,width,size=18,color=MUTED,leading=None):
    return ''.join(text(x,y+i*(leading or size*1.4),s,size,color) for i,s in enumerate(textwrap.wrap(value,width)))


def icon(name,x,y,size=24,color=MINT):
    paths={
        'bulb':'<path d="M8 18h8M9 21h6M9 16c0-4-4-4-4-9a7 7 0 0114 0c0 5-4 5-4 9M12 16v-5m-3-3 3 3 3-3"/>',
        'search':'<circle cx="10" cy="10" r="7"/><path d="m15 15 7 7"/>',
        'pen':'<path d="m3 21 2-7L17 2l5 5L10 19zM14 5l5 5M5 14l5 5"/>',
        'code':'<path d="m7 5-6 7 6 7m10-14 6 7-6 7M14 3l-4 18"/>',
        'check':'<circle cx="12" cy="12" r="10"/><path d="m7 12 4 4 7-9"/>',
        'chart':'<path d="M4 20V11m8 9V3m8 17V7" stroke-width="3"/>',
        'cube':'<path d="m12 1 10 6v11l-10 5-10-5V7zm0 11v11M2 7l10 5 10-5M7 4l10 6"/>',
        'folder':'<path d="M2 7V3h7l3 3h10v15H2zM2 8h20"/>',
        'star':'<path d="m12 1 3 7 8 1-6 6 1 8-6-4-7 4 2-8-6-6 8-1z"/>',
        'globe':'<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.5" ry="10"/><path d="M2 12h20M4 6h16M4 18h16"/>',
        'mail':'<rect x="1" y="4" width="22" height="16" rx="2"/><path d="m2 5 10 8L22 5"/>',
        'linkedin':'<rect width="24" height="24" rx="2" fill="currentColor" stroke="none"/><path d="M5 10v9M5 6v.2M10 19v-9m0 4c0-5 8-5 8 0v5" stroke="#071321" stroke-width="2.8"/>',
        'github':'<path fill="currentColor" stroke="none" d="M12 .8a11.3 11.3 0 00-3.57 22c.56.1.77-.24.77-.54v-2.1c-3.14.68-3.8-1.34-3.8-1.34-.51-1.3-1.25-1.65-1.25-1.65-1.03-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1.01 1.72 2.65 1.22 3.3.93.1-.73.4-1.22.72-1.5-2.51-.29-5.15-1.26-5.15-5.59 0-1.23.44-2.24 1.16-3.03-.12-.28-.5-1.43.11-2.99 0 0 .95-.3 3.11 1.16a10.8 10.8 0 015.66 0c2.16-1.46 3.1-1.16 3.1-1.16.62 1.56.23 2.71.12 2.99.72.79 1.15 1.8 1.15 3.03 0 4.34-2.64 5.3-5.16 5.58.4.35.76 1.04.76 2.1v3.1c0 .3.2.65.78.54A11.3 11.3 0 0012 .8z"/>',
        'layers':'<path d="m12 2 11 6-11 6L1 8zm-11 11 11 6 11-6M1 18l11 6 11-6"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/24})" color="{color}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</g>'


def pill(x,y,label,color=MINT,size=14,roomy=False):
    w=round(len(label)*size*.52+18)
    h=max(23,size+11) if roomy else 23
    return rect(x,y,w,h,'#0b1e29',8 if roomy else 9,color)+text(x+9,y+(size+2 if roomy else 16),label,size,color),w


def technology_panel(title,icons,mobile=False):
    w,h=(600,156) if mobile else (300,136)
    b=panel(w,h)+text(20 if mobile else 17,32 if mobile else 28,title,26 if mobile else 18,WHITE,650)
    step=144 if mobile else 72
    start=(w-step*len(icons))/2
    for i,(name,label) in enumerate(icons):
        center=start+(i+.5)*step
        size=44 if mobile else 36
        b+=embedded(A/f'icons/{name}.svg',center-size/2,52 if mobile else 49,size,size,'xMidYMid meet')
        b+=text(center,133 if mobile else 113,label,22.5 if mobile else 12.5,WHITE,extra='text-anchor="middle"')
    return b


def design():
    for mobile,w,h in [(False,1200,300),(True,600,650)]:
        b=panel(w,h)
        if mobile:
            b+=art('hero',1,1,598,284,'xMaxYMid slice')
            b+='<defs><linearGradient id="shade" x2="0" y2="1"><stop stop-color="#071321" stop-opacity="0"/><stop offset="1" stop-color="#071321"/></linearGradient></defs>'+rect(1,210,598,100,'url(#shade)',0)
            x,y=30,325
        else:
            b+=art('hero',375,1,824,298)
            b+='<defs><linearGradient id="shade"><stop offset=".28" stop-color="#071321"/><stop offset=".47" stop-color="#071321" stop-opacity=".95"/><stop offset=".65" stop-color="#071321" stop-opacity="0"/></linearGradient></defs>'+rect(1,1,1198,298,'url(#shade)',10)
            x,y=32,40
        b+=text(x,y,'$ whoami',19,MINT,600,extra='font-family="Consolas,monospace"')
        b+=text(x,y+45,'I build things to',40 if mobile else 39,WHITE,750)
        b+=text(x,y+90,'understand things.',40 if mobile else 39,'url(#accent)',750)
        b+=lines(SUBTITLE,x,y+123,43 if mobile else 50,22 if mobile else 17.5,WHITE,28 if mobile else 24)
        xx=x; yy=y+(232 if mobile else 211)
        for i,label in enumerate(['Backend','Cloud','AI Tools','DevOps','Learning by Building']):
            if mobile and i==4:xx=x; yy+=34
            p,pw=pill(xx,yy,label,[MINT,CYAN,VIOLET,VIOLET,CYAN][i],13)
            b+=p; xx+=pw+8
        b+=rect(1,1,w-2,h-2,'none',10,'#29455d')
        write('hero-mobile.svg' if mobile else 'hero.svg',svg(w,h,b,'I build things to understand things.',SUBTITLE))
    for name,label,url in CONTACTS:
        b=panel(180,46)+icon(name,22,11,25,WHITE if name=='github' else CYAN)+text(61,29,label,17,WHITE,600)
        write(f'social/{name}.svg',svg(180,46,b,label,url))
    for mobile,w,h in [(False,1200,122),(True,600,330)]:
        b=panel(w,h)
        # Moonlit ridgelines are vector illustration, never synthetic data.
        landscape='<circle cx="1060" cy="24" r="12" fill="#e0eaff" filter="url(#glow)"/><circle cx="1065" cy="20" r="12" fill="#091725"/>'
        landscape+='<path d="M760 122 827 80 857 94 914 35 963 78 997 63 1065 110 1122 87 1200 122" fill="#182c4c"/><path d="m865 122 49-87 49 43-37-21-12-9-12 25z" fill="#4c658e"/><path d="m750 122 119-24 40 17 59-30 60 37 78-29 94 29" fill="#07101d"/>'
        b+=f'<g opacity=".8" transform="translate({-600 if mobile else 0} {208 if mobile else 0})">{landscape}</g>'
        b+=f'<g filter="url(#glow)">{icon("bulb",24,28,48,MINT)}</g>'
        b+=text(92,40,"A Builder's Mindset",24,MINT,700)
        b+=lines(MINDSET,92,72 if mobile else 68,43 if mobile else 114,21 if mobile else 15.5,WHITE,29 if mobile else 25)
        if not mobile:b+=text(1028,57,'Same curiosity.',15,CYAN,extra='font-family="Segoe Print,cursive"')+text(1044,78,'New tools.',15,CYAN,extra='font-family="Segoe Print,cursive"')+text(1028,99,'Bigger possibilities.',14,CYAN,extra='font-family="Segoe Print,cursive"')
        write('mindset-mobile.svg' if mobile else 'mindset.svg',svg(w,h,b,"A Builder's Mindset",MINDSET))
    for mobile,w,h in [(False,1200,110),(True,600,302)]:
        b=panel(w,h)
        for i,(name,title,note) in enumerate(WORKFLOW):
            x=12+(i%2)*296 if mobile else 12+i*198
            y=12+(i//2)*96 if mobile else 12
            bw=280 if mobile else 186
            b+=rect(x,y,bw,84,'#091725',7,'#23475d')+icon(name,x+12,y+25,30,[MINT,CYAN,VIOLET,MINT,CYAN,MINT][i])
            b+=text(x+54,y+32,title,22 if mobile else 19,WHITE,650)
            b+=lines(note,x+54,y+53,21 if mobile else 19,19 if mobile else 13.5,WHITE,23 if mobile else 17)
            if i<5 and (not mobile or i%2==0):b+=text(x+bw+1,y+48,'›',22,CYAN)
        write('workflow-mobile.svg' if mobile else 'workflow.svg',svg(w,h,b,'How I Build',' → '.join(s[1] for s in WORKFLOW)))
    for slug,title,icons in TECH:
        b=technology_panel(title,icons)
        write(f'tech/{slug}.svg',svg(300,136,b,title,', '.join(t[1] for t in icons)))
    for mobile in [False,True]:
        w,h=(600,648) if mobile else (1232,136)
        b=''.join(f'<g transform="translate(0 {i*164})">{technology_panel(title,items,True)}</g>' if mobile else embedded(A/f'tech/{slug}.svg',i*308,0,300,136) for i,(slug,title,items) in enumerate(TECH))
        write('tech/stack-mobile.svg' if mobile else 'tech/stack.svg',svg(w,h,b,'Technology Stack','; '.join(title+': '+', '.join(i[1] for i in icons) for _,title,icons in TECH)))
    for mobile,w,h in [(False,1200,160),(True,600,220)]:
        b=embedded(A/'art/footer.jpg',0,0,w,h,'xMidYMid slice')
        b+='<defs><linearGradient id="shade"><stop stop-color="#06101b" stop-opacity=".88"/><stop offset=".65" stop-color="#06101b" stop-opacity="0"/></linearGradient></defs>'+rect(0,0,w,h,'url(#shade)',0)
        b+=text(30,65 if mobile else 70,'Better tools. Brighter ideas.',25,MINT,600,'font-family="Segoe Print,Georgia,serif" font-style="italic"')
        b+=text(45,100,'One useful thing at a time.',20,MINT,extra='font-family="Segoe Print,Georgia,serif" font-style="italic"')
        write('footer-mobile.svg' if mobile else 'footer.svg',svg(w,h,b,'Better tools. Brighter ideas. One useful thing at a time.','Existing mountain artwork, reused.'))


def project_cards(projects):
    for p in projects:
        if p['group']=='lab':continue
        featured=p['group']=='featured'
        for mobile in [False,True]:
            w,h=(600,466 if featured else 444) if mobile else (600,210) if featured else (420,344)
            b=panel(w,h)
            if mobile:ax,ay,aw,ah=2,2,596,240; x,y=24,278
            elif featured:ax,ay,aw,ah=2,2,270,206; x,y=290,35
            else:ax,ay,aw,ah=2,2,416,174; x,y=18,207
            b+=f'<defs><clipPath id="crop"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="9"/></clipPath></defs><g clip-path="url(#crop)">'+art(p['slug'],ax,ay,aw,ah,p.get('art_position','xMidYMid slice'))+'</g>'
            b+=text(x,y,p['name'],30 if mobile else 24,WHITE,700)
            if not p['private']:b+=text(w-19,y,'›',24,CYAN,extra='text-anchor="end"')
            tag,tw=pill(x,y+12,p['label'].split(' · ')[0],VIOLET if 'experiment' in p['label'] else CYAN if 'Learning' in p['label'] else MINT,21 if mobile else 14.5 if featured else 16,roomy=True)
            b+=tag
            if p['private']:
                tag,_=pill(x+tw+8,y+12,'Private · WIP' if 'WIP' in p['label'] else 'Private','#ffad99',20 if mobile else 14,roomy=True)
                b+=tag
            b+=lines(p['description'],x,y+(74 if mobile else 64),43 if mobile else 30 if featured else 36,24 if mobile else 18 if featured else 20,WHITE,30 if mobile else 24 if featured else 26)
            if featured:
                xx=x; yy=h-(42 if mobile else 35)
                for label in p['tags'][:3]:
                    ts=21 if mobile else 15.5
                    tw=len(label)*ts*.57+18
                    b+=rect(xx,yy,tw,ts+10,'#102236',6,'#315073')+text(xx+9,yy+ts+1,label,ts,WHITE)
                    xx+=tw+7
            b+=rect(1,1,w-2,h-2,'none',10,'#32627b')
            output=svg(w,h,b,p['name'],p['label']+'. '+p['description']+' Stack: '+', '.join(p['tags'])+'. Supplied conceptual artwork.')
            if not featured and not mobile:
                # Intrinsic desktop width allows three cards; the mobile source
                # has its own width and can fill the available README column.
                output=output.replace(f'width="{w}" height="{h}"',f'width="276" height="{h*276/w:.3f}"',1)
            write(f'projects/{p["slug"]}{"-mobile" if mobile else ""}.svg',output)


def stats(projects):
    data=json.loads((ROOT/'data/github-stats.json').read_text())
    repos=data['repositories']; selected=[r for r in repos if r['project']]
    langs,counts=Counter(),Counter()
    for r in selected:langs.update(r['language_bytes']); counts[r['primary_language'] or 'Unclassified']+=1
    date=data['generated_at'][:10]
    tools=sorted({label for _,_,items in TECH for _,label in items})
    summary=[(len(repos),'Public Repositories','cube'),(len(selected),'Project Repositories','folder'),(sum(p['group']=='featured' for p in projects),'Featured Projects','star'),(len(tools),'Languages / Tools','code')]
    for i,(value,label,name) in enumerate(summary):
        b=panel(294,92)+f'<circle cx="41" cy="46" r="25" fill="#071c26" stroke="{MINT if i%2 else CYAN}"/>'+icon(name,27,32,28,CYAN if i%2==0 else MINT)+text(81,44,value,33,WHITE,750)+text(81,67,label,16,WHITE)
        write(f'stats/summary-{i}.svg',svg(294,92,b,f'{value} {label}','Definitions in docs/METRICS.md; public API snapshot '+date if i<2 else 'Derived from reviewed profile configuration.'))
    for mobile in [False,True]:
        b=''
        for i,(value,label,name) in enumerate(summary):
            if mobile:
                x,y=(i%2)*302,(i//2)*148
                b+=f'<g transform="translate({x} {y})">'+panel(294,140)+icon(name,22,18,34,CYAN)+text(82,49,value,39,WHITE,750)
                words=label.rsplit(' ',1) if label!='Languages / Tools' else ['Languages /','Tools']
                b+=text(22,91,words[0],23,WHITE)+text(22,120,words[1],23,WHITE)+'</g>'
            else:b+=embedded(A/f'stats/summary-{i}.svg',i*302,0,294,92)
        write('stats/summary-mobile.svg' if mobile else 'stats/summary.svg',svg(596 if mobile else 1200,288 if mobile else 92,b,'Profile summary','; '.join(str(n)+' '+label for n,label,_ in summary)))
    total=sum(langs.values()); top=langs.most_common(4)
    if total-sum(n for _,n in top):top.append(('Other',total-sum(n for _,n in top)))
    b=panel(600,244)+text(20,30,'Languages by code volume',21,WHITE,650)
    offset=0; circumference=2*math.pi*66
    for i,(name,n) in enumerate(top):
        length=n/total*circumference; c=LANG_COLORS.get(name,'#9da8bb')
        b+=f'<circle cx="108" cy="135" r="66" fill="none" stroke="{c}" stroke-width="25" stroke-dasharray="{length} {circumference-length}" stroke-dashoffset="{-offset}" transform="rotate(-90 108 135)"/>'
        offset+=length
        b+=rect(215,65+i*29,12,12,c,4)+text(242,77+i*29,name,18,WHITE)+text(575,77+i*29,f'{100*n/total:.1f}%',18,WHITE,extra='text-anchor="end"')
    b+=text(20,226,'Public project code bytes · '+date+' UTC',13,MUTED)
    write('stats/languages.svg',svg(600,244,b,'Languages by code volume','; '.join(f'{k}: {v} bytes' for k,v in langs.most_common())))
    b=panel(600,244)+text(20,30,'Repositories by language',21,WHITE,650)
    for i,(name,n) in enumerate(counts.most_common()):
        y=51+i*23; c=LANG_COLORS.get(name,'#9da8bb')
        b+=rect(21,y,11,11,c,3)+text(44,y+12,name,16,WHITE)+rect(165,y+1,375*n/max(counts.values()),11,c,2)+text(555,y+12,n,16,WHITE)
    b+=text(20,226,'One primary language per public project · '+date,13,MUTED)
    write('stats/repositories.svg',svg(600,244,b,'Repositories by language','; '.join(f'{k}: {v}' for k,v in counts.most_common())))
    classification={p['repo']:p['category'] for p in projects}
    categories=Counter(classification.get(r['name'],'Unclassified') for r in selected)
    (ROOT/'data/stats-summary.json').write_text(json.dumps({'snapshot_date':date,'public_repositories':len(repos),'project_repositories':len(selected),'featured_projects':summary[2][0],'languages_tools':len(tools),'technology_list':tools,'language_bytes':dict(langs.most_common()),'repositories_by_primary_language':dict(counts.most_common()),'project_categories':dict(categories)},indent=2)+'\n')


def picture(path,alt,width='100%',mobile=None):
    sizing=f' width="{width}"' if width else ''
    img=f'<img src="assets/{path}.svg"{sizing} alt="{e(alt,quote=True)}" />'
    return f'<picture><source media="(max-width: 600px)" srcset="assets/{mobile}.svg" />{img}</picture>' if mobile else img


def readme(projects):
    summary=json.loads((ROOT/'data/stats-summary.json').read_text())
    content='<!-- Generated by scripts/build_profile.py. Edit the generator and data sources. -->\n\n'
    content+=picture('hero','Abhilash Kumar Giri. I build things to understand things. '+SUBTITLE,mobile='hero-mobile')+'\n\n'
    content+='<p align="center">\n'+'\n'.join(f'<a href="{url}">'+picture('social/'+name,label,'144')+'</a>' for name,label,url in CONTACTS)+'\n</p>\n\n'
    alt=f'{summary["public_repositories"]} public repositories; {summary["project_repositories"]} public project repositories; {summary["featured_projects"]} featured projects; {summary["languages_tools"]} distinct technologies shown. Definitions and snapshot date.'
    content+='<a href="docs/METRICS.md">'+picture('stats/summary',alt,mobile='stats/summary-mobile')+'</a>\n\n'
    content+=picture('mindset',"A Builder's Mindset. "+MINDSET,mobile='mindset-mobile')+'\n\n'
    for group,title in [('featured','✧ Featured Projects'),('more','◇ More to Explore')]:
        content+=f'### {title}\n\n<p align="center">\n'
        for p in projects:
            if p['group']!=group:continue
            alt=f'{p["name"]} | {p["label"]}. {p["description"]} Stack: '+', '.join(p['tags'])+'.'
            im=picture('projects/'+p['slug'],alt,'420' if group=='featured' else None,'projects/'+p['slug']+'-mobile')
            # Private repositories deliberately have no link or exploration arrow.
            content+=(im if p['private'] else f'<a href="https://github.com/Abhi-lash19/{p["repo"]}">{im}</a>')+'\n'
        content+='</p>\n\n'
    content+='### ↦ How I Build\n\n'+picture('workflow','Idea: a question or problem → Research: explore and plan → Design: shape the approach → Build: turn ideas into code → Verify: test and validate → Improve: refine and repeat.',mobile='workflow-mobile')+'\n\n'
    content+='### ◈ Tech Stack\n\n'+picture('tech/stack','; '.join(title+': '+', '.join(t[1] for t in items) for _,title,items in TECH),mobile='tech/stack-mobile')+'\n\n'
    content+='### ▥ GitHub Insights\n\n<p align="center">\n'
    for slug,key in [('languages','language_bytes'),('repositories','repositories_by_primary_language')]:
        alt=('Language bytes: ' if slug=='languages' else 'Repositories by primary language: ')+', '.join(f'{k}: {v}' for k,v in summary[key].items())
        content+='<a href="docs/METRICS.md">'+picture('stats/'+slug,alt,'420')+'</a>\n'
    content+='</p>\n\n[Snapshot '+summary['snapshot_date']+' · metric definitions](docs/METRICS.md) · [Accessible chart values](data/stats-summary.json)\n\n'
    content+='### ↝ Contribution Journey\n\n'
    # The fragment selects a static view of the SAME automatically updated file.
    content+='''<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg#reduced-motion" />
  <img src="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg" width="100%" alt="Animated snake following my real GitHub contribution grid. Updated daily; reduced-motion view shows the same calendar without animation." />
</picture>

'''
    content+=picture('footer','Better tools. Brighter ideas. One useful thing at a time.',mobile='footer-mobile')+'\n\n'
    content+='<details>\n<summary>About this workbench · artwork, access, and earlier projects</summary>\n\nSupplied artwork is conceptual, not an application screenshot. Private projects are shown without repository links; WIP means work in progress. Technologies reflect tools I use and explore, with different levels of familiarity.\n\n'
    for p in projects:
        if p['group']=='lab':content+=f'- [{p["name"]}](https://github.com/Abhi-lash19/{p["repo"]}) · {p["description"]}\n'
    content+='\n[Artwork and accessibility notes](docs/ASSETS.md) · [Project evidence](docs/PROJECT_RESEARCH.md)\n\n</details>\n'
    (ROOT/'README.md').write_text(content,encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--stats-only',action='store_true'); args=parser.parse_args()
    projects=json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))
    stats(projects)
    if not args.stats_only:design(); project_cards(projects)
    # Keep alt text and dates consistent with refreshed charts, even for stats-only.
    readme(projects)
    print('Generated cinematic README and self-contained panels')
