#!/usr/bin/env python3
"""Baut die Artikelliste in artikel.html aus den Dateien in artikel/.

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 werkzeuge/feed-bauen.py

Der Generator liest jede Datei in artikel/ und holt sich, was er finden kann.
Alles laesst sich pro Artikel ueberschreiben, ohne den Feed anzufassen, durch
optionale meta-Tags im Artikel selbst:

    <meta name="artikel:titel"    content="...">
    <meta name="artikel:teaser"   content="...">
    <meta name="artikel:thema"    content="Geschichte">
    <meta name="artikel:datum"    content="2026-08-30">
    <meta name="artikel:sprachen" content="de,en,mn">

Ohne meta-Tags gilt: Titel aus <title> oder erstem <h1>, Teaser aus dem ersten
laengeren Absatz, Sprachen aus den vorhandenen lang-/data-lang-Angaben, Datum
aus dem ersten Git-Commit der Datei (sonst Dateidatum), Belegzahl aus der
ersten Quellenliste. Der Feed wird zwischen den beiden Markern ersetzt.
"""

import json
import pathlib
import re
import subprocess
import sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ORDNER = WURZEL / "artikel"
FEED = WURZEL / "artikel.html"
ANFANG = "<!-- ARTIKEL:ANFANG -->"
ENDE = "<!-- ARTIKEL:ENDE -->"

QUELL_TITEL = ("Belege", "References", "Quellen", "Sources", "Эх сурвалж")


def text_aus(html):
    """HTML-Fragment zu lesbarem Text."""
    t = re.sub(r"<[^>]+>", " ", html)
    t = (t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"\s+", " ", t).strip()


def meta(html, name):
    m = re.search(
        r'<meta\s+name=["\']artikel:%s["\']\s+content=["\'](.*?)["\']' % name,
        html, re.I | re.S)
    return m.group(1).strip() if m else None


def titel_von(html):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m and text_aus(m.group(1)):
        return text_aus(m.group(1))
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    return text_aus(m.group(1)) if m else None


def teaser_von(html):
    """Erster Absatz mit Substanz nach der ersten Ueberschrift."""
    start = 0
    m = re.search(r"<h1[^>]*>.*?</h1>", html, re.I | re.S)
    if m:
        start = m.end()
    for p in re.finditer(r"<p[^>]*>(.*?)</p>", html[start:start + 20000], re.I | re.S):
        t = text_aus(p.group(1))
        if len(t) >= 60:
            return t if len(t) <= 260 else t[:257].rstrip() + "..."
    return ""


def sprachen_von(html):
    gefunden = re.findall(r'(?:^|\s)(?:data-)?lang=["\']([a-z]{2})["\']', html, re.I)
    reihenfolge, gesehen = [], set()
    for s in gefunden:
        s = s.lower()
        if s not in gesehen:
            gesehen.add(s)
            reihenfolge.append(s)
    return reihenfolge


def belege_von(html):
    """Eintraege der ersten Quellenliste zaehlen, begrenzt bis zur naechsten h1."""
    for wort in QUELL_TITEL:
        m = re.search(r"<h[2-4][^>]*>\s*%s\s*</h[2-4]>" % re.escape(wort), html, re.I)
        if not m:
            continue
        rest = html[m.end():]
        naechste = re.search(r"<h1[^>]*>", rest, re.I)
        block = rest[:naechste.start()] if naechste else rest
        n = len(re.findall(r"<li\b", block, re.I))
        if n:
            return n
    return 0


def datum_von(pfad, html):
    d = meta(html, "datum")
    if d:
        return d
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%ad",
             "--date=short", "--", str(pfad.relative_to(WURZEL))],
            cwd=WURZEL, capture_output=True, text=True, timeout=20)
        zeilen = [z for z in r.stdout.strip().splitlines() if z.strip()]
        if zeilen:
            return zeilen[-1]
    except Exception:
        pass
    import datetime
    return datetime.date.fromtimestamp(pfad.stat().st_mtime).isoformat()


def einlesen(pfad):
    html = pfad.read_text(encoding="utf-8", errors="replace")
    sprachen = meta(html, "sprachen")
    return {
        "datei": f"artikel/{pfad.name}",
        "titel": meta(html, "titel") or titel_von(html) or pfad.stem,
        "teaser": meta(html, "teaser") or teaser_von(html),
        "thema": meta(html, "thema") or "Unsortiert",
        "datum": datum_von(pfad, html),
        "sprachen": [s.strip().lower() for s in sprachen.split(",")] if sprachen
                    else sprachen_von(html),
        "belege": belege_von(html),
        "bytes": pfad.stat().st_size,
    }


def main():
    if not ORDNER.is_dir():
        sys.exit(f"Ordner fehlt: {ORDNER}")
    if not FEED.is_file():
        sys.exit(f"Feed fehlt: {FEED}")

    artikel = [einlesen(p) for p in sorted(ORDNER.glob("*.html"))]
    artikel.sort(key=lambda a: (a["datum"], a["titel"]), reverse=True)

    seite = FEED.read_text(encoding="utf-8")
    if ANFANG not in seite or ENDE not in seite:
        sys.exit("Marker ARTIKEL:ANFANG / ARTIKEL:ENDE fehlen in artikel.html")

    block = json.dumps(artikel, ensure_ascii=False, indent=1)
    vorher, rest = seite.split(ANFANG, 1)
    _, nachher = rest.split(ENDE, 1)
    FEED.write_text(f"{vorher}{ANFANG}\n{block}\n{ENDE}{nachher}", encoding="utf-8")

    print(f"{len(artikel)} Artikel in {FEED.name} geschrieben:")
    for a in artikel:
        print(f"  {a['datum']}  {a['titel']}")
        print(f"     {a['datei']}  Sprachen: {','.join(a['sprachen']) or '?'}"
              f"  Belege: {a['belege']}  {a['bytes'] // 1024} KB")


main()
