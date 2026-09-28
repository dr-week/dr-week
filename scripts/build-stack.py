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
    (576,160),(576,208),(384,208),(384,136),(288,136),(288,184),
    (192,184),(48,184),(48,256),(192,256),(192,208),(336,208),(480,208),(480,256),(672,256),
    (752,256),(752,304),(760,304),(760,16),(48,16),(48,64),
]
PICKUPS = [1,2,3,4,5,6,7,8,9,10,11,12]
LOOP_SECONDS = 20
MOVE_END = 82
PICKUP_LAPS = 2
RESPAWN_AFTER = [4,5,4,5,4,5,4,5,4,5,4,5]
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
    at = d / (ROUTE_LENGTH * PICKUP_LAPS) * MOVE_END
    event_count = len(STACK) * PICKUP_LAPS
    event_times = [(lap * ROUTE_LENGTH + pickup_distance(j % len(STACK))) / (ROUTE_LENGTH * PICKUP_LAPS) * MOVE_END
                   for lap in range(PICKUP_LAPS) for j in range(len(STACK))]
    previous_respawn = i - len(STACK) + RESPAWN_AFTER[i]
    food_frames = [(0, 0 if previous_respawn >= 0 else 1)]
    if previous_respawn >= 0:
        food_frames.append((event_times[previous_respawn], 1))
    for event in (i, i + len(STACK)):
        food_frames.append((event_times[event], 0))
        respawn_event = event + RESPAWN_AFTER[i]
        if respawn_event < event_count:
            food_frames.append((event_times[respawn_event], 1))
    food_frames.sort()
    css.append(f'@keyframes food{i} {{{"".join(f"{t:.3f}%{{opacity:{v}}}" for t,v in food_frames)}100%{{opacity:0}}}}')
    food.append(f'<g class="food" style="animation:food{i} {LOOP_SECONDS}s linear infinite"><title>{name}</title><rect x="{x-20}" y="{y-20}" width="40" height="40" rx="8" fill="#171914" stroke="#55594c" stroke-width="1.2"/><use href="#logo{i}" x="{x-12}" y="{y-12}" width="24" height="24" fill="#{color}"/></g>')
    reveal = min(MOVE_END, at + 0.55)  # grow only after this snack is eaten
    css.append(f'@keyframes reveal{i} {{0%,{reveal:.3f}%{{opacity:0}} {reveal+0.2:.3f}%,{MOVE_END}%{{opacity:1}} 100%{{opacity:0}}}}')
    body.append(f'<g style="animation:reveal{i} {LOOP_SECONDS}s linear infinite"><g class="segment" style="animation:move{i+1} {LOOP_SECONDS}s linear infinite"><rect x="-16" y="-16" width="32" height="32" rx="7" fill="#596650" stroke="#a9ad91"/><use href="#logo{i}" x="-11" y="-11" width="22" height="22" fill="#{color}"/></g></g>')

# Sample shared route distance. The common closed perimeter makes the loop seamless.
for i in range(13):
    offset = i * STEP
    frames = []
    for pct in range(MOVE_END + 1):
        x, y = point(pct / MOVE_END * ROUTE_LENGTH * PICKUP_LAPS - offset)
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
.head{{animation:idle 3.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.eyes{{animation:blink 4.8s steps(1,end) infinite;transform-box:fill-box;transform-origin:center}}
@keyframes idle{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-1px)}}}}
@keyframes blink{{0%,46%,49%,100%{{transform:scaleY(1)}}47%,48%{{transform:scaleY(.12)}}}}

@keyframes scene{{0%,100%{{opacity:0}}4%{{opacity:1}}90%{{opacity:1}}96%{{opacity:0}}}}

@media(prefers-reduced-motion:reduce){{.scene,.food{{animation:none!important}}.segment{{animation:none!important}}.snake{{display:none}}}}
</style>
<rect width="720" height="320" fill="#11120f"/>
<defs><pattern id="grain" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M2 8h5m20 11h4M11 31h3" stroke="#d8d1bd" stroke-width=".5" opacity=".12"/><circle cx="17" cy="5" r=".5" fill="#d8d1bd" opacity=".18"/><circle cx="31" cy="29" r=".5" fill="#d8d1bd" opacity=".14"/></pattern></defs>
<rect width="720" height="320" fill="url(#grain)" opacity=".42"/>
<path d="M48 64H672V160H48V256H672" fill="none" stroke="#33352d" stroke-width="1" stroke-dasharray="1 12"/>
<path d="M40 32h20M40 32v20M680 32h-20M680 32v20M40 288h20M40 288v-20M680 288h-20M680 288v-20" fill="none" stroke="#777762" stroke-width="1" opacity=".65"/>
<g class="scene">
{''.join(food)}
<g class="snake">{''.join(reversed(body))}
<g style="animation:move0 {LOOP_SECONDS}s linear infinite"><g class="head"><rect x="-17" y="-17" width="34" height="34" rx="7" fill="#d9d4bf" stroke="#f0ead7" stroke-width="1.5"/><g class="eyes" fill="#25271f"><rect x="-8" y="-5" width="4" height="5" rx="1"/><rect x="4" y="-5" width="4" height="5" rx="1"/></g><path d="M-4 7h8" stroke="#9b5847" stroke-width="1.5" stroke-linecap="round"/></g></g>
</g></g>
<g class="marquee"><path d="M286 142h148M286 180h148" stroke="#777762" stroke-width=".8" opacity=".8"/><text x="360" y="155" text-anchor="middle" fill="#a65d49" font-family="monospace" font-size="7" letter-spacing="2">TOOLS / PRACTICE / PLAY</text><text x="360" y="173" text-anchor="middle" fill="#e5dfcc" font-family="Georgia,serif" font-size="16" letter-spacing="2">I NEVER STOP</text><rect x="438" y="151" width="5" height="5" fill="#a65d49"/></g>
</svg>'''
ET.fromstring(svg)
(ROOT / 'assets' / 'stack-snake.svg').write_text(svg, encoding='utf-8')
print(f'Generated stack-snake.svg with 12 logos and a {LOOP_SECONDS}-second loop.')



