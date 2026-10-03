# Karma Specialty Coffee, Langen – Demo-Website

One-Pager für **Karma Specialty Coffee**, Bahnstraße 4, 63225 Langen (Hessen).
Scroll-Erlebnis durch die Signature Cups: Jede Sorte ist eine gepinnte Szene mit eigener, scroll-gekoppelter Choreografie.
Die vier Açaí Cups sind **echte Fotos des Cafés** (freigestellt und in Ebenen zerlegt), die schwebenden Früchte echte Fotos
aus Open Images (CC BY 2.0, Nachweis im Footer). Nur die Iced Strawberry Matcha ist eine 3D-Visualisierung.

## Szenen

| # | Szene | Bewegungsidee |
|---|---|---|
| 0 | Auftakt | Ladebildschirm mit Wortmarke; der echte Becher steigt ins Bild, sein Topping fällt von oben darauf und setzt federnd auf |
| 1 | Hero → **Classic** | „Gutes / Karma.“ wandern gegenläufig hinaus, derselbe Becher gleitet von rechts nach links; das Topping hebt ab wie in einer Explosionszeichnung, echte Erdbeeren, Himbeeren und Heidelbeeren steigen aus dem Becher und schweben in Tiefenebenen (vorn unscharf), dann fliegen sie hinaus und das Topping landet wieder |
| 2 | **Caramel Crunch** | Der Becher steht zuerst als blasse Vorschau da und füllt sich von unten mit Farbe (wandernde weiche Kante), dann fällt die Haube mit Mandeln obendrauf; Riesenschrift läuft gegenläufig |
| 3 | **Peanut Power** | Der Becher setzt sich Schicht für Schicht zusammen: Açaí, Chiapudding und Erdnussbutter gleiten abwechselnd von links und rechts herein, das Topping landet, dann kippt der Becher sanft; „Peanut“ und „Power“ laufen gegeneinander |
| 4 | **Berry Blast** | Echte Beeren explodieren als Kranz um den Becher, das Topping springt hoch, die Buchstaben des Titels fliegen mit und setzen sich zusammen, dann zieht sich alles zurück in den Becher |
| 5 | **Iced Strawberry Matcha** | Erdbeerpüree, Milch und Matcha setzen sich nacheinander ab (gerenderte Schicht-Sequenz); der Hintergrund läuft von Rot zu Grün; die Schichten werden auf ihrer Höhe beschriftet |
| 6 | Impressionen | Echte Café-Fotos im versetzten Editorial-Raster mit Parallax |
| 7 | Speisekarte | Beispielkarte mit sechs Kategorien, Vorschaubildern und mitlaufenden Kategorie-Tabs |
| 8 | Besuch | Adresse, Öffnungszeiten mit „Heute geöffnet bis …“, Google-Bewertung, Instagram, Route |

Zwischen den Szenen blendet eine durchgehende Farbfläche von Sorte zu Sorte über (nur `opacity`).
Animiert werden ausschließlich `transform` und `opacity`. Die Fotos sind pixelgenau in Ebenen zerlegt: Zu Beginn einer Szene
wird das Endbild gegen seine deckungsgleichen Einzelteile getauscht, am Ende zurück. Die Matcha-Bildfolge läuft auf `<canvas>`
mit weicher Überblendung zwischen zwei Bildern. Bei „Bewegung reduzieren“ zeigt die Seite alle Becher statisch untereinander.
Auf dem Handy gibt es eine eigene Variante (kürzere Szenen, kleinere Flugbahnen, 600 px breite Ebenen, weniger Früchte).

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
| `assets/photo/` | Becherfotos als WebP (je Sorte Endbild, Ebenen, Handy-Fassungen `-m`, Schatten) und `fruit/` (Fruchtfotos) |
| `assets/render/` | `manifest.json` (Lage aller Ebenen auf der Bühne) und die 3D-Matcha (Endbild, Bildfolge, Schatten) |
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

## Becherfotos neu erzeugen (z. B. mit den Originalfotos des Cafés)

Die Quellfotos liegen nicht im Repository (`_work/real/ig1.jpg` bis `ig3.jpg`, Fruchtfotos in `_work/oi/fruit/`).

```
pip install rembg onnxruntime pillow numpy scipy
# Freistellen (lokal, Modell birefnet-general; je Bild ein eigener Aufruf, das Modell braucht viel Arbeitsspeicher)
python3 -c "from rembg import remove, new_session; from PIL import Image; s=new_session('birefnet-general'); remove(Image.open('_work/real/ig1.jpg').convert('RGB'), session=s, post_process_mask=True).save('_work/real/ig1_birefn.png')"
python3 tools/photo/cups.py      # Becher trennen, in Ebenen zerlegen, auf die Bühne setzen (Umrisse oben in der Datei)
python3 tools/photo/sprites.py   # einzelne Früchte ausschneiden
python3 tools/photo/build.py     # WebP nach assets/photo/, Einträge in assets/render/manifest.json, Karten-Vorschaubilder
python3 tools/photo/og_image.py  # Vorschaubild für Link-Vorschauen
```

Bei anderen Fotos müssen in `tools/photo/cups.py` die Umrisse (`poly`), die Randlinie (`rim`) und der Boden (`bottom`)
an das neue Foto angepasst werden.

## 3D-Matcha neu erzeugen (optional)

Die Iced Strawberry Matcha und die übrigen Karten-Motive sind 3D-Visualisierungen, gerendert mit Blender 5.0 (Cycles, CPU) über das Python-Modul `bpy`.

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

## Ergebnisse der Prüfung (Oktober 2026, Fassung mit echten Fotos)

Lighthouse 12 gegen `tools/serve.mjs` (verhält sich wie der Webhoster mit `.htaccess`: Kompression, Cache-Header, CSP), je zwei Läufe:

| | Performance | Barrierefreiheit | Best Practices | SEO | LCP | CLS |
|---|---|---|---|---|---|---|
| Desktop | 97–98 | 100 | 100 | 100 | 0,4 s | 0,011 |
| Handy (gedrosselt) | 74–75 | 100 | 100 | 100 | 2,1 s | 0,009 |

Auf dem Handy-Profil (4-fach gedrosselte CPU) kostet der Aufbau der fünf gepinnten Szenen Rechenzeit
(„Total Blocking Time“ ca. 1,2–1,3 s); die Szenen werden deshalb nacheinander in kleinen Schritten aufgebaut,
während der Auftakt läuft. Zum Vergleich: Die vorherige 3D-Fassung erreichte im selben Prüfumfeld 74 Punkte (LCP 2,3 s).
Ohne Server-Kompression (z. B. `python3 -m http.server`) liegen die Werte etwas niedriger.

- Konsole: keine Fehler und keine Warnungen; **keine einzige Anfrage an fremde Server** (geprüft mit `tools/shoot.mjs`,
  Desktop, Handy und „Bewegung reduzieren“).
- Übertragung für die ganze Seite inklusive aller Szenen: ca. 3,1 MB Desktop, ca. 1,7 MB Handy
  (die Becherfotos samt Ebenen sind zusammen nur etwa 1 MB groß).

## Qualitätsprüfung

- `node tools/shoot.mjs desktop|mobile <ordner>`: Screenshots an festen Punkten jeder Szene
- `node tools/record.mjs desktop|mobile <datei.webm>`: Scroll-Video
- `node tools/serve.mjs 8791`: lokaler Testserver mit Kompression und Cache-Headern wie in `.htaccess`
- Nach Änderungen an CSS oder JavaScript die Versionsnummer `?v=` in `index.html` hochzählen (aktuell `?v=4`).
- `.htaccess` (Apache): Kompression, Browser-Cache, Content-Security-Policy (nur eigene Dateien erlaubt). Beim Hochladen
  mitkopieren, sie ist eine versteckte Datei. Bei nginx-Hostern die Regeln entsprechend übertragen.
