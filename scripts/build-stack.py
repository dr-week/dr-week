"""Build the self-contained night-sea technology animation."""
from math import hypot
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'assets' / 'stack-snake.svg'
old = TARGET.read_text(encoding='utf-8')
logos = old[old.index('<defs><symbol'):old.index('</defs>', old.index('<defs><symbol')) + 7]
cat_path = ET.parse(ROOT / 'assets' / 'cat-source.svg').getroot().find('{http://www.w3.org/2000/svg}path').attrib['d']
names = ['TypeScript', 'JavaScript', 'Vue', 'Python', 'Rust', 'Git', 'React', 'Three.js', 'Vite', 'Node.js', 'HTML', 'CSS']
colors = ['#3178c6','#f7df1e','#4fc08d','#77b5e8','#e7ad91','#f05032','#61dafb','#f1ede2','#ac83ff','#5fa04e','#e34f26','#b888f8']
# A loose circuit around the hull. Each pickup lies on the cat's route.
waypoints = [(32,64),(72,62),(169,48),(277,75),(387,54),(496,70),(620,51),(664,157),(620,265),(500,251),(378,274),(246,254),(111,270),(54,166),(32,64)]
pickups = list(range(1,13))
lengths = [hypot(x2-x1,y2-y1) for (x1,y1),(x2,y2) in zip(waypoints,waypoints[1:])]
bounds = [0.0]
for length in lengths: bounds.append(bounds[-1]+length)
total = bounds[-1]

def point(distance):
    distance = max(0, min(total, distance))
    for i in range(len(lengths)):
        if distance <= bounds[i+1]:
            t = (distance-bounds[i])/lengths[i]
            x1,y1 = waypoints[i]
            x2,y2 = waypoints[i+1]
            return x1+(x2-x1)*t, y1+(y2-y1)*t
    return waypoints[-1]

def motion(index):
    offset = index * 24
    samples = {0.0,total,*bounds}
    samples.update(min(total,b+offset) for b in bounds)
    samples.update(total*i/180 for i in range(181))
    parts = []
    for distance in sorted(samples):
        x,y = point(distance-offset)
        parts.append(f'{distance/total*94:.4f}%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    x,y = point(total-offset)
    parts.append(f'100%{{transform:translate({x:.2f}px,{y:.2f}px)}}')
    return f'@keyframes follow{index}{{{"".join(parts)}}}'

css = [motion(i) for i in range(13)]
foods, segments = [], []
for i,(name,color) in enumerate(zip(names,colors)):
    x,y = waypoints[pickups[i]]
    consumed = bounds[pickups[i]]/total*94
    css.append(f'@keyframes food{i}{{0%,{consumed-.15:.2f}%{{opacity:1}}{consumed:.2f}%,97%{{opacity:0}}100%{{opacity:1}}}}')
    css.append(f'@keyframes reveal{i}{{0%,{consumed-.15:.2f}%{{opacity:0}}{consumed:.2f}%,94%{{opacity:1}}98%,100%{{opacity:0}}}}')
    foods.append(f'<g class="food" style="animation:food{i} 28s linear infinite"><title>{name}</title><g class="bob" style="animation-delay:-{i*.63:.2f}s"><circle cx="{x}" cy="{y}" r="16" fill="#17242b" stroke="#54707a" stroke-opacity=".65"/><use href="#logo{i}" x="{x-9}" y="{y-9}" width="18" height="18" fill="{color}"/></g></g>')
    segments.append(f'<g class="collected" style="animation:reveal{i} 28s linear infinite"><g style="animation:follow{i+1} 28s linear infinite"><circle r="14" fill="#121b21" stroke="#a34d55" stroke-width="1"/><use href="#logo{i}" x="-8" y="-8" width="16" height="16" fill="{color}"/></g></g>')

messages = ['DESIGN / BUILD','RESEARCH / TEST','USEFUL BY DESIGN']
message_svg = ''.join(f'<text class="message m{i}" x="360" y="169" text-anchor="middle">{message}</text>' for i,message in enumerate(messages))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">An overhead night-sea illustration. A solid cargo vessel sits in the centre with a wake behind it. Technology logos float at irregular positions. A small black police cat follows a route outside the vessel, collecting logos that form a growing tail.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
<!-- Cat silhouette: Pictogrammers Material Design Icons, Apache 2.0. -->
{logos}
<defs>
  <symbol id="cat-shape" viewBox="0 0 24 24"><path d="{cat_path}"/></symbol>
  <linearGradient id="sea-color" x2="0" y2="1"><stop stop-color="#0d1117"/><stop offset=".5" stop-color="#0d1921"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
  <pattern id="water-lines" width="115" height="38" patternUnits="userSpaceOnUse"><path d="M4 11h22m48 13h31M44 34h10" fill="none" stroke="#537282" stroke-width=".8" opacity=".24"/></pattern>
  <pattern id="led" width="3" height="3" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.1" fill="#f08a85"/></pattern>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
{''.join(css)}
.water{{animation:water 19s linear infinite}}
.wake{{animation:wake 5s linear infinite}}
.bob{{animation:bob 4s ease-in-out infinite}}
.head{{animation:follow0 28s linear infinite}}
.collected,.food{{opacity:0}}
.scene{{animation:scene 28s linear infinite}}
.message{{opacity:0;fill:url(#led);font:700 14px 'Courier New',monospace;letter-spacing:1.7px;filter:url(#glow);animation:message 12s ease-in-out infinite}}
.m1{{animation-delay:4s}}.m2{{animation-delay:8s}}
.lamp{{animation:lamp 4s ease-in-out infinite}}
@keyframes water{{to{{transform:translateX(-115px)}}}}
@keyframes wake{{to{{stroke-dashoffset:-32}}}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
@keyframes lamp{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
@keyframes message{{0%,4%,29%,34%,100%{{opacity:0}}8%,26%{{opacity:1}}}}
@keyframes scene{{0%,94%{{opacity:1}}98%{{opacity:0}}100%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{.water,.wake,.bob,.head,.collected,.food,.scene,.message,.lamp{{animation:none!important}}.food,.scene,.m0{{opacity:1}}.head{{transform:translate(32px,64px)}}.collected{{display:none}}}}
</style>
<rect width="720" height="320" fill="url(#sea-color)"/>
<g class="water"><rect x="0" width="835" height="320" fill="url(#water-lines)"/></g>
<!-- Stern wake opens across the right-hand water. -->
<g fill="none" stroke="#80a9af" stroke-width="1" stroke-linecap="round" opacity=".4">
  <path class="wake" d="M552 134C607 120 652 111 718 95M552 160C620 160 662 159 719 159M552 186C607 202 653 211 718 228" stroke-dasharray="3 8"/>
  <path class="wake" d="M571 145C623 137 658 132 719 124M571 175C623 183 658 188 719 196" stroke-dasharray="1 10" opacity=".65"/>
</g>
<g class="scene">
{''.join(foods)}
<!-- Solid top-view hull, bow at left and squared stern at right. -->
<g>
  <path d="M163 160Q185 111 215 111H543Q557 112 558 127V193Q557 208 543 209H215Q185 209 163 160Z" fill="#202c31" stroke="#789097" stroke-width="1.5"/>
  <path d="M178 160Q194 125 217 124H542V196H217Q194 195 178 160Z" fill="#172127" stroke="#425b62"/>
  <path d="M184 160L217 137V183Z" fill="#26343a" stroke="#6e8991"/>
  <path d="M222 124V196M529 124V196" stroke="#67818a" stroke-width="1"/>
  <rect x="229" y="130" width="96" height="27" rx="2" fill="#2f4145" stroke="#648086"/>
  <rect x="331" y="130" width="96" height="27" rx="2" fill="#3b383a" stroke="#9a666a"/>
  <rect x="433" y="130" width="88" height="27" rx="2" fill="#2f4145" stroke="#648086"/>
  <rect x="229" y="163" width="96" height="27" rx="2" fill="#2f4145" stroke="#648086"/>
  <rect x="331" y="163" width="96" height="27" rx="2" fill="#3b383a" stroke="#9a666a"/>
  <rect x="433" y="163" width="88" height="27" rx="2" fill="#2f4145" stroke="#648086"/>
  <path d="M235 136h84m-84 6h84m-84 6h84m18-12h84m-84 6h84m-84 6h84m18-12h76m-76 6h76m-76 6h76M235 169h84m-84 6h84m-84 6h84m18-12h84m-84 6h84m-84 6h84m18-12h76m-76 6h76m-76 6h76" stroke="#b8cac6" stroke-opacity=".18"/>
  <rect x="267" y="149" width="186" height="22" rx="2" fill="#10191e" stroke="#9b565c"/>
  {message_svg}
  <path d="M532 133h19v54h-19Z" fill="#2e3c40" stroke="#6f888a"/>
  <path d="M536 139h11v18h-11Z" fill="#131e23" stroke="#829b9a"/>
  <circle class="lamp" cx="548" cy="123" r="2" fill="#e67d79" filter="url(#glow)"/>
  <circle class="lamp" cx="548" cy="197" r="2" fill="#e67d79" filter="url(#glow)"/>
  <circle class="lamp" cx="188" cy="160" r="2" fill="#edbc8a" filter="url(#glow)"/>
</g>
<!-- Each eaten logo becomes a segment of the cat's tail. -->
{''.join(reversed(segments))}
<g class="head">
  <circle r="23" fill="#a6404d" opacity=".17" filter="url(#glow)"/>
  <use href="#cat-shape" x="-24" y="-24" width="48" height="48" fill="#080b0e" stroke="#b45862" stroke-width=".35"/>
  <circle cx="-6" cy="0" r="3.6" fill="#e7b84d"/><circle cx="6" cy="0" r="3.6" fill="#e7b84d"/>
  <circle cx="-5" cy="-.2" r="1.9" fill="#0a0c0d"/><circle cx="7" cy="-.2" r="1.9" fill="#0a0c0d"/>
  <path d="M-2 5h4L0 8Z" fill="#e98991"/>
  <path d="M-11-12Q0-18 11-12L10-9H-10Z" fill="#9d3745" stroke="#e5848b" stroke-width=".8"/>
  <circle cx="0" cy="-12" r="1.4" fill="#f2c59c"/>
</g>
</g>
</svg>'''
ET.fromstring(svg)
TARGET.write_text(svg, encoding='utf-8')
print(f'Generated sea scene: {len(foods)} floating logos, {len(segments)} growing tail segments.')
