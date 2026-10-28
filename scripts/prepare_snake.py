"""Recolor the existing output-branch animation without changing its path or data."""
import re
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
source = subprocess.check_output(['git','show','origin/output:github-contribution-grid-snake-dark.svg'], cwd=ROOT).decode()
assert '@keyframes' in source and 'animation' in source
palette = {'cb':'#183041','cs':'#68efb5','ce':'#0c2028','c0':'#0c2028','c1':'#124632','c2':'#1b7550','c3':'#32b879','c4':'#68efb5'}
for key, value in palette.items():
    source, count = re.subn(r'--'+key+r':[^;}]+', '--'+key+':'+value, source)
    assert count == 1, (key,count)
source = source.replace('</style>', '</style><rect x="-16" y="-32" width="880" height="192" rx="14" fill="#06101b"/>',1)
(ROOT/'assets/snake.svg').write_text(source,encoding='utf-8')
static=source.replace('</svg>','<style>*{animation:none!important}</style></svg>')
(ROOT/'assets/snake-static.svg').write_text(static,encoding='utf-8')
print('Retained original contribution geometry and animation keyframes; recolored palette only')
