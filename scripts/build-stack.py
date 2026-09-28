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
LOOP_SECONDS = 18
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


def smoothstep(t):
    return t * t * (3 - 2 * t)


def time_percent(distance_fraction):
    """Invert smoothstep so pickups stay synchronized with eased motion."""
    low, high = 0.0, 1.0
    for _ in range(32):
        mid = (low + high) / 2
        if smoothstep(mid) < distance_fraction:
            low = mid
        else:
            high = mid
    return (low + high) / 2 * MOVE_END

defs, css, food, body = [], [], [], []
for i, (name, slug, color) in enumerate(STACK):
    source = check_output(['gh', 'api', f'repos/simple-icons/simple-icons/contents/icons/{slug}.svg?ref=develop', '-H', 'Accept: application/vnd.github.raw+json'], timeout=30)
    root = ET.fromstring(source)
    paths = ''.join(f'<path d="{p.attrib["d"]}"/>' for p in root if p.tag.endswith('path'))
    defs.append(f'<symbol id="logo{i}" viewBox="0 0 24 24">{paths}</symbol>')
    d = pickup_distance(i)
    x, y = point(d)
    at = time_percent(d / (ROUTE_LENGTH * PICKUP_LAPS))
    event_count = len(STACK) * PICKUP_LAPS
    event_times = [time_percent((lap * ROUTE_LENGTH + pickup_distance(j % len(STACK))) / (ROUTE_LENGTH * PICKUP_LAPS))
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
        x, y = point(smoothstep(pct / MOVE_END) * ROUTE_LENGTH * PICKUP_LAPS - offset)
        frames.append(f'{pct}%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    x, y = point(-offset)
    frames.append(f'100%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    css.append(f'@keyframes move{i}{{{"".join(frames)}}}')

COPY = ["I NEVER STOP", "BUILD WITH INTENT", "CURIOUS BY DESIGN", "MAKE / TEST / REFINE", "CODE MEETS CRAFT", "ALWAYS IN MOTION"]
COPY_CYCLE = len(COPY) * 3
copy_css, copy_markup = [], []
slot_pct, fade_pct = 100 / len(COPY), 4.5
for i, phrase in enumerate(COPY):
    start, end = i * slot_pct, (i + 1) * slot_pct
    copy_css.append(f"@keyframes copy{i}{{0%,{start:.3f}%{{opacity:0;animation-timing-function:cubic-bezier(.22,1,.36,1)}}{start+fade_pct:.3f}%{{opacity:1}}{end-fade_pct:.3f}%{{opacity:1;animation-timing-function:cubic-bezier(.4,0,1,1)}}{end:.3f}%,100%{{opacity:0}}}}")
    copy_markup.append(f"<text class=\"copy copy{i}\" x=\"360\" y=\"166\" text-anchor=\"middle\">{phrase}</text>")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">A retro arcade snake gathers the technologies I use: TypeScript, JavaScript, Vue, Python, Rust, Git, React, Three.js, Vite, Node.js, HTML and CSS.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
<defs>{''.join(defs)}</defs>
<style>
{''.join(css)}
{''.join(copy_css)}
.scene{{animation:scene {LOOP_SECONDS}s ease-in-out infinite}}
.head{{animation:idle 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.copy{{opacity:0;fill:#e5dfcc;font:600 13px monospace;letter-spacing:1.5px;animation-duration:{COPY_CYCLE}s;animation-timing-function:linear;animation-iteration-count:infinite}}
.copy0{{animation-name:copy0}}
.copy1{{animation-name:copy1}}
.copy2{{animation-name:copy2}}
.copy3{{animation-name:copy3}}
.copy4{{animation-name:copy4}}
.copy5{{animation-name:copy5}}
.glow{{filter:url(#soft-glow);transform-box:fill-box;transform-origin:center;animation:glow 6s ease-in-out infinite}}
.glow.g2{{animation-duration:9s;animation-delay:-3s}}
.glow.g3{{animation-duration:3s;animation-delay:-2s}}
.rain{{fill:#94b79a;opacity:.18;font:9px monospace;animation:rain 6s linear infinite}}
.rain.r2{{animation-duration:9s;animation-delay:-2s}}
.rain.r3{{animation-duration:3s;animation-delay:-1s}}
@keyframes glow{{0%,100%{{opacity:.12;transform:scale(.92)}}50%{{opacity:.36;transform:scale(1.08)}}}}
@keyframes rain{{0%{{transform:translateY(-10px);opacity:0}}20%{{opacity:.2}}80%{{opacity:.16}}100%{{transform:translateY(12px);opacity:0}}}}
@keyframes idle{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-1px)}}}}

@keyframes scene{{0%,100%{{opacity:0}}4%{{opacity:1}}90%{{opacity:1}}96%{{opacity:0}}}}

@media(prefers-reduced-motion:reduce){{.scene,.food{{animation:none!important}}.segment{{animation:none!important}}.snake{{display:none}}}}
</style>
<rect width="720" height="320" fill="#11120f"/>
<defs><filter id="soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="12"/></filter><linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3f0e5" stop-opacity=".82"/><stop offset=".48" stop-color="#d7ded0" stop-opacity=".58"/><stop offset="1" stop-color="#aab8ac" stop-opacity=".72"/></linearGradient><filter id="head-shadow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur"/><feOffset dy="1"/><feComponentTransfer><feFuncA type="linear" slope=".22"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter><pattern id="grain" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M2 8h5m20 11h4M11 31h3" stroke="#d8d1bd" stroke-width=".5" opacity=".12"/><circle cx="17" cy="5" r=".5" fill="#d8d1bd" opacity=".18"/><circle cx="31" cy="29" r=".5" fill="#d8d1bd" opacity=".14"/></pattern></defs>
<rect width="720" height="320" fill="url(#grain)" opacity=".42"/>
<path d="M48 64H672V160H48V256H672" fill="none" stroke="#33352d" stroke-width="1" stroke-dasharray="1 12"/>
<path d="M40 32h20M40 32v20M680 32h-20M680 32v20M40 288h20M40 288v-20M680 288h-20M680 288v-20" fill="none" stroke="#777762" stroke-width="1" opacity=".65"/>
<ellipse class="glow g1" cx="360" cy="160" rx="105" ry="35" fill="#6c9b75"/><ellipse class="glow g2" cx="324" cy="150" rx="68" ry="22" fill="#bd765f"/><ellipse class="glow g3" cx="402" cy="173" rx="72" ry="24" fill="#89aa92"/>
<text class="rain" x="285" y="125">ｱ 0 ｶ 1 ｻ 0 ﾀ</text><text class="rain r2" x="410" y="195">ﾅ 1 ﾊ 0 ﾏ 1</text><text class="rain r3" x="300" y="205">0 ﾔ 1 ﾗ 0 ｱ</text>
<g class="scene">
{''.join(food)}
<g class="snake">{''.join(reversed(body))}
<g style="animation:move0 {LOOP_SECONDS}s linear infinite"><g class="head"><rect x="-17" y="-17" width="34" height="34" rx="7" fill="url(#glass)" stroke="#f0ead7" stroke-opacity=".9" stroke-width="1.2" filter="url(#head-shadow)"/><path d="M-12-11h24" stroke="#fff" stroke-opacity=".62" stroke-width="1"/><path d="M-12-7l8 2-1 2-8-1zm24 0-8 2 1 2 8-1z" fill="#302a28"/><path d="M-12-4l9 2-2 6-7-2zm24 0L3-2l2 6 7-2z" fill="#faf1dc"/><path d="M-7-2l4 1-1 4-3-1zm14 0L3-1l1 4 3-1z" fill="#a64f42"/><path d="M-7 8q7 3 14 0" fill="none" stroke="#75463e" stroke-width="1.3" stroke-linecap="round"/></g></g>
</g></g>
<g class="marquee"><rect x="264" y="136" width="192" height="48" rx="10" fill="#17201b" fill-opacity=".76" stroke="#a6b7a1" stroke-opacity=".58" stroke-width="1"/><path d="M274 144h172" stroke="#fff" stroke-opacity=".24"/><text x="360" y="151" text-anchor="middle" fill="#a65d49" font-family="monospace" font-size="6" letter-spacing="2">DR.WEEK / TECH &amp; MAKING</text>{''.join(copy_markup)}</g>
</svg>'''
ET.fromstring(svg)
(ROOT / 'assets' / 'stack-snake.svg').write_text(svg, encoding='utf-8')
print(f'Generated stack-snake.svg with 12 logos and a {LOOP_SECONDS}-second loop.')



