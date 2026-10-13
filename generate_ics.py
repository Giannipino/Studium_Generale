#!/usr/bin/env python3
"""Erzeugt studium-generale-tuebingen.ics aus events.json (RFC 5545).

UIDs stammen aus der Veranstaltungs-ID der Uni-Webseite: Wird ein Termin verschoben,
aktualisiert Google den bestehenden Eintrag, statt einen doppelten anzulegen.
"""
import json, sys, datetime as dt

VTZ = """BEGIN:VTIMEZONE
TZID:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 75:
        cut = 75 if not out else 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1  # nicht mitten im UTF-8-Zeichen trennen
        out.append(b[:cut].decode()); b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def main(src="events.json", dst="studium-generale-tuebingen.ics"):
    with open(src, encoding="utf-8") as f:
        d = json.load(f)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//sg-ics//Studium Generale Tuebingen//DE",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Studium Generale Uni Tübingen", "X-WR-TIMEZONE:Europe/Berlin",
         "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"] + VTZ.split("\n")
    for e in d["events"]:
        ymd = e["date"].replace("-", "")
        title = ("ABGESAGT: " if e.get("cancelled") else "") + e["title"]
        desc = [f"Reihe: {e['series']}"]
        if e.get("speaker"): desc.append(f"Referent/in: {e['speaker']}")
        if e.get("note"): desc.append(f"Hinweis: {e['note']}")
        desc += ["Eintritt frei, ohne Anmeldung.", f"Details: {e.get('url') or d['source']}"]
        L += ["BEGIN:VEVENT",
              f"UID:{e['uid']}@studium-generale-ics",
              f"DTSTAMP:{now}",
              f"DTSTART;TZID=Europe/Berlin:{ymd}T{e['start'].replace(':', '')}00",
              f"DTEND;TZID=Europe/Berlin:{ymd}T{e['end'].replace(':', '')}00",
              fold("SUMMARY:" + esc(f"StG: {title}")),
              fold("LOCATION:" + esc(e.get("location") or "Universität Tübingen")),
              fold("DESCRIPTION:" + esc("\n".join(desc))),
              fold("CATEGORIES:" + esc(e["series"].split(":")[0].split(".")[0].split("?")[0])),
              fold(f"URL:{e.get('url') or d['source']}"),
              "STATUS:" + ("CANCELLED" if e.get("cancelled") else "CONFIRMED"),
              "TRANSP:OPAQUE", "END:VEVENT"]
    L.append("END:VCALENDAR")
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(L) + "\r\n")
    print(f"{len(d['events'])} Termine -> {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:])
