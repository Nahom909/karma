"""Setzt den SVG-Sprite (Icons von Phosphor, MIT-Lizenz, und die Karma-Wortmarke) in index.html ein."""
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = os.path.join(ROOT, 'node_modules/@phosphor-icons/core/assets')
icons = {'i-arrow-up-right': 'regular/arrow-up-right', 'i-instagram': 'regular/instagram-logo', 'i-map-pin': 'regular/map-pin',
         'i-clock': 'regular/clock', 'i-star': 'fill/star-fill', 'i-arrow-down': 'regular/arrow-down'}
parts = ['<svg class="sprite" aria-hidden="true" focusable="false">', '  <!-- UI-Icons: Phosphor Icons (MIT-Lizenz) -->']
for sid, f in icons.items():
    svg = open(os.path.join(PH, f + '.svg')).read()
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
    inner = re.sub(r'<rect width="256" height="256" fill="none"/>', '', inner).strip()
    parts.append(f'  <symbol id="{sid}" viewBox="0 0 256 256">{inner}</symbol>')
wm = open(os.path.join(ROOT, 'assets/img/wordmark.svg')).read()
vb = re.search(r'viewBox="([^"]+)"', wm).group(1)
paths = ''.join(re.findall(r'<path[^>]*/>', wm))
parts.append('  <!-- Wortmarke „THISISYOUR karma“ (nachgebaut nach dem Becheraufdruck) -->')
parts.append(f'  <symbol id="wordmark" viewBox="{vb}">{paths}</symbol>')
parts.append('</svg>')
sprite = '\n'.join(parts)
p = os.path.join(ROOT, 'index.html')
html = open(p).read()
if '<!--SPRITE-->' in html:
    html = html.replace('<!--SPRITE-->', sprite)
else:
    html = re.sub(r'<svg class="sprite".*?</svg>\n</svg>|<svg class="sprite".*?\n</svg>', sprite, html, count=1, flags=re.S)
open(p, 'w').write(html)
print('sprite ok', len(sprite))
