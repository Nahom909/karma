#!/bin/bash
# Packt die auslieferbare Website (ohne node_modules, Arbeitsdateien und Referenzbild) als ZIP.
cd "$(dirname "$0")/.."
OUT="${1:-/tmp/karma-specialty-coffee.zip}"
rm -f "$OUT"
zip -qr "$OUT" index.html impressum.html datenschutz.html content.json package.json \
  package-lock.json README.md LIES-MICH.md BILDQUELLEN.md .gitignore .htaccess assets tools \
  -x "*.DS_Store" -x "*/__pycache__/*" -x "tools/_*" -x "tools/render-after.sh" -x "tools/render-matcha-after-menu.sh"
echo "$OUT $(du -h "$OUT" | cut -f1)"
