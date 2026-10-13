# Studium Generale Uni Tübingen – Kalender (ICS)

Alle öffentlichen Vorlesungen des Studium Generale der Universität Tübingen als abonnierbarer Kalender.

- Daten: `events.json` (aus der Programmbroschüre / https://uni-tuebingen.de/studium-generale)
- Generator: `python3 generate_ics.py`
- Aktualisierung: wöchentlich per GitHub Action (`.github/workflows/update.yml`) mit Claude, Anleitung in `AGENT.md`

**In Google Kalender abonnieren:** Weitere Kalender → „Per URL“ → Raw-URL von `studium-generale-tuebingen.ics` einfügen.
Google aktualisiert abonnierte Kalender selbstständig (typischerweise alle 12–24 Stunden).

Ohne Gewähr – maßgeblich sind die Angaben der Universität.
