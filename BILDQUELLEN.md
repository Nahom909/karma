# Bildquellen, Schriften und Lizenzen

Stand: Oktober 2026. Auf der Website werden **keine** Bilder, Schriften oder Skripte von fremden Servern geladen.
Alles liegt im eigenen Website-Ordner.

## 1. Signature Cups: echte Fotos aus dem Café

Die vier Açaí Cups in den Scroll-Szenen (Classic, Caramel Crunch, Peanut Power, Berry Blast) sind **echte Fotos des Cafés**,
keine KI-Bilder und keine 3D-Modelle. Grundlage sind die drei Instagram-Fotos, die der Auftraggeber bereitgestellt hat
(dieselben Fotos wie unter „Impressionen“, siehe Abschnitt 3).

| Datei / Ordner | Inhalt | Quelle | Urheber | Rechte |
|---|---|---|---|---|
| `assets/photo/classic/` | Classic: Becher links auf Foto 2 (Endbild, Becher- und Topping-Ebene, Schatten) | Instagram @yourkarmacoffee, vom Auftraggeber bereitgestellt | Karma Specialty Coffee | Rechte beim Café. **Vor Veröffentlichung schriftliche Freigabe einholen.** |
| `assets/photo/caramel/` | Caramel Crunch: Becher rechts auf Foto 2 (zusätzlich entsättigte „Vorschau“ für die Füll-Animation) | wie oben | wie oben | wie oben |
| `assets/photo/peanut/` | Peanut Power: Becher auf Foto 1 (drei waagerechte Schichten + Topping) | wie oben | wie oben | wie oben |
| `assets/photo/berry/` | Berry Blast: vorderer Becher auf Foto 3 | wie oben | wie oben | wie oben |
| `assets/img/karte/cup-*.webp` (außer `cup-matcha.webp`) | Vorschaubilder der Speisekarte, Ausschnitte der Endbilder oben | wie oben | wie oben | wie oben |
| `assets/img/og-image.jpg` | Vorschaubild für Link-Vorschauen (WhatsApp, Facebook) mit dem Classic-Becher | wie oben | wie oben | wie oben |

**Bearbeitung** (Skripte in `tools/photo/`, alles lokal, kein Upload zu einem Online-Dienst):
freigestellt mit dem Modell BiRefNet (über `rembg`, läuft auf dem eigenen Rechner), Nachbarbecher über Umrisse abgetrennt,
in Ebenen zerlegt (Topping und Becher, bei Peanut Power drei Schichten), vergrößert und leicht nachgeschärft, Schatten ergänzt.
Beim Berry-Blast-Becher war im Originalfoto der linke Rand angeschnitten; er ist spiegelbildlich aus der rechten Becherseite ergänzt.
**Alle Metadaten (EXIF, ggf. GPS) entfernt.** Auf Foto 1 war im Hintergrund ein Arm zu sehen; er ist durch das Freistellen nicht mehr im Bild.
Der Aufdruck „THISISYOUR karma“ ist der echte Becheraufdruck des Cafés.

Die Fotos sind Instagram-Screenshots (etwa 550 bis 770 Pixel breit). Mit den Originaldateien des Cafés werden die Becher
schärfer; die Skripte in `tools/photo/` lassen sich dafür einfach erneut ausführen (siehe README).

## 2. Schwebende Früchte: Fotos aus Open Images (CC BY 2.0)

In den Animationen fliegen echte Fruchtfotos um die Becher. Sie stammen aus **Open Images** (Google, Version 6), einer Sammlung
von Flickr-Fotos, die ihre Urheber unter **Creative Commons Attribution 2.0 (CC BY 2.0)** freigegeben haben.
Die Lizenz erlaubt die kommerzielle Nutzung und Bearbeitung, verlangt aber die Nennung von Urheber, Titel, Quelle und Lizenz
sowie einen Hinweis auf Änderungen. Diese Nennung steht **sichtbar auf der Website** (Footer und Impressum, Text in
`content.json` unter `bildnachweis`). Die Bilder wurden einmalig heruntergeladen und liegen im Website-Ordner; die Website lädt
nichts von Flickr oder Google. Auf keinem der Fotos sind Personen zu sehen (bei der großen Erdbeere hielten Finger den Stiel, sie
sind durch das Freistellen entfernt).

| Datei | Motiv | Titel | Urheber | Quelle | Lizenz |
|---|---|---|---|---|---|
| `assets/photo/fruit/strawberry_1.webp` | Erdbeere | Fresh-Strawberry-Against-Blue-Sky__DSCF0707-768x1024 | Emilian Robert Vicol | https://www.flickr.com/photos/free-stock/8425214419 | CC BY 2.0 |
| `assets/photo/fruit/strawberry_2.webp` | Erdbeere | One Big Strawberry | dailylifeofmojo | https://www.flickr.com/photos/dailylifeofmojo/5586975143 | CC BY 2.0 |
| `assets/photo/fruit/raspberry_1.webp`, `raspberry_2.webp` | Himbeeren | Red raspberries on white plate | Bernt Rostad | https://www.flickr.com/photos/brostad/9051431448 | CC BY 2.0 |
| `assets/photo/fruit/blueberry_1.webp` bis `blueberry_3.webp` | Heidelbeeren | Fresh Blueberries | John Morgan | https://www.flickr.com/photos/aidanmorgan/4646285067 | CC BY 2.0 |

Lizenztext: https://creativecommons.org/licenses/by/2.0/deed.de.
Bearbeitung: freigestellt (BiRefNet, lokal), einzelne Früchte ausgeschnitten, verkleinert, die Heidelbeeren farblich angepasst.
Die Lizenzangabe stammt aus den Metadaten von Open Images (`oidv6-train-images-with-labels-with-rotation.csv`, Spalte `License`).
Empfehlung vor dem Livegang: die vier Flickr-Seiten einmal aufrufen und die Angaben als Screenshot ablegen.

## 3. Iced Strawberry Matcha und Speisekarte (3D-Visualisierungen)

Für die Iced Strawberry Matcha gibt es kein Foto des Cafés und kein frei lizenziertes Foto mit passendem Becher.
Sie bleibt deshalb eine **3D-Visualisierung** und ist auf der Website als „3D-Visualisierung“ gekennzeichnet
(steuerbar in `content.json` unter `bildkennzeichnung`).

| Datei / Ordner | Inhalt | Quelle | Urheber | Lizenz |
|---|---|---|---|---|
| `assets/render/matcha/` | Iced Strawberry Matcha: Endbild, Schicht-Sequenz, Schatten | eigene 3D-Visualisierung (Blender 5.0, Cycles), `tools/blender/matcha.py` | erstellt für Karma Specialty Coffee | frei nutzbar für die Website des Cafés, keine Rechte Dritter |
| `assets/img/karte/` (Bowls, Smoothies, Drinks, Kaffee, Extras, `cup-matcha.webp`) | Vorschaubilder der Speisekarte | eigene 3D-Visualisierung, `tools/blender/menu.py` | wie oben | wie oben |
| Texturen (nicht auf der Website, entstehen in `_work/tex/`) | Erdbeer-Schnitt, Latte Art, Logo-Aufdruck für die 3D-Szenen | per Skript erzeugt (`tools/textures/`) | wie oben | wie oben |

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
| frühere 3D-Becher (Classic, Tropical, Peanut, Berry) | Durch die echten Fotos ersetzt und aus `assets/` entfernt. Die Blender-Szenen liegen weiter in `tools/blender/`. |

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
