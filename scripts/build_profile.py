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
    ('cloud','Serverless on AWS','At work',[('amazonwebservices','AWS'),('aws-lambda','Lambda'),('aws-api-gateway','API Gateway'),('aws-s3','S3'),('aws-dynamodb','DynamoDB')]),
    ('operations','Delivery, data & monitoring','At work',[('azuredevops','Azure DevOps'),('mysql','MySQL'),('aws-cloudwatch','CloudWatch'),('datadog-icon','Datadog')]),
    ('languages','Languages & databases','Project work',[('python','Python'),('typescript','TypeScript'),('javascript','JavaScript'),('@database','SQL'),('postgresql','PostgreSQL'),('sqlite','SQLite')]),
    ('backend','Services & containers','Project work',[('nodejs','Node.js'),('express','Express'),('fastapi','FastAPI'),('@route','REST'),('graphql','GraphQL'),('docker','Docker')]),
    ('systems','Systems & delivery','Learning lab',[('java','Java'),('terraform','Terraform'),('kubernetes','Kubernetes'),('githubactions','CI/CD')]),
    ('ai','Models & retrieval','Learning lab',[('@model','LLMs'),('@retrieval','RAG'),('@network','FAISS'),('@vector','Vector search'),('pytorch','PyTorch'),('@code','AI coding tools')]),
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
        'database':'<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0"/>',
        'route':'<path d="M2 7h18l-4-4m6 14H4l4 4"/><circle cx="4" cy="7" r="2"/><circle cx="20" cy="17" r="2"/>',
        'model':'<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 6 9-6m-9 6v9M7 4l10 6"/>',
        'retrieval':'<path d="M3 2h12l4 4v5M3 2v19h8M6 7h8M6 11h5"/><circle cx="16" cy="16" r="4"/><path d="m19 19 4 4"/>',
        'network':'<path d="m4 17 6-12 11 8-17 4 9 4 8-8"/><g fill="currentColor"><circle cx="4" cy="17" r="2"/><circle cx="10" cy="5" r="2"/><circle cx="21" cy="13" r="2"/><circle cx="13" cy="21" r="2"/></g>',
        'vector':'<path d="M3 2v19h19M6 17 19 5m-6 0h6v6"/><circle cx="9" cy="9" r="1"/><circle cx="17" cy="16" r="1"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/24})" color="{color}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</g>'


def pill(x,y,label,color=MINT,size=14,roomy=False):
    w=round(len(label)*size*.52+18)
    h=max(23,size+11) if roomy else 23
    return rect(x,y,w,h,'#0b1e29',8 if roomy else 9,color)+text(x+9,y+(size+2 if roomy else 16),label,size,color),w


def technology_panel(title, context, items, mobile=False):
    columns = 2 if mobile else 3
    row_height = 62 if mobile else 55
    height = 82 + math.ceil(len(items)/columns)*row_height
    color = {'At work': MINT, 'Project work': CYAN, 'Learning lab': VIOLET}[context]
    body = panel(600,height) + rect(18,18,4,43,color,2)
    body += text(36,31,context.upper(),19 if mobile else 15,color,650)
    body += text(36,62,title,29 if mobile else 26,WHITE,700)
    step = 564 / columns
    for index,(name,label) in enumerate(items):
        x = 18 + (index % columns)*step
        y = 77 + (index // columns)*row_height
        size = 40 if mobile else 36
        if name.startswith('@'):
            body += icon(name[1:],x+4,y+4,size-5,color)
        else:
            if name in {'express','amazonwebservices','mysql','datadog-icon'}:
                body += rect(x,y,size,size,'#e1eaf0',6)
            body += embedded(A/f'icons/{name}.svg',x+3,y+3,size-6,size-6,'xMidYMid meet')
        body += text(x+size+8,y+size*.72,label,24 if mobile else 19,WHITE,500)
    return body,height


def tech_stack():
    for mobile in (False, True):
        columns = 1 if mobile else 2
        y = 0
        rows = []
        for start in range(0,len(TECH),columns):
            row_height = 0
            for column,(slug,title,context,items) in enumerate(TECH[start:start+columns]):
                body,height = technology_panel(title,context,items,mobile)
                if not mobile:
                    write(f'tech/{slug}.svg',svg(600,height,body,title,context+'. '+', '.join(label for _,label in items)))
                rows.append(f'<g transform="translate({column*612} {y})">{body}</g>')
                row_height = max(row_height,height)
            y += row_height+12
        write('tech/stack-mobile.svg' if mobile else 'tech/stack.svg',
              svg(600 if mobile else 1212,y-12,''.join(rows),'My tech stack',tech_description()))


def tech_description():
    return '. '.join(f'{context}, {title}: '+', '.join(label for _,label in items)
                     for _,title,context,items in TECH)


def mindset_panel(mobile):
    w,h = (420,365) if mobile else (1000,202)
    scene = '<defs><linearGradient id="twilight" x2="0" y2="1"><stop stop-color="#0c2034"/><stop offset=".62" stop-color="#233852"/><stop offset="1" stop-color="#162239"/></linearGradient></defs>'
    scene += rect(0,0,400,190,'url(#twilight)',0)
    for x,y in [(32,24),(60,57),(93,36),(121,19),(157,62),(177,32),(223,12),(240,48),(265,29),(344,56),(369,24)]:
        scene += f'<circle cx="{x}" cy="{y}" r="1.2" fill="#b6cadc"/>'
    scene += '<circle cx="306" cy="41" r="13" fill="#ddf4f3" filter="url(#glow)"/><circle cx="312" cy="36" r="12" fill="#10283d"/>'
    scene += '<path d="M0 123 58 88 86 103 133 74 169 98 211 55 251 86 284 63 327 104 357 85 400 109V190H0Z" fill="#435873"/><path d="m179 91 32-36 40 31-27-13-10-9-8 12-4-2zM267 77l17-14 19 19-17-9-6 3z" fill="#a2c1d1"/>'
    scene += '<path d="M0 142 55 108 110 134 169 102 216 123 260 97 317 118 357 105 400 122V190H0Z" fill="#203b50"/><path d="M0 160Q83 136 150 158T288 147L400 123V190H0Z" fill="#0c2633"/><path d="M177 190q75-21 44-28t52-16q-30 4-15 9t-10 14l-28 21" fill="#346171"/>'
    for x,y,k in [(7,170,.9),(30,164,.7),(53,175,1.1),(81,160,.65),(103,177,.9),(324,165,.8),(346,174,1.05),(370,168,1.25),(392,160,1.15)]:
        scene += f'<path transform="translate({x} {y}) scale({k})" d="M0-39-7-20h4l-9 11h6l-11 12h14v14h5V3h14L6-9h5L3-20h4Z" fill="#071b24"/>'
    x,y,sw,sh = (1,240,418,124) if mobile else (667,1,332,200)
    body = panel(w,h)+f'<svg x="{x}" y="{y}" width="{sw}" height="{sh}" viewBox="0 0 400 190" preserveAspectRatio="xMidYMid slice">{scene}</svg>'
    direction = 'x2="0" y2="1"' if mobile else 'x2="1" y2="0"'
    body += f'<defs><linearGradient id="haze" {direction}><stop stop-color="#0a1725"/><stop offset="1" stop-color="#0a1725" stop-opacity="0"/></linearGradient></defs>'
    body += rect(x,y,sw if mobile else 70,30 if mobile else sh,'url(#haze)',0)
    body += '<circle cx="41" cy="39" r="24" fill="#0e3033" stroke="#28715e"/><g filter="url(#glow)">'+icon('bulb',27,24,29,MINT)+'</g>'
    body += text(80,47,"A Builder's Mindset",27 if mobile else 29,MINT,700)
    body += lines(MINDSET,22 if mobile else 28,87 if mobile else 89,43 if mobile else 73,18 if mobile else 19,WHITE,25 if mobile else 27)
    body += rect(1,1,w-2,h-2,'none',10,'#325366')
    return svg(w,h,body,"A Builder's Mindset",MINDSET)


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
    write('mindset.svg',mindset_panel(False))
    write('mindset-mobile.svg',mindset_panel(True))
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
    tech_stack()
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
            w,h=(600,482 if featured else 460) if mobile else (600,220) if featured else (420,360)
            b=panel(w,h)
            if mobile:ax,ay,aw,ah=2,2,596,252; x,y=24,291
            elif featured:ax,ay,aw,ah=2,2,284,216; x,y=302,36
            else:ax,ay,aw,ah=2,2,416,186; x,y=18,221
            b+=f'<defs><clipPath id="crop"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="9"/></clipPath></defs><g clip-path="url(#crop)">'+art(p['slug'],ax,ay,aw,ah,p.get('art_position','xMidYMid slice'))+'</g>'
            b+=text(x,y,p['name'],30 if mobile else 24,WHITE,700)
            if not p['private']:b+=text(w-19,y,'›',24,CYAN,extra='text-anchor="end"')
            tag,tw=pill(x,y+12,p['label'].split(' · ')[0],VIOLET if 'experiment' in p['label'] else CYAN if 'Learning' in p['label'] else MINT,21 if mobile else 14.5 if featured else 16,roomy=True)
            b+=tag
            if p['private']:
                tag,_=pill(x+tw+8,y+12,'Private · WIP' if 'WIP' in p['label'] else 'Private','#ffad99',20 if mobile else 14,roomy=True)
                b+=tag
            b+=lines(p['description'],x,y+(74 if mobile else 64),43 if mobile else 29 if featured else 36,24 if mobile else 18.5 if featured else 20,WHITE,30 if mobile else 24 if featured else 26)
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


def language_charts(top,total,counts,date,mobile):
    w = 420 if mobile else 600
    h = max(252 if mobile else 244,90+23*len(counts))
    cx,cy,r = (73,130,46) if mobile else (108,135,66)
    legend = 142 if mobile else 215
    body = panel(w,h)+text(18,31,'Languages by code volume',21,WHITE,650)
    circumference = 2*math.pi*r
    offset = 0
    for i,(name,n) in enumerate(top):
        length = n/total*circumference
        color = LANG_COLORS.get(name,'#9da8bb')
        body += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{19 if mobile else 25}" stroke-dasharray="{length} {circumference-length}" stroke-dashoffset="{-offset}" transform="rotate(-90 {cx} {cy})"/>'
        offset += length
        y = 73+i*29
        body += rect(legend,y-11,11,11,color,3)+text(legend+23,y,name,18,WHITE)+text(w-20,y,f'{100*n/total:.1f}%',18,WHITE,extra='text-anchor="end"')
    body += text(18,h-14,'Public project code bytes · '+date,15,MUTED)
    suffix = '-mobile' if mobile else ''
    write(f'stats/languages{suffix}.svg',svg(w,h,body,'Languages by code volume'))
    body = panel(w,h)+text(18,31,'Repositories by language',21,WHITE,650)
    left = 145 if mobile else 165
    for i,(name,n) in enumerate(counts.most_common()):
        y = 52+i*23
        color = LANG_COLORS.get(name,'#9da8bb')
        body += rect(18,y,10,10,color,3)+text(39,y+11,name,17,WHITE)+rect(left,y+1,(w-left-54)*n/max(counts.values()),11,color,2)+text(w-25,y+11,n,17,WHITE)
    body += text(18,h-14,'Primary language per project · '+date,15,MUTED)
    write(f'stats/repositories{suffix}.svg',svg(w,h,body,'Repositories by primary language'))


def commit_data():
    return json.loads((ROOT/'data/commit-stats.json').read_text(encoding='utf-8'))


def commit_description():
    d = commit_data()
    return (f"{d['year_to_date']} commits authored in {d['year']}, {d['monthly_average']:.1f} per month across "
            f"{d['elapsed_calendar_months']} elapsed calendar months, and {d['lifetime']} lifetime. "
            f"Distinct commits linked to my GitHub author ID on default branches of my {len(d['repositories'])} "
            f"owned public non-fork repositories, as of {d['as_of'][:10]}.")


def commit_panels():
    d = commit_data()
    metrics = [(str(d['year_to_date']),f"Commits in {d['year']}",MINT),
               (f"{d['monthly_average']:.1f}",f"Monthly average · {d['elapsed_calendar_months']} months",CYAN),
               (str(d['lifetime']),'Lifetime commits',VIOLET)]
    for mobile in (False,True):
        w,h = (420,316) if mobile else (1000,186)
        body = panel(w,h)+text(20,35,'Authored commits',24,WHITE,700)
        body += text(w-20,34,d['as_of'][:10],15,MUTED,extra='text-anchor="end"')
        scope = f"{len(d['repositories'])} owned public repos · default branches · forks excluded"
        if mobile:
            body += text(20,63,f"{len(d['repositories'])} owned public repos · forks excluded",17,MUTED)
            body += text(20,85,'Default-branch history',17,MUTED)
        else:body += text(20,62,scope,17,MUTED)
        for i,(value,label,color) in enumerate(metrics):
            x,y = (16,101+68*i) if mobile else (16+325*i,78)
            width,height = (388,60) if mobile else (318,91)
            body += rect(x,y,width,height,'#091a27',7,'#274859')+rect(x+9,y+11,3,height-22,color,1)
            if mobile:
                body += text(x+22,y+36,label,18,WHITE,550)+text(x+width-15,y+41,value,32,color,700,extra='text-anchor="end"')
            else:
                body += text(x+24,y+42,value,37,color,700)+text(x+24,y+72,label,19,WHITE)
        write('stats/commits-mobile.svg' if mobile else 'stats/commits.svg',svg(w,h,body,'Authored commits',commit_description()))


def stats(projects):
    data=json.loads((ROOT/'data/github-stats.json').read_text())
    repos=data['repositories']; selected=[r for r in repos if r['project']]
    langs,counts=Counter(),Counter()
    for r in selected:langs.update(r['language_bytes']); counts[r['primary_language'] or 'Unclassified']+=1
    date=data['generated_at'][:10]
    tools=sorted({label for _,_,_,items in TECH for _,label in items})
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
    for mobile in (False,True):
        language_charts(top,total,counts,date,mobile)
    commit_panels()
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
    alt=f'{summary["public_repositories"]} public repositories; {summary["project_repositories"]} public project repositories; {summary["featured_projects"]} featured projects; {summary["languages_tools"]} distinct technologies shown.'
    content+=picture('stats/summary',alt,mobile='stats/summary-mobile')+'\n\n'
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
    content+='### ◈ Tech Stack\n\n'+picture('tech/stack',tech_description(),mobile='tech/stack-mobile')+'\n\n'
    content+='### ▥ GitHub Insights\n\n'+picture('stats/commits',commit_description(),mobile='stats/commits-mobile')+'\n\n<p align="center">\n'
    for slug,key in [('languages','language_bytes'),('repositories','repositories_by_primary_language')]:
        alt=('Language bytes: ' if slug=='languages' else 'Repositories by primary language: ')+', '.join(f'{k}: {v}' for k,v in summary[key].items())
        content+='<a href="docs/METRICS.md">'+picture('stats/'+slug,alt,'420',mobile='stats/'+slug+'-mobile')+'</a>\n'
    content+='</p>\n\n'
    content+='### ↝ Contribution Journey\n\n'
    # The fragment selects a static view of the SAME automatically updated file.
    content+='''<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg#reduced-motion" />
  <img src="https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg" width="100%" alt="Animated snake following my real GitHub contribution grid. Updated daily; reduced-motion view shows the same calendar without animation." />
</picture>

'''
    content+=picture('footer','Better tools. Brighter ideas. One useful thing at a time.',mobile='footer-mobile')+'\n'
    (ROOT/'README.md').write_text(content,encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--stats-only',action='store_true'); args=parser.parse_args()
    projects=json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))
    stats(projects)
    if not args.stats_only:design(); project_cards(projects)
    # Keep alt text and dates consistent with refreshed charts, even for stats-only.
    readme(projects)
    print('Generated cinematic README and self-contained panels')
