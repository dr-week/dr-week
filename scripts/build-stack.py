"""Build the self-contained technology scene from the checked-in SVG logos."""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'assets' / 'stack-snake.svg'
old = TARGET.read_text(encoding='utf-8')
logos = old[old.index('<defs><symbol'):old.index('</defs>', old.index('<defs><symbol')) + len('</defs>')]
names = ['TypeScript', 'JavaScript', 'Vue', 'Python', 'Rust', 'Git', 'React', 'Three.js', 'Vite', 'Node.js', 'HTML', 'CSS']
colors = ['#3178c6','#f7df1e','#4fc08d','#77b5e8','#e7ad91','#f05032','#61dafb','#f1ede2','#ac83ff','#5fa04e','#e34f26','#b888f8']
icons = []
food_css = []
badges = []
for i, (name, color) in enumerate(zip(names, colors)):
    x = 72 + (i % 6) * 112
    y = 54 if i < 6 else 270
    pickup = 5 + i * 8 if i < 6 else 55 + (11 - i) * 8
    food_css.append(f'@keyframes eat{i}{{0%,{pickup - .1:.1f}%{{opacity:1}}{pickup:.1f}%,96%{{opacity:0}}100%{{opacity:1}}}}')
    icons.append(f'<g class="food" style="animation:eat{i} 24s linear infinite"><title>{name}</title><circle cx="{x}" cy="{y}" r="19" fill="#161d24" stroke="#303b42"/><use href="#logo{i}" x="{x-11}" y="{y-11}" width="22" height="22" fill="{color}"/></g>')
    badges.append(f'<use class="badge" style="animation:badge{i} 24s linear infinite" href="#logo{i}" x="{-24 + (i % 6) * 9}" y="{18 + (i // 6) * 10}" width="8" height="8" fill="{color}"/>')
    food_css.append(f'@keyframes badge{i}{{0%,{pickup - .1:.1f}%{{opacity:0}}{pickup:.1f}%,96%{{opacity:1}}100%{{opacity:0}}}}')

messages = ['DESIGN / BUILD', 'RESEARCH / TEST', 'MAKE IT USEFUL']
labels = ''.join(f'<text class="message m{i}" x="360" y="171" text-anchor="middle">{message}</text>' for i, message in enumerate(messages))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="320" viewBox="0 0 720 320" role="img" aria-labelledby="title desc">
<title id="title">Technologies in my projects</title>
<desc id="desc">Night sea from above. A solid cargo ship points left with a wake behind it. A black cat police monster patrols outside the hull, grows as it collects twelve technology logos, and wears them as markings. Container lights cycle short messages.</desc>
<!-- Technology logos: Simple Icons, CC0. https://github.com/simple-icons/simple-icons -->
{logos}
<defs>
  <pattern id="sea" width="130" height="36" patternUnits="userSpaceOnUse"><path d="M3 14h22m38-8h12m23 19h18" stroke="#3b5661" stroke-width=".8" stroke-linecap="round" opacity=".36"/></pattern>
  <pattern id="ribs" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M1 0v8" stroke="#66737a" stroke-opacity=".3" stroke-width=".7"/></pattern>
  <pattern id="led-pixels" width="3" height="3" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.2" fill="#f28b7e"/></pattern>
  <filter id="soft-light" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="2.4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="police-halo" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<style>
{''.join(food_css)}
.sea{{animation:water 18s linear infinite}}
.wake{{animation:wake 5s linear infinite}}
.boat{{animation:drift 7s ease-in-out infinite;transform-origin:360px 162px}}
.light{{animation:light 4s ease-in-out infinite}}
.message{{fill:url(#led-pixels);font:700 16px 'Courier New',monospace;letter-spacing:2px;filter:url(#soft-light);opacity:0;animation:message 12s ease-in-out infinite}}
.cat-hunt{{animation:patrol 24s linear infinite}}
.cat-growth{{animation:growth 24s ease-in-out infinite;transform-origin:0 0}}
.orbit-red{{animation:orbit-red 3.7s ease-in-out infinite;transform-origin:0 0}}
.orbit-blue{{animation:orbit-blue 4.9s ease-in-out infinite;transform-origin:0 0}}
.m1{{animation-delay:4s}}.m2{{animation-delay:8s}}
@keyframes patrol{{0%{{transform:translate(16px,54px);opacity:0}}5%{{transform:translate(72px,54px);opacity:1}}45%{{transform:translate(632px,54px)}}55%{{transform:translate(632px,270px)}}95%{{transform:translate(72px,270px);opacity:1}}97%{{opacity:0}}100%{{transform:translate(16px,54px);opacity:0}}}}
@keyframes growth{{0%,5%{{transform:scale(.84)}}45%{{transform:scale(1.05)}}55%{{transform:scale(1.1)}}95%{{transform:scale(1.28)}}100%{{transform:scale(.84)}}}}
@keyframes orbit-red{{0%,100%{{transform:translate(-27px,-8px);opacity:.45}}40%{{transform:translate(0,-31px);opacity:.9}}70%{{transform:translate(29px,-3px);opacity:.3}}}}
@keyframes orbit-blue{{0%,100%{{transform:translate(25px,7px);opacity:.35}}35%{{transform:translate(-5px,29px);opacity:.75}}75%{{transform:translate(-29px,3px);opacity:.25}}}}
@keyframes water{{to{{transform:translateX(-130px)}}}}
@keyframes wake{{to{{stroke-dashoffset:-36}}}}
@keyframes drift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}
@keyframes light{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
@keyframes message{{0%,4%,29%,34%,100%{{opacity:0}}8%,26%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{.sea,.wake,.boat,.light,.message,.cat-hunt,.cat-growth,.orbit-red,.orbit-blue,.food,.badge{{animation:none!important}}.m0{{opacity:1}}.cat-hunt{{transform:translate(72px,54px)}}.badge{{opacity:1}}}}
</style>
<rect width="720" height="320" fill="#0d1117"/>
<g class="sea"><rect x="0" width="850" height="320" fill="url(#sea)"/></g>
<g fill="none" stroke="#7c9aa0" stroke-width="1" stroke-linecap="round" opacity=".4">
  <path class="wake" d="M594 133C632 126 658 125 698 118M596 162C645 159 667 159 716 160M594 190C632 197 660 202 700 211" stroke-dasharray="4 8"/>
  <path class="wake" d="M607 144C642 140 666 138 693 134M607 180C640 184 663 187 691 193" stroke-dasharray="2 10"/>
</g>
{''.join(icons)}
<g class="boat">
  <!-- Solid top-view hull; pointed bow left, wake at the stern on the right. -->
  <path d="M118 160Q153 115 184 115H572Q590 117 594 132V188Q590 203 572 205H184Q153 205 118 160Z" fill="#252d31" stroke="#8b9b99" stroke-width="1.5"/>
  <path d="M136 160Q165 128 186 128H578V192H186Q165 192 136 160Z" fill="#1b2227" stroke="#4b5e60"/>
  <path d="M149 160Q164 146 177 137V183Q164 174 149 160Z" fill="#303b40" stroke="#7e9291"/>
  <path d="M509 136H565V184H509Z" fill="#30393b" stroke="#667978"/>
  <path d="M516 143H558V177H516Z" fill="#161e22" stroke="#82918a"/>
  <path d="M216 127V193M521 127V193" stroke="#69807e" stroke-width="1"/>
  <!-- Containers, seen from above. -->
  <rect x="226" y="130" width="94" height="27" rx="2" fill="#343d40" stroke="#677d7c"/>
  <rect x="325" y="130" width="94" height="27" rx="2" fill="#3b3938" stroke="#946b66"/>
  <rect x="424" y="130" width="88" height="27" rx="2" fill="#343d40" stroke="#677d7c"/>
  <rect x="226" y="163" width="94" height="27" rx="2" fill="#343d40" stroke="#677d7c"/>
  <rect x="325" y="163" width="94" height="27" rx="2" fill="#3b3938" stroke="#946b66"/>
  <rect x="424" y="163" width="88" height="27" rx="2" fill="#343d40" stroke="#677d7c"/>
  <path d="M232 135H313M232 141H313M232 147H313M331 135H412M331 141H412M331 147H412M430 135H505M430 141H505M430 147H505M232 169H313M232 175H313M232 181H313M331 169H412M331 175H412M331 181H412M430 169H505M430 175H505M430 181H505" stroke="#aab6ad" stroke-opacity=".17"/>
  <!-- Inset LED display, flush with the deck. -->
  <rect x="250" y="149" width="220" height="24" rx="2" fill="#101719" stroke="#734c4a"/>
  {labels}
  <circle class="light" cx="575" cy="127" r="2" fill="#e9877d" filter="url(#soft-light)"/>
  <circle class="light" cx="575" cy="193" r="2" fill="#e9877d" filter="url(#soft-light)"/>
  <circle class="light" cx="148" cy="160" r="2.5" fill="#e6ba86" filter="url(#soft-light)"/>
</g>
<!-- The patrol path stays outside the hull and reaches each logo in order. -->
<g class="cat-hunt">
  <circle r="28" fill="#b43e46" opacity=".22" filter="url(#police-halo)"/>
  <g class="orbit-red"><circle r="7" fill="#d64950" opacity=".3" filter="url(#police-halo)"/><circle r="2" fill="#ed777e"/></g>
  <g class="orbit-blue"><circle r="6" fill="#5a8eaa" opacity=".22" filter="url(#police-halo)"/><circle r="1.7" fill="#82b0be"/></g>
  <g class="cat-growth">
    <rect x="-29" y="15" width="58" height="24" rx="10" fill="#11171a" stroke="#a95052" stroke-width=".8"/>
    {''.join(badges)}
    <path d="M-16-7l-2-17 11 6Q0-21 7-18l11-6-2 17q5 12-2 19-5 5-14 5t-14-5q-7-7-2-19Z" fill="#0b0d10" stroke="#bd6966" stroke-width="1.2"/>
    <path d="M-14-17l-1-5 5 3zm28 0 1-5-5 3z" fill="#cc7174"/>
    <path d="M-10-2l6 1m8-1 6-1" stroke="#f0d4cc" stroke-width="1.4" stroke-linecap="round"/>
    <path d="M-3 5h6l-3 3z" fill="#ed777e"/>
    <path d="M-6 9Q0 15 6 9" fill="none" stroke="#cf6364" stroke-width="1.2"/>
    <path d="M-10-13Q0-20 10-13M-13-11H13" fill="none" stroke="#bb5e5b" stroke-width="1.2"/>
    <circle cx="0" cy="-16" r="1.8" fill="#e9877d"/>
  </g>
</g>
</svg>'''
ET.fromstring(svg)
TARGET.write_text(svg, encoding='utf-8')
print('Generated top-view cargo ship scene with 12 embedded technology logos.')
