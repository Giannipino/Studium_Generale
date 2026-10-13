# Studium Generale Uni Tübingen – Kalender (ICS)

Alle öffentlichen Vorlesungen des Studium Generale der Universität Tübingen als abonnierbarer Kalender.

- Quelle: https://uni-tuebingen.de/universitaet/im-dialog/studium-generale/ und die dort verlinkten Veranstaltungsseiten
- `scrape.py` liest alle Termine → `events.json`; `generate_ics.py` erzeugt daraus `studium-generale-tuebingen.ics`
- GitHub Action (`.github/workflows/update.yml`) läuft täglich und committet nur bei Änderungen.
  Scheitert das Skript, übernimmt optional Claude (Secret `ANTHROPIC_API_KEY`, Anleitung in `AGENT.md`).

**In Google Kalender abonnieren:** Weitere Kalender → „Per URL“ →
`https://raw.githubusercontent.com/Giannipino/Studium_Generale/main/studium-generale-tuebingen.ics`
Google aktualisiert abonnierte Kalender selbstständig (typischerweise alle 12–24 Stunden).

Ohne Gewähr – maßgeblich sind die Angaben der Universität.
