"""Build the self-contained animated technology illustration."""
from base64 import b64encode
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'assets' / 'technologies-floating.svg'
symbol_source = (ROOT / 'assets' / 'technology-symbols.svg').read_text(encoding='utf-8')
logos = symbol_source[symbol_source.index('<defs><symbol'):symbol_source.index('</defs>') + 7]
art = b64encode((ROOT / 'assets' / 'technology-sea.png').read_bytes()).decode('ascii')
items = [
    ('TypeScript','#3178c6',320,327), ('JavaScript','#f7df1e',208,495),
    ('Vue','#4fc08d',568,215), ('Python','#77b5e8',815,220),
    ('Rust','#e7ad91',1090,205), ('Git','#f05032',1465,258),
    ('React','#61dafb',574,655), ('Three.js','#eee9df',770,682),
    ('Vite','#ac83ff',975,645), ('Node.js','#5fa04e',1210,661),
    ('HTML','#e34f26',1460,677), ('CSS','#b888f8',1615,516),
]
orbs = []
for i,(name,color,x,y) in enumerate(items):
    orbs.append(f'''<g transform="translate({x} {y})"><g class="float f{i%3}" style="animation-delay:-{i*.83:.2f}s"><title>{name}</title>
      <circle r="26" fill="#0e202b" fill-opacity=".91" stroke="#7ea0a4" stroke-opacity=".6"/>
      <path d="M-16-13Q-7-24 8-20" fill="none" stroke="#f5d3bf" stroke-opacity=".32" stroke-width="1.5" stroke-linecap="round"/>
      <use href="#logo{i}" x="-13" y="-13" width="26" height="26" fill="{color}"/>
    </g></g>''')
messages = ['DESIGN / BUILD','RESEARCH / TEST','USEFUL BY DESIGN']
caption = ''.join(f'<text class="caption c{i}" x="897" y="451" text-anchor="middle">{message}</text>' for i,message in enumerate(messages))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1774" height="887" viewBox="0 0 1774 887" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">Night-time overhead cargo ship illustration. Twelve technology logos float independently around the ship, and the dark cargo display cycles three short messages.</desc>
<!-- Technology marks: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
{logos}
<defs>
  <pattern id="led" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.45" fill="#ff9a81"/></pattern>
  <filter id="soft-glow" x="-20%" y="-100%" width="140%" height="300%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
.float{{animation:floatA 8s ease-in-out infinite}}
.float.f1{{animation-name:floatB;animation-duration:9.5s}}
.float.f2{{animation-name:floatC;animation-duration:7.2s}}
.caption{{fill:url(#led);font:700 30px 'Courier New',monospace;letter-spacing:3px;filter:url(#soft-glow);opacity:0;animation:caption 12s ease-in-out infinite}}
.c1{{animation-delay:4s}}.c2{{animation-delay:8s}}
@keyframes floatA{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(5px,-9px)}}}}
@keyframes floatB{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-7px,-6px)}}}}
@keyframes floatC{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(6px,7px)}}}}
@keyframes caption{{0%,27%{{opacity:1}}34%,100%{{opacity:0}}}}
@media(prefers-reduced-motion:reduce){{.float,.caption{{animation:none}}.c0{{opacity:1}}}}
</style>
<image width="1774" height="887" href="data:image/png;base64,{art}"/>
{''.join(orbs)}
{caption}
</svg>'''
ET.fromstring(svg)
TARGET.write_text(svg, encoding='utf-8')
print(f'Generated floating technology scene with {len(items)} logos.')
