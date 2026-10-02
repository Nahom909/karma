# Bildquellen, Schriften und Lizenzen

Stand: Oktober 2026. Auf der Website werden **keine** Bilder, Schriften oder Skripte von fremden Servern geladen.
Alles liegt im eigenen Website-Ordner.

## 1. Produktabbildungen (3D-Visualisierungen)

Alle Becher, Toppings und Speisekarten-Motive sind **3D-Visualisierungen**, die eigens für diese Website erstellt wurden.
Es sind weder Stockfotos noch Fotos Dritter. Auf der Website sind sie als „3D-Visualisierung“ gekennzeichnet,
und im Footer steht ein Hinweis (beides lässt sich in `content.json` unter `bildkennzeichnung` steuern).

| Datei / Ordner | Inhalt | Quelle | Urheber | Lizenz |
|---|---|---|---|---|
| `assets/render/classic/` | Classic Cup: Endbild, 48-teilige 360°-Drehung, 7 Topping-Ebenen, Schatten | eigene 3D-Visualisierung (Blender 5.0, Cycles), Szene: `tools/blender/classic.py` | erstellt für Karma Specialty Coffee | frei nutzbar für die Website des Cafés, keine Rechte Dritter |
| `assets/render/tropical/` | Tropical Cup: Endbild, Füll-Sequenz, Mango-, Ananas- und Kokos-Ebenen, Schatten | eigene 3D-Visualisierung, `tools/blender/tropical.py` | wie oben | wie oben |
| `assets/render/peanut/` | Peanut Power Cup: Endbild, Drip-Sequenz, Schatten | eigene 3D-Visualisierung, `tools/blender/peanut.py` | wie oben | wie oben |
| `assets/render/berry/` | Berry Blast Cup: Endbild, Becher ohne Toppings, Beeren-Ebenen, Schatten | eigene 3D-Visualisierung, `tools/blender/berry.py` | wie oben | wie oben |
| `assets/render/matcha/` | Iced Strawberry Matcha: Endbild, Schicht-Sequenz, Schatten | eigene 3D-Visualisierung, `tools/blender/matcha.py` | wie oben | wie oben |
| `assets/img/karte/` | Vorschaubilder der Speisekarte (Bowls, Cups, Smoothies, Drinks, Kaffee, Extras) | eigene 3D-Visualisierung, `tools/blender/menu.py`; Cup-Bilder aus den Endbildern oben | wie oben | wie oben |
| `assets/img/og-image.jpg` | Vorschaubild für Link-Vorschauen (WhatsApp, Facebook) | aus dem Classic-Endbild zusammengesetzt | wie oben | wie oben |
| Texturen (nicht auf der Website, entstehen in `_work/tex/`) | Texturen: Erdbeer-Schnitt, Bananenscheibe, Latte Art, Logo-Aufdruck | per Skript erzeugt (`tools/textures/make_food_tex.py`, `make_latte_tex.py`, `make_logo.py`) | wie oben | wie oben |

**Logo auf den Bechern:** Der Aufdruck „THISISYOUR karma“ ist dem echten Becheraufdruck des Cafés nachgebaut
(Fotos unter „Impressionen“). Es ist das Markenzeichen des Cafés und wird nur für dessen eigene Website verwendet.
Die Nachbildung (Datei `assets/img/wordmark.svg` und die Textur `logo.png` aus `tools/textures/make_logo.py`) besteht aus den Umrissen der
freien Schriften Jost und Courier Prime (siehe unten).

**Hinweis:** Die 3D-Visualisierungen sind Symbolbilder. Wenn echte Produktfotos vorliegen, können sie die
Endbilder ersetzen (Anleitung in `LIES-MICH.md`).

## 2. Impressionen (echte Fotos aus dem Café)

| Datei | Motiv | Quelle | Urheber | Lizenz / Rechte |
|---|---|---|---|---|
| `assets/impressionen/karma-01-chia-layer.webp` | Becher mit Açaí, Erdnussbutter, Chiapudding, Beeren | Instagram @yourkarmacoffee, https://www.instagram.com/yourkarmacoffee/, vom Auftraggeber als Screenshot bereitgestellt | Karma Specialty Coffee (Fotograf/in bitte beim Café erfragen) | Rechte beim Café. **Vor Veröffentlichung schriftliche Freigabe einholen.** |
| `assets/impressionen/karma-02-swirl-duo.webp` | zwei Açaí-Becher mit Swirl | wie oben (Instagram-Bedienelement oben rechts weggeschnitten) | wie oben | wie oben |
| `assets/impressionen/karma-03-trio.webp` | drei Becher in einer Reihe | wie oben (Instagram-Bedienelement weggeschnitten) | wie oben | wie oben |

Bearbeitung: zugeschnitten, in WebP umgewandelt, **alle Metadaten (EXIF, ggf. GPS) entfernt**.
Auf Foto 1 ist im Hintergrund unscharf ein Arm mit Handschuh zu sehen; eine Person ist nicht erkennbar.
Die Fotos sind Screenshots mit etwa 750 Pixel Breite. Für die Veröffentlichung sind die Originaldateien
(mindestens 1200 Pixel breit) deutlich besser.

## 3. Nicht auf der Website

| Datei | Zweck |
|---|---|
| `reference/IMG_0771.jpeg` | Nur Referenz für die Perspektive der Becher. **Wird nicht auf der Website verwendet** und ist nicht Teil der Auslieferung. |

## 4. Schriften (alle selbst gehostet, kein Google-Fonts-CDN)

| Datei | Schrift | Urheber | Lizenz | Bezug |
|---|---|---|---|---|
| `assets/fonts/bodoni-moda.woff2`, `bodoni-moda-italic.woff2` | Bodoni Moda (variabel, Latein-Zeichensatz) | Owen Earl (indestructible type*) | SIL Open Font License 1.1 | npm-Paket `@fontsource-variable/bodoni-moda` |
| `assets/fonts/instrument-sans.woff2` | Instrument Sans (variabel, Latein) | Instrument | SIL Open Font License 1.1 | npm-Paket `@fontsource-variable/instrument-sans` |
| in `assets/img/wordmark.svg` (als Umrisse) | Jost, Courier Prime | Owen Earl (Jost); Alan Dague-Greene / Quote-Unquote Apps (Courier Prime) | SIL Open Font License 1.1 | npm-Pakete `@fontsource/jost`, `@fontsource/courier-prime` |

## 5. Icons und Bibliotheken

| Was | Urheber | Lizenz |
|---|---|---|
| UI-Icons (Pfeil, Instagram, Stern) im SVG-Sprite von `index.html`, `assets/img/stars.svg` | Phosphor Icons | MIT |
| `assets/vendor/gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js` (GSAP 3.15) | GreenSock / Webflow | GSAP Standard „No Charge“ License (kostenlos, auch kommerziell) |
| `assets/vendor/lenis.min.js` (Lenis 1.3) | darkroom.engineering | MIT |
