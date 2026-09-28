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
# Hand-authored arcade route. Uneven timing and varied turns make pickups feel less linear.
ROUTE = [
    (48, 64, 0), (144, 64, 5), (240, 64, 9), (240, 112, 12),
    (384, 112, 17), (528, 112, 22), (528, 64, 25), (672, 64, 30),
    (672, 160, 35), (576, 160, 39), (576, 208, 42), (384, 208, 48),
    (384, 160, 51), (192, 160, 57), (48, 160, 62), (48, 256, 67),
    (192, 256, 71), (192, 208, 74), (336, 208, 79), (480, 208, 83),
    (480, 256, 86), (672, 256, 90), (752, 256, 94),
]
PICKUPS = [5, 9, 17, 22, 30, 35, 39, 48, 57, 67, 79, 86]
LOOP_END = 100
MOVE_END = 94
STEP = 2.6  # route percentage points between body segments


def point(progress):
    """Interpolate closed route coordinates, including the off-screen exit."""
    progress %= LOOP_END
    for (x1, y1, t1), (x2, y2, t2) in zip(ROUTE, ROUTE[1:]):
        if t1 <= progress <= t2:
            ratio = (progress - t1) / (t2 - t1)
            return x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio
    # Last route section wraps from the off-screen exit to the initial entry.
    x1, y1, t1 = ROUTE[-1]
    x2, y2, t2 = ROUTE[0][0], ROUTE[0][1], LOOP_END
    ratio = (progress - t1) / (t2 - t1)
    return x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio

defs, css, food, body = [], [], [], []
for i, (name, slug, color) in enumerate(STACK):
    source = check_output(['gh', 'api', f'repos/simple-icons/simple-icons/contents/icons/{slug}.svg?ref=develop', '-H', 'Accept: application/vnd.github.raw+json'], timeout=30)
    root = ET.fromstring(source)
    paths = ''.join(f'<path d="{p.attrib["d"]}"/>' for p in root if p.tag.endswith('path'))
    defs.append(f'<symbol id="logo{i}" viewBox="0 0 24 24">{paths}</symbol>')
    x, y = point(PICKUPS[i])
    consumed = PICKUPS[i] / MOVE_END * MOVE_END
    css.append(f'@keyframes food{i} {{0%,{consumed-0.35:.3f}%{{opacity:1}} {consumed:.3f}%,100%{{opacity:0}}}}')
    food.append(f'<g class="food" style="animation:food{i} 26s linear infinite"><title>{name}</title><rect x="{x-20}" y="{y-20}" width="40" height="40" rx="12" fill="#161b22" stroke="#30363d"/><use href="#logo{i}" x="{x-12}" y="{y-12}" width="24" height="24" fill="#{color}"/></g>')
    reveal = max(0, consumed - 1.5)
    css.append(f'@keyframes reveal{i} {{0%,{reveal:.3f}%{{opacity:0}} {reveal+0.2:.3f}%,{MOVE_END}%{{opacity:1}} 100%{{opacity:0}}}}')
    body.append(f'<g style="animation:reveal{i} 26s linear infinite"><g class="segment" style="animation:move{i+1} 26s linear infinite"><circle r="19" fill="#253a36" stroke="#658c7b"/><use href="#logo{i}" x="-11" y="-11" width="22" height="22" fill="#{color}"/></g></g>')

# Derive body keyframes from shared progress samples so each segment follows the head path.
for i in range(13):
    offset = i * STEP
    times = {0, MOVE_END, *[t for _, _, t in ROUTE if t <= MOVE_END]}
    times.update(range(0, MOVE_END, 1))
    frames = []
    for progress in sorted(times):
        x, y = point(progress - offset)
        frames.append(f'{progress:.3f}%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    # Hold at the exit while the caption takes over the board.
    frames.append('100%{transform:translate(752px,256px)}')
    css.append(f'@keyframes move{i}{{{"".join(frames)}}}')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">A retro arcade snake gathers the technologies I use: TypeScript, JavaScript, Vue, Python, Rust, Git, React, Three.js, Vite, Node.js, HTML and CSS.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
<defs>{''.join(defs)}</defs>
<style>
{''.join(css)}
.scene{{animation:scene 26s linear infinite}}
.message{{opacity:0;animation:message 26s ease-in-out infinite}}
@keyframes scene{{0%,94%{{opacity:1}}96%,99%{{opacity:0}}100%{{opacity:1}}}}
@keyframes message{{0%,94%,100%{{opacity:0}}95%,98%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{.scene,.message,.food{{animation:none!important}}.snake{{display:none}}}}
</style>
<rect width="720" height="320" fill="#0d1117"/>
<path d="M48 64H672V160H48V256H672" fill="none" stroke="#21262d" stroke-width="1" stroke-dasharray="2 10"/>
<g class="scene">
{''.join(food)}
<text class="message" x="360" y="151" text-anchor="middle" fill="#f0c84b" font-family="monospace" font-size="12" letter-spacing="2">TECH I USE TO BUILD</text>
<text class="message" x="360" y="174" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="9" letter-spacing="1">SOFTWARE / DESIGN / PLAY</text>
<g class="snake">{''.join(reversed(body))}
<g style="animation:move0 26s linear infinite"><circle r="20" fill="#aac0ad"/><circle cx="-5" cy="-5" r="2.5" fill="#0d1117"/><circle cx="5" cy="-5" r="2.5" fill="#0d1117"/></g>
</g></g>
</svg>'''
ET.fromstring(svg)
(ROOT / 'assets' / 'stack-snake.svg').write_text(svg, encoding='utf-8')
print('Generated stack-snake.svg with 12 logos and a 26-second loop.')

