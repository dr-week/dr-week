"""Generate a self-contained SVG animation using Simple Icons (CC0)."""
from pathlib import Path
from subprocess import check_output
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STACK = [
    ('TypeScript', 'typescript', '3178C6'), ('JavaScript', 'javascript', 'F7DF1E'),
    ('Vue', 'vuedotjs', '4FC08D'), ('Python', 'python', '77B5E8'),
    ('Rust', 'rust', 'E7AD91'), ('Git', 'git', 'F05032'),
    ('React', 'react', '61DAFB'), ('Three.js', 'threedotjs', 'FFFFFF'),
    ('Vite', 'vite', 'AC83FF'), ('Node.js', 'nodedotjs', '5FA04E'),
    ('HTML', 'html5', 'E34F26'), ('CSS', 'css', 'B888F8'),
]
DISTANCES = [96, 240, 384, 528, 816, 960, 1104, 1248, 1536, 1680, 1824, 1968]
LENGTH = 2064

def point(d):
    d = max(0, min(LENGTH, d))
    if d <= 624: return 48 + d, 64
    if d <= 720: return 672, 64 + d - 624
    if d <= 1344: return 672 - (d - 720), 160
    if d <= 1440: return 48, 160 + d - 1344
    return 48 + d - 1440, 256

defs, css, food, body = [], [], [], []
for i, (name, slug, color) in enumerate(STACK):
    source = check_output(['gh', 'api', f'repos/simple-icons/simple-icons/contents/icons/{slug}.svg?ref=develop', '-H', 'Accept: application/vnd.github.raw+json'], timeout=30)
    root = ET.fromstring(source)
    paths = ''.join(f'<path d="{p.attrib["d"]}"/>' for p in root if p.tag.endswith('path'))
    defs.append(f'<symbol id="logo{i}" viewBox="0 0 24 24">{paths}</symbol>')
    x, y = point(DISTANCES[i])
    consumed = DISTANCES[i] / LENGTH * 90
    css.append(f'@keyframes food{i} {{0%,{consumed-.05:.3f}%{{opacity:1}} {consumed:.3f}%,100%{{opacity:0}}}}')
    food.append(f'<g class="food" style="animation:food{i} 26s linear infinite"><title>{name}</title><rect x="{x-20}" y="{y-20}" width="40" height="40" rx="12" fill="#161b22" stroke="#30363d"/><use href="#logo{i}" x="{x-12}" y="{y-12}" width="24" height="24" fill="#{color}"/></g>')
    css.append(f'@keyframes reveal{i} {{0%,{consumed-.05:.3f}%{{opacity:0}} {consumed:.3f}%,100%{{opacity:1}}}}')
    body.append(f'<g style="animation:reveal{i} 26s linear infinite"><g class="segment" style="animation:move{i+1} 26s linear infinite"><circle r="19" fill="#253a36" stroke="#658c7b"/><use href="#logo{i}" x="-11" y="-11" width="22" height="22" fill="#{color}"/></g></g>')

# Include every path corner and each segment's corner crossing for exact turns.
for i in range(13):
    offset = i * 36
    distances = sorted({0, LENGTH, *range(0, LENGTH, 24), *[min(LENGTH, c+offset) for c in [0,624,720,1344,1440]]})
    frames = []
    for d in distances:
        x, y = point(d-offset)
        frames.append(f'{d/LENGTH*90:.4f}%{{transform:translate({x}px,{y}px)}}')
    x, y = point(LENGTH-offset)
    frames.append(f'100%{{transform:translate({x}px,{y}px)}}')
    css.append(f'@keyframes move{i}{{{"".join(frames)}}}')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">A snake collects twelve technology logos and grows. TypeScript, JavaScript, Vue, Python, Rust, Git, React, Three.js, Vite, Node.js, HTML and CSS.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
<defs>{''.join(defs)}</defs>
<style>
{''.join(css)}
.scene{{animation:scene 26s linear infinite}}
@keyframes scene{{0%,93%{{opacity:1}}97%,99%{{opacity:0}}100%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{.scene,.food{{animation:none!important}}.snake{{display:none}}}}
</style>
<rect width="720" height="320" fill="#0d1117"/>
<path d="M48 64H672V160H48V256H672" fill="none" stroke="#21262d" stroke-width="1" stroke-dasharray="2 10"/>
<g class="scene">
{''.join(food)}
<g class="snake">{''.join(reversed(body))}
<g style="animation:move0 26s linear infinite"><circle r="20" fill="#aac0ad"/><circle cx="-5" cy="-5" r="2.5" fill="#0d1117"/><circle cx="5" cy="-5" r="2.5" fill="#0d1117"/></g>
</g></g>
</svg>'''
ET.fromstring(svg)
(ROOT / 'assets' / 'stack-snake.svg').write_text(svg, encoding='utf-8')
print('Generated stack-snake.svg with 12 logos and a 26-second loop.')
