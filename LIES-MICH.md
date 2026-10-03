# Website Karma Specialty Coffee: Texte selbst ändern

Hier steht, wie Sie Texte, Preise, Öffnungszeiten und Bilder Ihrer Website selbst ändern können.
Sie brauchen dafür keine Programmierkenntnisse, nur einen einfachen Texteditor.

---

## 1. Welche Datei öffne ich?

**Alles Sichtbare steht in einer einzigen Datei: `content.json`.**
Sie liegt im Hauptordner der Website, direkt neben `index.html`.

Zum Öffnen einen **einfachen Texteditor** verwenden:

- **Windows:** Rechtsklick auf `content.json` → „Öffnen mit“ → **Editor**. Noch angenehmer ist das kostenlose **Notepad++**.
- **Mac:** Rechtsklick → „Öffnen mit“ → **TextEdit**. Vorher im Menü *Format* → **„In reinen Text umwandeln“** wählen.

**Nicht verwenden:** Word, Pages oder LibreOffice. Diese Programme verändern die Anführungszeichen und machen die Datei unbrauchbar.

---

## 2. Wie ist die Datei aufgebaut?

Jede Zeile hat links einen **Namen** und rechts den **Inhalt**:

```
"preis": "7,90 €",
```

- Links vom Doppelpunkt steht der Name (`"preis"`). **Den nie ändern.**
- Rechts steht der Text zwischen Anführungszeichen (`"7,90 €"`). **Nur den ändern Sie.**

| Bereich | Was drinsteht |
|---|---|
| `cafe` | Name, Adresse, Instagram, Google-Sterne und Anzahl der Bewertungen, Links |
| `seo` | Titel und Beschreibung für Google |
| `navigation` | Menüpunkte oben, Text „Heute geöffnet bis …“ |
| `hero` | Große Überschrift ganz oben („Gutes Karma.“), Satz darunter, Text im runden Siegel |
| `signature` | Die vier großen Becher-Szenen: Name, Untertitel, Beschreibung, Zutaten, Preis |
| `matcha` | Die Matcha-Szene mit den drei Schichten |
| `impressionen` | Die Fotos aus dem Café |
| `speisekarte` | Kategorien und Einträge der Karte (Name, Beschreibung, Preis, Bild) |
| `oeffnungszeiten` | Tage und Uhrzeiten |
| `besuch`, `footer` | Texte unten, Links zu Impressum und Datenschutz |
| `bildkennzeichnung` | Hinweis „3D-Visualisierung“ an der Matcha und Bildhinweis im Footer |
| `bildnachweis` | Pflichtangaben zu den Fruchtfotos (Urheber, Titel, Link, Lizenz). **Bitte nicht löschen**, solange die Früchte auf der Seite fliegen |

---

## 3. Was darf ich ändern, was nicht?

**Das dürfen Sie:** jeden Text **zwischen den Anführungszeichen rechts**, Preise, und `true`/`false` umstellen (ohne Anführungszeichen).

**Das bitte nicht:**
1. **Kommas nicht löschen.** Am Ende fast jeder Zeile steht ein Komma. Die **letzte** Zeile in einem Bereich (direkt vor `}` oder `]`) hat **keins**.
2. **Anführungszeichen nicht löschen.** Jeder Text beginnt und endet mit `"`.
3. **Keine geraden Anführungszeichen im Text.** Nehmen Sie typografische wie „so“.
4. **Die Namen links** und die Klammern `{ } [ ]` nicht verändern.

---

## 4. Häufige Änderungen

### Einen Preis ändern
Mit Strg+F (Mac: Cmd+F) nach dem Namen suchen, z. B. `Berry Blast`. Ein paar Zeilen darunter steht `"preis": "8,40 €",`. Nur die Zahl ändern.
Achtung: Die Becher stehen zweimal in der Datei, einmal bei `signature` (große Szene) und einmal bei `speisekarte` (Karte).

### Öffnungszeiten ändern
Im Bereich `oeffnungszeiten` steht für jeden Tag z. B.:
```
{ "tag": "Montag", "zeiten": ["09:00-19:00"] },
```
- Zeiten immer im Format `"09:00-19:00"`.
- **Ruhetag:** leere Klammern → `"zeiten": []`
- **Mittagspause:** zwei Zeitfenster → `"zeiten": ["09:00-13:00", "14:00-19:00"]`
- Den Satz `"zusammenfassung": "Täglich 9–19 Uhr"` bitte passend mitändern.

Die Website zeigt oben rechts automatisch „Heute geöffnet bis 19 Uhr“ bzw. „Gerade geschlossen“ an (nach deutscher Zeit).

### Google-Bewertung aktualisieren
Im Bereich `cafe`: `"google_sterne": "4,4"` und `"google_anzahl_bewertungen": "103"`. Die Sterne passen sich automatisch an.

### Speisekarte ändern
Im Bereich `speisekarte` → `kategorien`. Jeder Eintrag sieht so aus:
```
{ "name": "Espresso", "beschreibung": "Specialty Roast, doppelt", "preis": "2,60 €", "bild": "assets/img/karte/coffee-espresso.webp" },
```
Einen Eintrag hinzufügen: eine solche Zeile kopieren und darunter einfügen (Komma dazwischen nicht vergessen).
Ohne Bild: `"bild": ""`.

### Fotos unter „Impressionen“ tauschen oder ergänzen
1. Foto im **Hochformat 4:5** zuschneiden (ideal **1200 × 1500 Pixel**), als `.jpg` oder `.webp` speichern.
2. In den Ordner `assets/impressionen/` hochladen.
3. In `content.json` bei `impressionen` → `bilder` einen Eintrag anlegen oder ändern:
```
{ "bild": "assets/impressionen/mein-foto.jpg", "format": "hoch", "bildunterschrift": "Morgens an der Theke", "beschreibung": "Barista schäumt Milch auf" },
```
Die `beschreibung` lesen Blinde und Google, bitte kurz beschreiben, was zu sehen ist.
Die Galerie ordnet beliebig viele Fotos automatisch im versetzten Raster an.

### Die großen Becherbilder
Die vier Açaí Cups sind **Ihre eigenen Instagram-Fotos**, freigestellt und für die Animationen in Teile zerlegt
(Topping, Becher, bei Peanut Power drei Schichten). Wenn Sie die **Originalfotos** in voller Größe haben, werden die Becher
noch schärfer. Schicken Sie die Dateien einfach an die Person, die die Website betreut; die Aufbereitung ist in der
README beschrieben (Ordner `tools/photo/`). Ein neues Foto von Hand einzusetzen ist nicht sinnvoll, weil die Teile
pixelgenau zusammenpassen müssen.

Die Iced Strawberry Matcha ist weiterhin eine 3D-Visualisierung und deshalb als solche gekennzeichnet.
Sobald es ein gutes Foto davon gibt, kann sie genauso ersetzt werden.

---

## 5. Wie lade ich die Datei hoch?

1. Datei speichern (Strg+S bzw. Cmd+S). Der Dateiname bleibt **genau** `content.json`.
2. Beim Webhoster anmelden und den **Dateimanager** öffnen (oder FileZilla verwenden).
3. `content.json` in den Ordner der Website hochladen und die alte Datei **ersetzen**.
4. Website neu laden. Falls noch der alte Text zu sehen ist: **Strg+F5** (Windows) bzw. **Cmd+Shift+R** (Mac).

**Tipp:** Vor jeder Änderung eine Kopie anlegen, z. B. `content-sicherung.json`.

**Beim ersten Hochladen der ganzen Website:** Die Datei `.htaccess` mit hochladen. Sie beginnt mit einem Punkt und wird
deshalb oft ausgeblendet (in FileZilla: Menü *Server* → „Anzeigen versteckter Dateien erzwingen“). Sie sorgt für schnelle
Ladezeiten und dafür, dass die Seite nur Dateien vom eigenen Server lädt.

---

## 6. Und wenn ich mich vertippt habe?

Die Seite bleibt **nicht leer**. Bei einem Fehler in `content.json` zeigt sie automatisch die zuletzt ausgelieferten Texte.
Ihre Änderungen erscheinen dann aber nicht. So finden Sie den Fehler:

1. Den Inhalt von `content.json` auf **https://jsonlint.com** einfügen und „Validate JSON“ klicken.
2. Dort steht die Zeile mit dem Fehler, meist ein fehlendes Komma oder Anführungszeichen.

---

## 7. Was steht NICHT in content.json?

- **Impressum und Datenschutz** (`impressum.html`, `datenschutz.html`): Das sind **Platzhalter**. Vor der Veröffentlichung mit den
  echten Angaben füllen und prüfen lassen.
- **Vorschau für Google und Messenger**: Titel und Beschreibung stehen zusätzlich oben in `index.html`.
- `assets/js/content-fallback.js` ist die Sicherheitskopie. **Bitte nicht bearbeiten.**

## Wichtig beim Testen

Die Website muss über einen Webserver laufen (online oder mit einem lokalen Testserver).
Per Doppelklick auf `index.html` zeigt der Browser nur die Sicherheitskopie der Texte.
