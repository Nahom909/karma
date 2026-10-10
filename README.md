# Karma Specialty Coffee, Langen – Demo-Website

One-Pager für **Karma Specialty Coffee**, Bahnstraße 4, 63225 Langen (Hessen).

## Abschnitte

| # | Abschnitt | Inhalt und Bewegung |
|---|---|---|
| 1 | Hero | „Karma / Specialty Coffee“ in goldener 3D-Schrift (reines CSS: Metallverlauf + gestaffelte Schatten), darunter die vier Becher aus dem Bild des Auftraggebers. Schrift und Becher blenden beim Laden einmal ein; auf dem Handy stehen die Becher zwei mal zwei |
| 2 | Highlight **Açaí** | Lila Fläche, Becher 3 (Karma Signature) mit Beschreibung, Zutaten und Beispielpreis in Gold; Becher und Text blenden beim Scrollen ein, das große Hintergrundwort gleitet |
| 3 | Highlight **Matcha** | Grüne Fläche, Becher 1 (Iced Strawberry Matcha), gespiegelt aufgebaut |
| 4 | Speisekarte | Beispielkarte mit sechs Kategorien, Vorschaubildern und mitlaufenden Kategorie-Tabs |
| 5 | Impressionen | Echte Café-Fotos im versetzten Editorial-Raster mit Parallax |
| 6 | Besuch | Adresse, Öffnungszeiten mit „Heute geöffnet bis …“, Google-Bewertung, Instagram, Route |

Es gibt keine gepinnten Becher-Szenen mehr. Animiert werden ausschließlich `transform` und `opacity`.
Bei „Bewegung reduzieren“ ist alles sofort und unbewegt sichtbar.

## Aufbau

| Datei / Ordner | Inhalt |
|---|---|
| `index.html` | Seitengerüst ohne Inhaltstexte |
| `content.json` | **Alle Texte, Preise, Öffnungszeiten, Links und Bildpfade** |
| `LIES-MICH.md` | Anleitung für das Café: Texte ändern, Bilder tauschen, hochladen |
| `BILDQUELLEN.md` | Quelle, Urheber und Lizenz jedes Bildes, jeder Schrift und Bibliothek |
| `assets/js/content.js` | Lädt `content.json`, setzt die Inhalte ein, Öffnungsstatus nach deutscher Zeit |
| `assets/js/content-fallback.js` | Sicherheitskopie der Texte (erzeugt mit `node tools/build-fallback.mjs`) |
| `assets/js/motion.js` | Einblendungen (GSAP, ScrollTrigger, SplitText, Lenis) |
| `assets/css/style.css` | Gestaltung; Farben, Schriften und Abstände als Variablen ganz oben |
| `assets/hero/` | Die vier freigestellten Becher (Hero und Highlights) |
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

Die Seite liest `content.json` per `fetch`, deshalb über einen kleinen Webserver öffnen:

```
python3 -m http.server 8790
```

Dann `http://localhost:8790` im Browser öffnen.

## Becher neu erzeugen (z. B. aus einem neuen Gesamtbild)

Das Quellbild liegt nicht im Repository (`_work/hero/src.png`, vier Becher nebeneinander auf hellem Grund).

```
pip install rembg onnxruntime pillow numpy scipy
python3 tools/hero/build.py cut   # freistellen (lokal, Modell birefnet-general, ca. 3 Minuten)
python3 tools/hero/build.py       # vier Becher nach assets/hero/, Karten-Vorschaubilder, og-image.jpg
```

Für das Vorschaubild braucht das Skript die TTF-Schriften aus `python3 tools/textures/fonts.py` (in `_work/fonts/`).

## 3D-Karten-Motive neu erzeugen (optional)

Die übrigen Karten-Motive (Smoothies, Drinks, Kaffee, Extras) sind 3D-Visualisierungen, gerendert mit Blender 5.0 (Cycles, CPU) über das Python-Modul `bpy`.

```
npm install                          # Schriften, GSAP, Lenis, Icons
node tools/vendor.mjs                # Schriften und Bibliotheken nach assets/ kopieren
pip install bpy==5.0.1 pillow fonttools brotli numpy
python3 tools/textures/fonts.py      # Schriften für die Texturen
python3 tools/textures/make_logo.py  # Becheraufdruck „THISISYOUR karma“
python3 tools/textures/make_food_tex.py && python3 tools/textures/make_latte_tex.py
python3 tools/blender/pipeline.py matcha
python3 tools/blender/menu.py                  # Speisekarten-Motive
python3 tools/blender/project_points.py        # Bildkoordinaten der Matcha-Schichten
python3 tools/build-assets.py matcha karte     # PNG -> WebP + manifest.json
python3 tools/inject-sprite.py                 # Icon-Sprite und Wortmarke in index.html
```

Die Szenen liegen in `tools/blender/` (`klib.py` enthält Becher, Füllungen, Toppings, Materialien, Licht und Kamera).
Mit `KARMA_TEST=1 python3 tools/blender/pipeline.py <szene> schnell` gibt es einen Schnelltest in Mini-Auflösung.

## Ergebnisse der Prüfung (Oktober 2026, Fassung mit Hero und Highlights)

Lighthouse 12 gegen `tools/serve.mjs` (verhält sich wie der Webhoster mit `.htaccess`: Kompression, Cache-Header, CSP), je zwei Läufe:

| | Performance | Barrierefreiheit | Best Practices | SEO | LCP | CLS |
|---|---|---|---|---|---|---|
| Desktop | 99–100 | 100 | 100 | 100 | 0,8 s | 0,004 |
| Handy (gedrosselt) | 88 | 100 | 100 | 100 | 3,3 s | 0,002 |

- Konsole: keine Fehler und keine Warnungen; **keine einzige Anfrage an fremde Server** (geprüft mit `tools/shoot.mjs`,
  Desktop, Handy und „Bewegung reduzieren“).
- Übertragung für die ganze Seite: ca. 0,8 MB.

## Qualitätsprüfung

- `node tools/shoot.mjs desktop|mobile|reduced <ordner>`: Screenshots der ganzen Seite, Konsolenfehler, fremde Anfragen
- `node tools/serve.mjs 8791`: lokaler Testserver mit Kompression und Cache-Headern wie in `.htaccess`
- Nach Änderungen an CSS oder JavaScript die Versionsnummer `?v=` in `index.html` hochzählen (aktuell `?v=6`).
- `.htaccess` (Apache): Kompression, Browser-Cache, Content-Security-Policy (nur eigene Dateien erlaubt). Beim Hochladen
  mitkopieren, sie ist eine versteckte Datei. Bei nginx-Hostern die Regeln entsprechend übertragen.
