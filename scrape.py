#!/usr/bin/env python3
"""Liest alle Studium-Generale-Termine von der Uni-Tübingen-Webseite und schreibt events.json.

Quelle: https://uni-tuebingen.de/universitaet/im-dialog/studium-generale/
Jeder Termin ist dort mit einer eigenen Veranstaltungsseite (/news-default/article/...) verlinkt,
die Datum, Uhrzeit, Ort, Referent/in und Reihe strukturiert enthält.

Sicherheitsnetz: Findet das Skript deutlich weniger künftige Termine als bisher, bricht es mit
Fehler ab, statt den Kalender zu leeren (z. B. wenn die Uni ihre Seite umbaut).
"""
import datetime as dt, json, re, sys, time, urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup

BASE = "https://uni-tuebingen.de"
INDEX = BASE + "/universitaet/im-dialog/studium-generale/"
OUT = "events.json"
UA = {"User-Agent": "studium-generale-ics (privater Kalender-Abgleich)"}
CANCEL_RE = re.compile(r"\b(abgesagt|entfällt|entfaellt|fällt aus|faellt aus|verschoben)\b", re.I)


def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(3)


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def index_links():
    soup = BeautifulSoup(get(INDEX), "html.parser")
    main = soup.find("main") or soup
    # Reihen-Titel stehen als Akkordeon-Überschriften (Links auf "#...panel-N..."),
    # darunter die Termin-Links. So bekommt jeder Termin die Reihe aus der Übersicht.
    links, seen, series = [], set(), None
    for a in main.find_all("a", href=True):
        href, text = a["href"], clean(a.get_text(" "))
        if href.startswith("#") and "panel" in href and text:
            series = text
        elif "/news-default/article/" in href:
            u = urljoin(BASE, href.split("#")[0])
            if u not in seen:
                seen.add(u); links.append((u, series))
    return links


def parse_event(url, index_series=None):
    soup = BeautifulSoup(get(url), "html.parser")
    item = soup.find(class_="news-single-item")
    if not item:
        raise ValueError(f"Keine Veranstaltungsdaten auf {url}")
    nid = item.find(attrs={"data-news-id": True})
    title = clean(item.find("h1").get_text(" ")) if item.find("h1") else ""
    h2 = item.find(class_="newsItemTeaserLine")
    series = index_series or (clean(h2.get_text(" ")) if h2 else "Studium Generale")
    info = {}
    for tr in item.select("tr.ut-infotable__item"):
        th, td = tr.find("th"), tr.find("td")
        if th and td:
            info[clean(th.get_text(" ")).rstrip(" :").strip()] = clean(td.get_text(" "))
    when = info.get("Datum", "")
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", when)
    if not m:
        raise ValueError(f"Kein Datum auf {url}: {when!r}")
    date = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    rest = when[m.end():]  # Uhrzeiten stehen hinter dem Datum
    tlist = [f"{int(h):02d}:{mi}" for h, mi in re.findall(r"\b(\d{1,2})[:.](\d{2})\b", rest)]
    start = tlist[0] if tlist else "18:15"
    if len(tlist) > 1:
        end = tlist[1]
    else:
        h, mi = map(int, start.split(":")); e = h * 60 + mi + 90
        end = f"{e // 60:02d}:{e % 60:02d}"
    body = clean(item.get_text(" "))
    cancelled = bool(CANCEL_RE.search(title)) or bool(re.search(r"\b(abgesagt|entfällt|fällt aus)\b", body, re.I))
    note = []
    if re.search(r"auf englisch|in english", title + " " + body, re.I):
        note.append("Vortrag auf Englisch")
    return {
        "uid": f"sg-tue-{nid['data-news-id'] if nid else re.sub(r'[^a-z0-9]+', '-', url.lower())[-60:]}",
        "date": date, "start": start, "end": end,
        "title": title, "series": series,
        "speaker": info.get("Referent/in", info.get("Referent/innen", "")),
        "location": info.get("Veranstaltungsort", ""),
        "note": "; ".join(note), "cancelled": cancelled, "url": url,
    }


def main():
    today = dt.date.today().isoformat()
    try:
        old = json.load(open(OUT, encoding="utf-8")).get("events", [])
    except Exception:
        old = []

    links = index_links()
    if not links:
        sys.exit("FEHLER: Keine Termin-Links auf der Studium-Generale-Seite gefunden – Seitenstruktur geändert?")
    new, errors = [], []
    for u, ser in links:
        try:
            new.append(parse_event(u, ser))
        except Exception as e:
            errors.append(f"{u}: {e}")
        time.sleep(0.5)  # Server schonen

    old_future = [e for e in old if e["date"] >= today and not e.get("cancelled")]
    new_future = [e for e in new if e["date"] >= today]
    if old_future and len(new_future) < 0.5 * len(old_future):
        sys.exit(f"FEHLER: Nur {len(new_future)} künftige Termine gefunden (bisher {len(old_future)}). "
                 "Abbruch, um den Kalender nicht zu leeren.\n" + "\n".join(errors))

    # Vergangene Termine behalten (Kalender-Historie), alles Künftige kommt von der Webseite.
    new_uids = {e["uid"] for e in new}
    keep = [e for e in old if e["uid"] not in new_uids and e["date"] < today]
    events = sorted(keep + new, key=lambda e: (e["date"], e["start"], e["series"]))

    data = {"source": INDEX, "events": events}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(new)} Termine von der Webseite gelesen, {len(keep)} vergangene behalten, "
          f"{sum(e['cancelled'] for e in new)} abgesagt.")
    if errors:
        print("Warnungen:\n" + "\n".join(errors))


if __name__ == "__main__":
    main()
