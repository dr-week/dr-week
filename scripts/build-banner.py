"""Wrap the profile artwork in a self-contained SVG with a quiet glass sheen."""
from base64 import b64encode
from pathlib import Path
from xml.etree import ElementTree as ET

root = Path(__file__).resolve().parents[1]
art = root / 'assets' / 'profile-banner.png'
output = root / 'assets' / 'profile-banner-glare.svg'
png = b64encode(art.read_bytes()).decode('ascii')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2172" height="724" viewBox="0 0 2172 724" role="img" aria-labelledby="title desc">
<title id="title">Dishant Naik — Computer Engineer and Designer</title>
<desc id="desc">Dark illustrated profile banner with a slow, subtle glass reflection passing over the artwork.</desc>
<defs>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#f7f1e8" stop-opacity="0"/>
    <stop offset=".33" stop-color="#f7f1e8" stop-opacity=".015"/>
    <stop offset=".5" stop-color="#fff9f0" stop-opacity=".14"/>
    <stop offset=".61" stop-color="#ffb78e" stop-opacity=".045"/>
    <stop offset="1" stop-color="#f7f1e8" stop-opacity="0"/>
  </linearGradient>
</defs>
<style>
  .reflection {{ animation: sweep 14s cubic-bezier(.42,0,.58,1) infinite; opacity:0; }}
  @keyframes sweep {{
    0%,14% {{ transform:translateX(0); opacity:0; }}
    19% {{ opacity:.75; }}
    66% {{ transform:translateX(3100px); opacity:.75; }}
    71%,100% {{ transform:translateX(3100px); opacity:0; }}
  }}
  @media (prefers-reduced-motion:reduce) {{ .reflection {{ animation:none; opacity:0; }} }}
</style>
<image x="0" y="0" width="2172" height="724" href="data:image/png;base64,{png}"/>
<g class="reflection" aria-hidden="true">
  <rect x="-720" y="-360" width="430" height="1450" transform="skewX(-18)" fill="url(#glass)"/>
</g>
</svg>'''

ET.fromstring(svg)
output.write_text(svg, encoding='utf-8')
print(f'Generated {output.name} ({output.stat().st_size:,} bytes).')
