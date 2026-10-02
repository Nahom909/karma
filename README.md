# Karma Specialty Coffee, Langen – Demo-Website

One-Pager für **Karma Specialty Coffee**, Bahnstraße 4, 63225 Langen (Hessen).
Scroll-Erlebnis durch die Signature Cups: Jede Sorte ist eine gepinnte Szene mit eigener, scroll-gekoppelter Choreografie.

## Szenen

| # | Szene | Bewegungsidee |
|---|---|---|
| 0 | Auftakt | Ladebildschirm mit Wortmarke; der Becher steigt auf und dreht sich (echte 3D-Bildfolge) ins Bild, die Toppings fallen einzeln auf den Rand |
| 1 | Hero → **Classic** | „Gutes / Karma.“ wandern gegenläufig hinaus, derselbe Becher gleitet von rechts nach links, die Toppings heben ab und kreisen um den Becher, während er sich einmal um 360° dreht; danach landen sie einzeln auf dem Rand |
| 2 | **Tropical** | Der leere Becher füllt sich von unten (gerenderte Füll-Sequenz), Mango und Ananas schweben in Tiefenebenen (mit Tiefenunschärfe) und landen am Ende oben drauf; Riesenschrift läuft gegenläufig |
| 3 | **Peanut Power** | Erdnussbutter läuft außen am Becher herunter (gerenderte Drip-Sequenz), der Becher kippt dabei sanft; „Peanut“ und „Power“ laufen in entgegengesetzte Richtungen |
| 4 | **Berry Blast** | Die Beeren explodieren aus dem Becher nach außen, die Buchstaben des Titels fliegen mit und setzen sich zusammen, dann zieht sich alles zurück in den Becher |
| 5 | **Iced Strawberry Matcha** | Erdbeerpüree, Milch und Matcha setzen sich nacheinander ab (gerenderte Schicht-Sequenz); der Hintergrund läuft von Rot zu Grün; die Schichten werden auf ihrer Höhe beschriftet |
| 6 | Impressionen | Echte Café-Fotos im versetzten Editorial-Raster mit Parallax |
| 7 | Speisekarte | Beispielkarte mit sechs Kategorien, Vorschaubildern und mitlaufenden Kategorie-Tabs |
| 8 | Besuch | Adresse, Öffnungszeiten mit „Heute geöffnet bis …“, Google-Bewertung, Instagram, Route |

Zwischen den Szenen blendet eine durchgehende Farbfläche von Sorte zu Sorte über (nur `opacity`).
Animiert werden ausschließlich `transform` und `opacity`; die Bildfolgen laufen auf `<canvas>` mit weicher Überblendung
zwischen zwei Bildern. Bei „Bewegung reduzieren“ zeigt die Seite alle Becher statisch untereinander.
Auf dem Handy gibt es eine eigene Variante (kürzere Szenen, kleinere Umlaufbahnen, 520 px breite Bildfolgen).

## Aufbau

| Datei / Ordner | Inhalt |
|---|---|
| `index.html` | Seitengerüst ohne Inhaltstexte |
| `content.json` | **Alle Texte, Preise, Öffnungszeiten, Links und Bildpfade** |
| `LIES-MICH.md` | Anleitung für das Café: Texte ändern, Bilder tauschen, hochladen |
| `BILDQUELLEN.md` | Quelle, Urheber und Lizenz jedes Bildes, jeder Schrift und Bibliothek |
| `assets/js/content.js` | Lädt `content.json`, setzt die Inhalte ein, Öffnungsstatus nach deutscher Zeit |
| `assets/js/content-fallback.js` | Sicherheitskopie der Texte (erzeugt mit `node tools/build-fallback.mjs`) |
| `assets/js/motion.js` | Scroll-Choreografie (GSAP, ScrollTrigger, SplitText, Lenis) |
| `assets/css/style.css` | Gestaltung; Farben, Schriften und Abstände als Variablen ganz oben |
| `assets/render/` | 3D-Visualisierungen als WebP: Endbilder, Bildfolgen (`seq/`, Handy `seq-m/`), Topping-Ebenen, Schatten, `manifest.json` |
| `assets/img/karte/` | Vorschaubilder der Speisekarte |
| `assets/impressionen/` | Fotos aus dem Café |
| `assets/fonts/` | Bodoni Moda, Instrument Sans (selbst gehostet, Latein-Zeichensatz) |
| `assets/vendor/` | GSAP 3.15 (inkl. ScrollTrigger, SplitText), Lenis 1.3 (lokal, keine CDN-Verbindung) |
| `impressum.html`, `datenschutz.html` | **Platzhalter**, vor Veröffentlichung ausfüllen |
| `.htaccess` | Server-Einstellungen für Apache: Kompression, Cache, Sicherheits-Header |
| `tools/` | Render- und Build-Skripte (siehe unten) |

## DSGVO

- Keine Cookies, kein Tracking, keine Analyse, keine eingebetteten Karten, Instagram- oder Google-Widgets.
- Schriften, Bilder und Skripte liegen alle lokal; beim Aufruf wird kein fremder Server kontaktiert.
- Instagram und Google Maps sind nur normale Links. Deshalb ist kein Cookie-Banner nötig.

## Lokal ansehen

Die Seite liest `content.json` und `assets/render/manifest.json` per `fetch`, deshalb über einen kleinen Webserver öffnen:

```
python3 -m http.server 8790
```

Dann `http://localhost:8790` im Browser öffnen.

## Bilder neu erzeugen (optional)

Die Produktbilder sind 3D-Visualisierungen, gerendert mit Blender 5.0 (Cycles, CPU) über das Python-Modul `bpy`.

```
npm install                          # Schriften, GSAP, Lenis, Icons
node tools/vendor.mjs                # Schriften und Bibliotheken nach assets/ kopieren
pip install bpy==5.0.1 pillow fonttools brotli numpy
python3 tools/textures/fonts.py      # Schriften für die Texturen
python3 tools/textures/make_logo.py  # Becheraufdruck „THISISYOUR karma“
python3 tools/textures/make_food_tex.py && python3 tools/textures/make_latte_tex.py
python3 tools/blender/pipeline.py classic      # ebenso: tropical, peanut, berry, matcha
python3 tools/blender/menu.py                  # Speisekarten-Motive
python3 tools/blender/project_points.py        # Bildkoordinaten der Matcha-Schichten
python3 tools/build-assets.py                  # PNG -> WebP + manifest.json
python3 tools/inject-sprite.py                 # Icon-Sprite und Wortmarke in index.html
```

Die Szenen liegen in `tools/blender/` (`klib.py` enthält Becher, Füllungen, Toppings, Materialien, Licht und Kamera).
Mit `KARMA_TEST=1 python3 tools/blender/pipeline.py <szene> schnell` gibt es einen Schnelltest in Mini-Auflösung.

## Ergebnisse der Prüfung (Oktober 2026)

Lighthouse 12 gegen `tools/serve.mjs` (verhält sich wie der Webhoster mit `.htaccess`: Kompression, Cache-Header, CSP), je zwei Läufe:

| | Performance | Barrierefreiheit | Best Practices | SEO | LCP | CLS |
|---|---|---|---|---|---|---|
| Desktop | 97–99 | 100 | 100 | 100 | 0,5 s | 0,01 |
| Handy (gedrosselt) | 77–79 | 100 | 100 | 100 | 2,3 s | 0,007 |

Auf dem Handy-Profil (4-fach gedrosselte CPU) kostet der Aufbau der fünf gepinnten Szenen Rechenzeit
(„Total Blocking Time“ ca. 0,8–0,9 s); die Szenen werden deshalb nacheinander in kleinen Schritten aufgebaut,
während der Auftakt läuft. Ohne Server-Kompression (z. B. `python3 -m http.server`) liegen die Werte etwas niedriger.

- Konsole: keine Fehler und keine Warnungen; **keine einzige Anfrage an fremde Server** (geprüft mit `tools/shoot.mjs`).
- Übertragung für die ganze Seite inklusive aller Bildfolgen: ca. 5,6 MB Desktop, ca. 2,9 MB Handy.
  Zuerst lädt nur, was der Auftakt braucht; die Bildfolgen der späteren Szenen folgen im Hintergrund.

## Qualitätsprüfung

- `node tools/shoot.mjs desktop|mobile <ordner>`: Screenshots an festen Punkten jeder Szene
- `node tools/record.mjs desktop|mobile <datei.webm>`: Scroll-Video
- `node tools/serve.mjs 8791`: lokaler Testserver mit Kompression und Cache-Headern wie in `.htaccess`
- Nach Änderungen an CSS oder JavaScript die Versionsnummer `?v=` in `index.html` hochzählen (aktuell `?v=3`).
- `.htaccess` (Apache): Kompression, Browser-Cache, Content-Security-Policy (nur eigene Dateien erlaubt). Beim Hochladen
  mitkopieren, sie ist eine versteckte Datei. Bei nginx-Hostern die Regeln entsprechend übertragen.
