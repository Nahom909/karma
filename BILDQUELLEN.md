# Bildquellen, Schriften und Lizenzen

Stand: Oktober 2026. Auf der Website werden **keine** Bilder, Schriften oder Skripte von fremden Servern geladen.
Alles liegt im eigenen Website-Ordner.

## 1. Hero und Highlights: Bild des Auftraggebers

Die vier Becher im Hero (Iced Strawberry Matcha, Açaí-Becher mit Mango-Maracuja, Açaí-Becher mit Granola, Erdbeer-Smoothie)
stammen aus **einem Bild, das der Auftraggeber bereitgestellt hat** (1536 × 1024 Pixel, vier Becher auf weißem Grund).
Der erste Becher (Matcha) und der dritte Becher (Açaí) sind zugleich die Bilder der beiden Highlights.
Auf der Website sind sie als **„Symbolbild“** gekennzeichnet (Text in `content.json` unter `bildkennzeichnung`).

| Datei | Inhalt | Quelle | Rechte |
|---|---|---|---|
| `assets/hero/cup-matcha.webp` | Becher 1: Iced Strawberry Matcha (Hero, Highlight Matcha) | Bild des Auftraggebers | **Herkunft und Nutzungsrechte vor Veröffentlichung schriftlich bestätigen lassen** |
| `assets/hero/cup-mango.webp` | Becher 2: Açaí mit Mango-Maracuja (Hero) | wie oben | wie oben |
| `assets/hero/cup-karma.webp` | Becher 3: Açaí mit Granola und Kokoscreme (Hero, Highlight Açaí) | wie oben | wie oben |
| `assets/hero/cup-pink.webp` | Becher 4: Erdbeer-Smoothie (Hero) | wie oben | wie oben |
| `assets/img/karte/cup-karma.webp`, `cup-mango.webp`, `drink-strawberry-matcha.webp`, `smoothie-pink.webp` | Vorschaubilder der Karte (Ausschnitte der Becher oben) | wie oben | wie oben |
| `assets/img/og-image.jpg` | Vorschaubild für Link-Vorschauen (WhatsApp, Facebook) mit den vier Bechern | wie oben | wie oben |

**Bearbeitung** (`tools/hero/build.py`, alles lokal, kein Upload zu einem Online-Dienst): freigestellt mit dem Modell
BiRefNet (über `rembg`, läuft auf dem eigenen Rechner), in vier Einzelbilder geteilt, als WebP gespeichert. Metadaten
werden dabei nicht übernommen. Auf den Bechern ist kein Aufdruck und keine fremde Marke zu sehen.

**Hinweis zur Kennzeichnung:** Falls das Bild mit einem KI-Programm erzeugt wurde, empfiehlt sich statt „Symbolbild“
die Angabe „KI-generiert“ (in `content.json` unter `bildkennzeichnung` → `bild_text` und `footer_text` änderbar).
Falls es von einer Bilddatenbank oder einer Agentur stammt, bitte die Lizenz und gegebenenfalls die Pflicht zur
Urheberangabe prüfen und den Nachweis hier ergänzen.

## 2. Speisekarte: echte Fotos aus dem Café

| Datei | Inhalt | Quelle | Urheber | Rechte |
|---|---|---|---|---|
| `assets/img/karte/cup-classic.webp`, `cup-caramel.webp`, `cup-peanut.webp`, `cup-berry.webp`, `cup-base-*.webp` | Vorschaubilder der Signature Cups und „Eigener Cup“ | Ausschnitte aus den Instagram-Fotos unter „Impressionen“ (Abschnitt 4), vom Auftraggeber bereitgestellt | Karma Specialty Coffee | Rechte beim Café. **Vor Veröffentlichung schriftliche Freigabe einholen.** |

Bearbeitung: freigestellt (BiRefNet, lokal), zugeschnitten, **alle Metadaten (EXIF, ggf. GPS) entfernt**.
Der Aufdruck „THISISYOUR karma“ auf diesen Bechern ist der echte Becheraufdruck des Cafés.

## 3. Übrige Vorschaubilder der Speisekarte (3D-Visualisierungen)

| Datei / Ordner | Inhalt | Quelle | Urheber | Lizenz |
|---|---|---|---|---|
| `assets/img/karte/` (Green Glow, Mango Sunrise, Iced Matcha Latte, Matcha Latte, Chai, Kaffee, Extras) | Vorschaubilder der Speisekarte | eigene 3D-Visualisierung (Blender 5.0, Cycles), `tools/blender/menu.py` | erstellt für Karma Specialty Coffee | frei nutzbar für die Website des Cafés, keine Rechte Dritter |
| Texturen (nicht auf der Website, entstehen in `_work/tex/`) | Latte Art, Logo-Aufdruck für die 3D-Szenen | per Skript erzeugt (`tools/textures/`) | wie oben | wie oben |

**Wortmarke:** `assets/img/wordmark.svg` ist dem echten Becheraufdruck „THISISYOUR karma“ nachgebaut, aus den Umrissen der
freien Schriften Jost und Courier Prime (siehe unten). Es ist das Markenzeichen des Cafés und wird nur für dessen eigene Website verwendet.

## 4. Impressionen (echte Fotos aus dem Café)

| Datei | Motiv | Quelle | Urheber | Lizenz / Rechte |
|---|---|---|---|---|
| `assets/impressionen/karma-01-chia-layer.webp` | Becher mit Açaí, Erdnussbutter, Chiapudding, Beeren | Instagram @yourkarmacoffee, https://www.instagram.com/yourkarmacoffee/, vom Auftraggeber als Screenshot bereitgestellt | Karma Specialty Coffee (Fotograf/in bitte beim Café erfragen) | Rechte beim Café. **Vor Veröffentlichung schriftliche Freigabe einholen.** |
| `assets/impressionen/karma-02-swirl-duo.webp` | zwei Açaí-Becher mit Swirl | wie oben (Instagram-Bedienelement oben rechts weggeschnitten) | wie oben | wie oben |
| `assets/impressionen/karma-03-trio.webp` | drei Becher in einer Reihe | wie oben (Instagram-Bedienelement weggeschnitten) | wie oben | wie oben |

Bearbeitung: zugeschnitten, in WebP umgewandelt, **alle Metadaten (EXIF, ggf. GPS) entfernt**.
Auf Foto 1 ist im Hintergrund unscharf ein Arm mit Handschuh zu sehen; eine Person ist nicht erkennbar.
Die Fotos sind Screenshots mit etwa 750 Pixel Breite. Für die Veröffentlichung sind die Originaldateien
(mindestens 1200 Pixel breit) deutlich besser.

## 5. Nicht auf der Website

| Datei | Zweck |
|---|---|
| `reference/IMG_0771.jpeg` | Nur Referenz für die Perspektive der Becher. **Wird nicht auf der Website verwendet** und ist nicht Teil der Auslieferung. |
| frühere Scroll-Szenen (Becherfotos in Ebenen, 3D-Matcha, schwebende Fruchtfotos aus Open Images) | Mit dem neuen Aufbau (Hero + Highlights) entfernt. Damit entfällt auch der CC-BY-Bildnachweis der Fruchtfotos. Die Blender-Szenen liegen weiter in `tools/blender/`. |

## 6. Schriften (alle selbst gehostet, kein Google-Fonts-CDN)

| Datei | Schrift | Urheber | Lizenz | Bezug |
|---|---|---|---|---|
| `assets/fonts/bodoni-moda.woff2`, `bodoni-moda-italic.woff2` | Bodoni Moda (variabel, Latein-Zeichensatz) | Owen Earl (indestructible type*) | SIL Open Font License 1.1 | npm-Paket `@fontsource-variable/bodoni-moda` |
| `assets/fonts/instrument-sans.woff2` | Instrument Sans (variabel, Latein) | Instrument | SIL Open Font License 1.1 | npm-Paket `@fontsource-variable/instrument-sans` |
| in `assets/img/wordmark.svg` (als Umrisse) | Jost, Courier Prime | Owen Earl (Jost); Alan Dague-Greene / Quote-Unquote Apps (Courier Prime) | SIL Open Font License 1.1 | npm-Pakete `@fontsource/jost`, `@fontsource/courier-prime` |

## 7. Icons und Bibliotheken

| Was | Urheber | Lizenz |
|---|---|---|
| UI-Icons (Pfeil, Instagram, Stern) im SVG-Sprite von `index.html`, `assets/img/stars.svg` | Phosphor Icons | MIT |
| `assets/vendor/gsap.min.js`, `ScrollTrigger.min.js`, `SplitText.min.js` (GSAP 3.15) | GreenSock / Webflow | GSAP Standard „No Charge“ License (kostenlos, auch kommerziell) |
| `assets/vendor/lenis.min.js` (Lenis 1.3) | darkroom.engineering | MIT |
| Werkzeuge zum Freistellen (nicht Teil der Website): `rembg` mit dem Modell BiRefNet | Daniel Gatis (rembg); Zheng Peng u. a. (BiRefNet) | MIT |
