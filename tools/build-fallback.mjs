// Erzeugt assets/js/content-fallback.js aus content.json (Sicherheitskopie, falls content.json fehlerhaft ist).
import { readFileSync, writeFileSync } from 'node:fs';
const data = JSON.parse(readFileSync('content.json', 'utf8'));
writeFileSync('assets/js/content-fallback.js',
  '/* Automatisch erzeugt aus content.json (node tools/build-fallback.mjs). Bitte nicht von Hand bearbeiten. */\n' +
  'window.KARMA_FALLBACK = ' + JSON.stringify(data) + ';\n');
console.log('content-fallback.js aktualisiert');
