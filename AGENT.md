# Anleitung für den Claude-Fallback

Normalerweise aktualisiert `scrape.py` die Termine automatisch. Diese Anleitung gilt nur, wenn das Skript fehlschlägt.

1. **Quelle:** https://uni-tuebingen.de/universitaet/im-dialog/studium-generale/ (per `curl -sLf`, sonst WebFetch).
   Unter „Themenübersicht“ stehen die Vorlesungsreihen; jeder Termin verlinkt auf eine Veranstaltungsseite
   (`/news-default/article/...`) mit Datum, Uhrzeit, Veranstaltungsort und Referent/in. Alle Termine öffnen.
   Falls die Seite unbrauchbar ist: das dort verlinkte Programm-PDF (`pdftotext -layout`), zuletzt WebSearch.
2. **`events.json` aktualisieren** – Format: `{"source": "...", "events": [ {uid, date (YYYY-MM-DD), start (HH:MM),
   end (HH:MM; Standard Start + 90 min), title, series, speaker, location, note, cancelled (bool), url} ]}`.
   - `uid` bestehender Termine NIE ändern (sonst Dubletten in Google). Neue Termine: `sg-tue-<news-id>` aus
     `data-news-id` der Veranstaltungsseite, sonst `sg-tue-<kurzer-slug>`.
   - Abgesagte Termine nicht löschen, sondern `cancelled: true` setzen. Vergangene Termine behalten.
3. **Prüfen:** keine doppelten UIDs, Wochentage plausibel. Dann `python3 generate_ics.py`.
4. **Nicht selbst committen.** Bericht in `LETZTER_LAUF.md`: was geändert wurde, welche Quellen lesbar waren,
   warum `scrape.py` vermutlich scheiterte. Nichts raten – Unklares im Bericht nennen.
