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
# Closed arcade maze. Last points carry the snake off-screen, then around the
# perimeter to the same entry point, keeping every body segment on one route.
ROUTE = [
    (48,64),(240,64),(240,112),(528,112),(528,64),(672,64),(672,160),
    (576,160),(576,208),(384,208),(384,160),(192,160),(48,160),
    (48,256),(192,256),(192,208),(336,208),(480,208),(480,256),(672,256),
    (752,256),(752,304),(760,304),(760,16),(48,16),(48,64),
]
PICKUPS = [1,2,3,4,5,6,7,8,9,10,11,12]
LOOP_SECONDS = 20
MOVE_END = 78
STEP = 28  # pixels between body segments


def distances():
    out = [0]
    for (x1,y1),(x2,y2) in zip(ROUTE,ROUTE[1:]):
        out.append(out[-1] + abs(x2-x1) + abs(y2-y1))
    return out


ROUTE_DISTANCES = distances()
ROUTE_LENGTH = ROUTE_DISTANCES[-1]


def point(distance):
    distance %= ROUTE_LENGTH
    for i, end in enumerate(ROUTE_DISTANCES[1:]):
        if distance <= end:
            (x1,y1),(x2,y2) = ROUTE[i],ROUTE[i+1]
            ratio = (distance - ROUTE_DISTANCES[i]) / (end - ROUTE_DISTANCES[i])
            return x1+(x2-x1)*ratio, y1+(y2-y1)*ratio
    return ROUTE[0]


def pickup_distance(index):
    return ROUTE_DISTANCES[PICKUPS[index]]

defs, css, food, body = [], [], [], []
for i, (name, slug, color) in enumerate(STACK):
    source = check_output(['gh', 'api', f'repos/simple-icons/simple-icons/contents/icons/{slug}.svg?ref=develop', '-H', 'Accept: application/vnd.github.raw+json'], timeout=30)
    root = ET.fromstring(source)
    paths = ''.join(f'<path d="{p.attrib["d"]}"/>' for p in root if p.tag.endswith('path'))
    defs.append(f'<symbol id="logo{i}" viewBox="0 0 24 24">{paths}</symbol>')
    d = pickup_distance(i)
    x, y = point(d)
    at = d / ROUTE_LENGTH * MOVE_END
    css.append(f'@keyframes food{i} {{0%,{at-0.35:.3f}%{{opacity:1}} {at:.3f}%,100%{{opacity:1}}}}')
    food.append(f'<g class="food" style="animation:food{i} {LOOP_SECONDS}s linear infinite"><title>{name}</title><rect x="{x-20}" y="{y-20}" width="40" height="40" rx="12" fill="#161b22" stroke="#30363d"/><use href="#logo{i}" x="{x-12}" y="{y-12}" width="24" height="24" fill="#{color}"/></g>')
    reveal = max(0, at - 1.6)
    css.append(f'@keyframes reveal{i} {{0%,{reveal:.3f}%{{opacity:0}} {reveal+0.2:.3f}%,{MOVE_END}%{{opacity:1}} 100%{{opacity:0}}}}')
    body.append(f'<g style="animation:reveal{i} {LOOP_SECONDS}s linear infinite"><g class="segment" style="animation:move{i+1} {LOOP_SECONDS}s linear infinite"><circle r="19" fill="#253a36" stroke="#658c7b"/><use href="#logo{i}" x="-11" y="-11" width="22" height="22" fill="#{color}"/></g></g>')

# Sample shared route distance. The common closed perimeter makes the loop seamless.
for i in range(13):
    offset = i * STEP
    frames = []
    for pct in range(MOVE_END + 1):
        x, y = point(pct / MOVE_END * ROUTE_LENGTH - offset)
        frames.append(f'{pct}%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    x, y = point(-offset)
    frames.append(f'100%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    css.append(f'@keyframes move{i}{{{"".join(frames)}}}')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">A retro arcade snake gathers the technologies I use: TypeScript, JavaScript, Vue, Python, Rust, Git, React, Three.js, Vite, Node.js, HTML and CSS.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
<defs>{''.join(defs)}</defs>
<style>
{''.join(css)}
.scene{{animation:scene {LOOP_SECONDS}s ease-in-out infinite}}
.message{{opacity:0;animation:message {LOOP_SECONDS}s ease-in-out infinite}}
@keyframes scene{{0%,100%{{opacity:0}}4%{{opacity:1}}90%{{opacity:1}}96%{{opacity:0}}}}
@keyframes message{{0%,64%,100%{{opacity:0}}68%{{opacity:1}}88%{{opacity:1}}94%{{opacity:0}}}}
@media(prefers-reduced-motion:reduce){{.scene,.message,.food{{animation:none!important}}.segment{{animation:none!important}}.snake{{display:none}}}}
</style>
<rect width="720" height="320" fill="#0d1117"/>
<path d="M48 64H672V160H48V256H672" fill="none" stroke="#21262d" stroke-width="1" stroke-dasharray="2 10"/>
<g class="scene">
{''.join(food)}
<g class="snake">{''.join(reversed(body))}
<g style="animation:move0 {LOOP_SECONDS}s linear infinite"><circle r="20" fill="#aac0ad"/><circle cx="-5" cy="-5" r="2.5" fill="#0d1117"/><circle cx="5" cy="-5" r="2.5" fill="#0d1117"/></g>
</g></g>
<text class="message" x="360" y="151" text-anchor="middle" fill="#f0c84b" font-family="monospace" font-size="12" letter-spacing="2">TECH I USE TO BUILD</text>
<text class="message" x="360" y="174" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="9" letter-spacing="1">SOFTWARE / DESIGN / PLAY</text>
</svg>'''
ET.fromstring(svg)
(ROOT / 'assets' / 'stack-snake.svg').write_text(svg, encoding='utf-8')
print(f'Generated stack-snake.svg with 12 logos and a {LOOP_SECONDS}-second loop.')



