# mendeltem.github.io

Meine Browser-Startseite. Eine einzelne HTML-Datei mit Uhr, Wetter, Suchfeld
und Linkliste, dazu ein Ordner mit Hintergrundbildern.

Live: <https://mendeltem.github.io/>

## Was die Seite kann

- **Uhr und Begrüßung**, die sich nach der Tageszeit richtet, daneben eine
  zweite Zeitzone (Ulan-Bator) mit Hinweis, wenn dort schon der nächste Tag ist.
- **Wetter** für Berlin und Ulan-Bator, aktuell und Vorhersage für morgen.
  Quelle ist [Open-Meteo](https://open-meteo.com/) — kein Schlüssel nötig, die
  Antwort gilt 15 Minuten und liegt so lange im `localStorage`.
- **Suchfeld** mit Präfixen: Das erste Wort entscheidet das Ziel, alles ohne
  bekanntes Präfix geht zu Google.

  | Präfix | Ziel | Präfix | Ziel |
  |---|---|---|---|
  | `y` | YouTube | `gs` | Google Scholar |
  | `w` | Wikipedia | `pm` | PubMed |
  | `gh` | GitHub | `ar` | arXiv |
  | `r` | Reddit | `yf` | Yahoo Finance |
  | `mp` | Google Maps | | |

- **Links** in vier Gruppen: Täglich, Märkte, KI & Code, Meine Projekte.
- **Elf Farbschemata** mit passendem Hintergrundbild. Ekko und Space rotieren
  durch mehrere Bilder, 12 Sekunden Standzeit und 1,6 Sekunden Blende.

### Tastenkürzel

| Taste | Wirkung |
|---|---|
| `1`–`9` | die ersten neun Links öffnen |
| `t` | nächstes Theme |
| `b` | nächstes Hintergrundbild |
| `/` | ins Suchfeld springen |
| `Esc` | Suchfeld verlassen |

### Theme nach Uhrzeit

Ohne eigene Wahl richtet sich das Schema nach der Stunde: ab 5 Uhr Sakura,
ab 11 Uhr Ocean, ab 17 Uhr Ekko, ab 22 Uhr Space. Ein Klick auf ein Theme gilt
bis zum Ende des laufenden Abschnitts, danach übernimmt wieder die Uhr.

## Aufbau

```
index.html      alles in einer Datei: CSS, Markup, JavaScript
bg/<theme>/     die Hintergrundbilder, WebP, durchnummeriert ab 01
```

Kein Build, keine Abhängigkeiten. Die Datei lokal im Browser öffnen genügt;
auch das Wetter lädt aus einer `file://`-Seite, weil Open-Meteo
`Access-Control-Allow-Origin: *` schickt. Von außen kommen nur die Schrift
Space Grotesk von Google Fonts und die Wetterabfrage.

## Anpassen

**Link hinzufügen** — eine Zeile in die passende `.chips`-Gruppe:

```html
<a href="https://…" class="chip" target="_blank" rel="noopener"><span class="chip-icon">🌍</span>Name</a>
```

**Suchpräfix hinzufügen** — eine Zeile in `routes`. Die Kurzhilfe unten auf der
Seite baut sich aus derselben Tabelle und veraltet dadurch nicht:

```js
const routes = {
    y: ['YouTube', 'https://www.youtube.com/results?search_query='],
    …
};
```

**Hintergrundbild hinzufügen** — Datei nach `bg/<theme>/` legen und eine Zeile
in `rotations` ergänzen. Ist die Helligkeit unpassend, statt des Pfads ein
Objekt eintragen:

```js
{ img: 'bg/space/08.webp', filter: 'brightness(0.8)' }
```

Ab zwei Bildern läuft die Rotation von selbst; bei einem bleibt das Bild
stehen, das im CSS unter `--bg-img` steht.

**Theme hinzufügen** — einen `body[data-theme="name"]`-Block im CSS anlegen
(dieselben Variablen wie bei den anderen), einen Knopf in `.theme-bar`
eintragen und einen Eintrag in `rotations`.

**Stadt wechseln** — Koordinaten in `wxUrl` anpassen (erst Berlin, dann der
zweite Ort) und die IANA-Zeitzone in `farTz` sowie die beiden Städtenamen im
Markup nachziehen.

## Rücksichten

- `prefers-reduced-motion: reduce` schaltet Übergänge und die
  Hintergrundrotation ab.
- Im Hintergrundtab pausiert die Rotation; beim Zurückkehren laufen Uhr und
  Wetter sofort nach.
- Schlägt `localStorage` fehl, etwa im Privatmodus, gilt die Themewahl nur für
  die geöffnete Seite.

## Veröffentlichen

GitHub Pages liefert `main` aus. Ein Push genügt, nach ein bis zwei Minuten
steht die neue Fassung.
