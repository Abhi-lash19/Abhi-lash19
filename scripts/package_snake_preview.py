"""Optional QA packaging; Pillow only. Does not change artwork or production SVGs."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'.preview/snake-motion'
report=json.loads((folder/'capture.json').read_text())
samples=report['samples']
palette=Image.open(folder/samples[0]['file']).convert('RGB').quantize(colors=256)
frames=[Image.open(folder/s['file']).convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE) for s in samples]
times=[round(s['elapsed']/10)*10 for s in samples]+[round(report['duration']/10)*10]
delays=[max(10,b-a) for a,b in zip(times,times[1:])]
output=ROOT/'docs/previews/snake.gif'
frames[0].save(output,save_all=True,append_images=frames[1:],duration=delays,loop=0,optimize=True,disposal=1)
# Temporal contact sheet supplements the animated artifact and loop checks.
moments=[700,1700,3000,4500,8000,12000,20000,32000]
labels=['before','after'] if all((folder/f'before-{t}.png').exists() for t in moments) else ['after']
sheet=Image.new('RGB',(880*len(labels),len(moments)*220),'#071321')
draw=ImageDraw.Draw(sheet)
for row,t in enumerate(moments):
    for column,label in enumerate(labels):
        image=Image.open(folder/f'{label}-{t}.png').convert('RGB')
        sheet.paste(image,(column*880,row*220+28))
        draw.text((column*880+12,row*220+8),f'{label.upper()}   {t/1000:.1f}s',fill='#9eefd0')
sheet.save(ROOT/'docs/previews/snake-comparison.jpg',quality=93)
with Image.open(output) as gif:
    assert gif.n_frames>100
print(f'Packaged {len(frames)} real-time frames into {output.name}; temporal before/after sheet saved')
