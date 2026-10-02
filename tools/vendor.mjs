// Kopiert Schriften und Bibliotheken aus node_modules in den Website-Ordner (keine CDN-Verbindung zur Laufzeit).
import { copyFileSync, mkdirSync } from 'node:fs';
const copy = [
  ['node_modules/gsap/dist/gsap.min.js', 'assets/vendor/gsap.min.js'],
  ['node_modules/gsap/dist/ScrollTrigger.min.js', 'assets/vendor/ScrollTrigger.min.js'],
  ['node_modules/lenis/dist/lenis.min.js', 'assets/vendor/lenis.min.js'],
  ['node_modules/gsap/dist/SplitText.min.js', 'assets/vendor/SplitText.min.js'],
  ['node_modules/@fontsource-variable/bodoni-moda/files/bodoni-moda-latin-opsz-normal.woff2', 'assets/fonts/bodoni-moda.woff2'],
  ['node_modules/@fontsource-variable/bodoni-moda/files/bodoni-moda-latin-opsz-italic.woff2', 'assets/fonts/bodoni-moda-italic.woff2'],
  ['node_modules/@fontsource-variable/instrument-sans/files/instrument-sans-latin-standard-normal.woff2', 'assets/fonts/instrument-sans.woff2'],
  ['node_modules/@fontsource/courier-prime/files/courier-prime-latin-700-normal.woff2', 'assets/fonts/courier-prime-bold.woff2'],
];
for (const [from, to] of copy) { mkdirSync(to.replace(/\/[^/]+$/, ''), { recursive: true }); copyFileSync(from, to); console.log('✓', to); }
