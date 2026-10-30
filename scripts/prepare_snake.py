"""Style Platane/snk output without altering contribution cells or movement keyframes.

Usage: python scripts/prepare_snake.py --input path.svg --output-dir dist
Without arguments, reads the preserved real output snapshot for a local preview.
"""
import argparse
from bisect import bisect_right
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PALETTE={'cb':'#173c36','cs':'#68efb5','ce':'#0b2527','c0':'#0b2527','c1':'#164f3b','c2':'#247b50','c3':'#39b574','c4':'#82f5b0'}
NS={'s':'http://www.w3.org/2000/svg'}


def head_route(source):
    """Decode the existing compressed CSS route; timestamps remain authoritative."""
    match=re.search(r'@keyframes s0\{((?:[^{}]*\{[^{}]*\})+)\}',source)
    if not match:raise ValueError('Missing real head route')
    points={}
    for percentages,x,y in re.findall(r'([\d.,%]+)\{transform:translate\((-?[\d.]+)px,(-?[\d.]+)px\)\}',match[1]):
        for percentage in percentages.split(','):
            points[float(percentage.rstrip('%'))/100]=(float(x),float(y))
    if 0 not in points:raise ValueError('Route has no initial position')
    points[1]=points[0]
    times=sorted(points)
    def position(t):
        t=t%1
        index=max(0,bisect_right(times,t)-1)
        a,b=times[index],times[index+1]
        fraction=(t-a)/(b-a)
        return tuple(points[a][axis]+fraction*(points[b][axis]-points[a][axis]) for axis in (0,1))
    return position


def skin_keyframes(source,seconds):
    """Round only the drawn skin's corners within a few pixels of the real route.

    The three-point time filter is symmetric, so it does not shift activity
    timing. Dense linear keyframes avoid easing pauses at each calendar cell.
    """
    route=head_route(source)
    window=.045/seconds
    def smooth(t):
        before,center,after=route(t-window),route(t),route(t+window)
        return tuple(.25*before[j]+.5*center[j]+.25*after[j] for j in (0,1))
    frames=[]; angle=0
    steps=max(600,min(3600,math.ceil(seconds*30)))
    for i in range(steps+1):
        t=i/steps; x,y=smooth(t)
        behind,ahead=smooth(t-.012/seconds),smooth(t+.012/seconds)
        dx,dy=ahead[0]-behind[0],ahead[1]-behind[1]
        if math.hypot(dx,dy)>.001:
            heading=math.degrees(math.atan2(dy,dx))
            angle+=(heading-angle+180)%360-180
        frames.append(f'{100*t:.5f}%{{transform:translate({x+8:.3f}px,{y+8:.3f}px) rotate({angle:.2f}deg)}}')
    return '@keyframes skin-motion{'+''.join(frames)+'}'


def enhance(source):
    if 'id="cinematic-snake"' in source:
        raise ValueError('Already styled; use the unmodified Platane/snk output')
    tree=ET.fromstring(source)
    view=list(map(float,tree.attrib['viewBox'].split()))
    if view != [-16,-32,880,192]:
        raise ValueError(f'Unexpected snk geometry {view}; review renderer before publishing')
    assert '@keyframes s0{' in source and 'class="s s0"' in source
    duration=re.search(r'\.s\{[^}]*?([\d.]+)ms',source)
    if not duration:raise ValueError('Missing snake animation duration')
    seconds=float(duration[1])/1000
    for key,value in PALETTE.items():
        source,count=re.subn(r'--'+key+r':[^;}]+','--'+key+':'+value,source)
        if count!=1:raise ValueError(f'Expected exactly one palette variable {key}')
    motion=skin_keyframes(source,seconds)
    defs='''<defs><linearGradient id="head-skin" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#c0fbdc"/><stop offset=".4" stop-color="#74e5b3"/><stop offset="1" stop-color="#319969"/></linearGradient><filter id="snake-glow" x="-30%" y="-50%" width="160%" height="200%"><feDropShadow dx="0" dy="0" stdDeviation="1.4" flood-color="#76f7be" flood-opacity=".45"/></filter><filter id="body-surface" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur in="SourceAlpha" stdDeviation="1.1" result="relief"/><feSpecularLighting in="relief" surfaceScale="2" specularConstant=".38" specularExponent="16" lighting-color="#d3ffe8" result="light"><feDistantLight azimuth="235" elevation="50"/></feSpecularLighting><feComposite in="light" in2="SourceAlpha" operator="in" result="shine"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="shine"/></feMerge></filter><linearGradient id="night" x2="0" y2="1"><stop stop-color="#0a1d26"/><stop offset="1" stop-color="#051219"/></linearGradient></defs>'''
    background='<g id="cinematic-snake"><rect x="-15" y="-31" width="878" height="190" rx="12" fill="url(#night)" stroke="#285347"/><path d="M-16 160v-20l14-13 15 21 13-16 19 28M770 160l19-20 13 7 24-24 16 14 22-24v47" fill="#10352e"/><text x="670" y="147" font-family="Georgia,serif" font-style="italic" font-size="13" fill="#87cdb3">Keep building</text></g>'
    source=source.replace('</style>','</style>'+defs+background,1)
    # Keep original .s elements/keyframes for auditability. The skin follows a
    # locally rounded version of that timed route; it never changes grid activity.
    css=f'.s,.u{{visibility:hidden}}.trail{{fill:#4fc997;stroke:none;animation:skin-motion {seconds}s linear infinite}}'+motion
    trail='<g filter="url(#body-surface)">'
    for i in range(96,-1,-1):
        lag=i*.8/96
        radius=.9+6.3*(1-i/96)**.7
        trail+=f'<g class="trail" style="animation-delay:{-seconds+lag:.5f}s"><circle r="{radius:.3f}"/></g>'
    trail+='</g>'
    trail+=f'''<g class="trail snake-head" style="animation-delay:{-seconds}s"><path d="M-8-5C-4-7 4-8 8-4Q12 0 8 4C4 8-4 7-8 5Z" fill="url(#head-skin)" stroke="#a3f4cf" stroke-width=".45"/><ellipse cx="3" cy="-4" rx="1.7" ry="2" fill="#05251c"/><ellipse cx="3" cy="4" rx="1.7" ry="2" fill="#05251c"/><circle cx="3.7" cy="-4.5" r=".6" fill="#ecfff4"/><circle cx="3.7" cy="3.5" r=".6" fill="#ecfff4"/><path d="M7-1Q9 0 7 1" fill="none" stroke="#277b59" stroke-width=".6"/></g>'''
    reduced='*{animation:none!important}.trail,.s,.u{display:none}'
    # An explicit fragment also works where image documents do not inherit the
    # embedding page's motion preference. The README selects it using picture.
    source=source.replace('<svg ', '<svg id="reduced-motion" ', 1)
    css+='svg:target *{animation:none!important}svg:target .trail,svg:target .s,svg:target .u{display:none}'
    source=source.replace('</svg>',f'<style>{css}@media(prefers-reduced-motion:reduce){{{reduced}}}</style><g id="snake-skin-layer" filter="url(#snake-glow)">{trail}</g></svg>')
    # Static cells use their original activity color, before consumption begins.
    static=source.replace('</svg>','<style>'+reduced+'</style></svg>')
    return source,static


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--input',type=Path); parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    source=(args.input or ROOT/'assets/source/contribution-snake.svg').read_text(encoding='utf-8')
    animated,static=enhance(source)
    folder=args.output_dir or ROOT/'assets'; folder.mkdir(parents=True,exist_ok=True)
    animated_name='github-contribution-grid-snake-dark.svg' if args.output_dir else 'snake.svg'
    static_name='github-contribution-grid-snake-static.svg' if args.output_dir else 'snake-static.svg'
    (folder/animated_name).write_text(animated,encoding='utf-8')
    (folder/static_name).write_text(static,encoding='utf-8')
    print('Preserved all contribution cells and movement keyframes; wrote glowing animation and matching reduced-motion calendar')


if __name__=='__main__':main()
