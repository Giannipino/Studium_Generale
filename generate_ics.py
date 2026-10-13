#!/usr/bin/env python3
"""Erzeugt studium-generale-tuebingen.ics aus events.json (RFC 5545, stabile UIDs)."""
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
        while (b[cut] & 0xC0) == 0x80: cut -= 1  # nicht mitten im UTF-8-Zeichen trennen
        out.append(b[:cut].decode()); b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)

def main(src="events.json", dst="studium-generale-tuebingen.ics"):
    d = json.load(open(src, encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//sg-ics//Studium Generale Tuebingen//DE",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         "X-WR-CALNAME:Studium Generale Uni Tübingen", "X-WR-TIMEZONE:Europe/Berlin",
         "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"] + VTZ.split("\n")
    n = 0
    for s in d["series"]:
        for lec in s["lectures"]:
            date, speaker, title, note = lec[:4]
            loc = lec[4] if len(lec) > 4 and lec[4] else s["location"]
            start = lec[5] if len(lec) > 5 else d["default_start"]
            end = lec[6] if len(lec) > 6 else d["default_end"]
            ymd = date.replace("-", "")
            desc = [f"Reihe: {s['title']}", f"Vortragende: {speaker}"]
            if note: desc.append(f"Hinweis: {note}")
            if s.get("series_note"): desc.append(s["series_note"])
            desc += ["Eintritt frei, ohne Anmeldung. Beginn 18 Uhr c.t. (18:15).", f"Aktuelle Infos: {d['source']}"]
            L += ["BEGIN:VEVENT",
                  f"UID:sg-tue-{s['key']}-{ymd}@studium-generale-ics",
                  f"DTSTAMP:{now}",
                  f"DTSTART;TZID=Europe/Berlin:{ymd}T{start.replace(':','')}00",
                  f"DTEND;TZID=Europe/Berlin:{ymd}T{end.replace(':','')}00",
                  fold("SUMMARY:" + esc(f"StG: {title}")),
                  fold("LOCATION:" + esc(loc)),
                  fold("DESCRIPTION:" + esc("\n".join(desc))),
                  fold("CATEGORIES:" + esc(s["title"].split(":")[0].split(".")[0])),
                  f"URL:{d['source']}",
                  "STATUS:CONFIRMED", "TRANSP:OPAQUE", "END:VEVENT"]
            n += 1
    L.append("END:VCALENDAR")
    open(dst, "w", encoding="utf-8", newline="").write("\r\n".join(L) + "\r\n")
    print(f"{n} Termine -> {dst}")

if __name__ == "__main__":
    main(*sys.argv[1:])
