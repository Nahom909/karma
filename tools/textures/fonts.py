"""Wandelt die benötigten Schriften (aus node_modules) in TTF-Dateien für die Textur-Skripte um. Ausgabe: _work/fonts/"""
import os
from fontTools.ttLib import TTFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, '_work', 'fonts')
os.makedirs(OUT, exist_ok=True)
SRC = {
    'jost-400': 'node_modules/@fontsource/jost/files/jost-latin-400-normal.woff2',
    'jost-500': 'node_modules/@fontsource/jost/files/jost-latin-500-normal.woff2',
    'courier-regular': 'node_modules/@fontsource/courier-prime/files/courier-prime-latin-400-normal.woff2',
    'courier-bold': 'node_modules/@fontsource/courier-prime/files/courier-prime-latin-700-normal.woff2',
    'bodoni': 'assets/fonts/bodoni-moda.woff2', 'bodoni-italic': 'assets/fonts/bodoni-moda-italic.woff2',
    'instrument': 'assets/fonts/instrument-sans.woff2',
}
for k, v in SRC.items():
    f = TTFont(os.path.join(ROOT, v)); f.flavor = None; f.save(os.path.join(OUT, k + '.ttf')); print('✓', k)
