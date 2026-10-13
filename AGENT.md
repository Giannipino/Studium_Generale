# Update-Anleitung für den Studium-Generale-Agenten

Ziel: `studium-generale-tuebingen.ics` in diesem Repo stets aktuell halten. Google Kalender abonniert die Raw-URL der Datei.

## Ablauf (wöchentlich)

1. **Programm lesen.** Quellen in dieser Reihenfolge. Bevorzugt die PDF-Broschüre per `curl -sLf -o /tmp/sg.pdf <URL>` laden und mit `pdftotext -layout /tmp/sg.pdf -` vollständig lesen; falls die Shell die Seite nicht erreicht, WebFetch nutzen:
   - Programmbroschüre: `https://uni-tuebingen.de/fileadmin/Uni_Tuebingen/Universitaet/Im_Dialog/Studium_Generale/Studium_Generale_<SEM>_Broschuere_web.pdf`
     mit `<SEM>` = `WiSe26`, `SoSe27`, `WiSe27` … (aktuelles und nächstes Semester probieren).
   - Studium-Generale-Seite: https://uni-tuebingen.de/universitaet/im-dialog/studium-generale/ (Hinweise auf Ausfälle, Raum-/Terminänderungen)
   - Falls nichts gefunden: WebSearch „Studium Generale Universität Tübingen <Semester>“ und Pressemitteilungen der Uni.
   Für jede Reihe ALLE Einzeltermine vollständig erfragen (Datum, Vortragende, Titel, Raum, Hinweise wie Englisch/anderer Raum/Ausfall).

2. **`events.json` aktualisieren.**
   - Format: `series[].lectures[] = [Datum, Vortragende, Titel, Hinweis, (optional) abweichender Ort, (optional) Start, (optional) Ende]`.
   - Standardzeit 18:15–19:45 („18 Uhr c.t.“); abweichende Zeiten als Feld 6/7 eintragen.
   - Abgesagte Termine nicht löschen, sondern Hinweis „ABGESAGT“ setzen und Titel mit „ABGESAGT: “ beginnen.
   - Neues Semester: neue Reihen mit neuem eindeutigem `key` ergänzen; vergangene Semester dürfen drin bleiben (max. 2 Semester zurück).
   - `key` und Datum bilden die UID – bestehende `key`s nie umbenennen, sonst entstehen Dubletten in Google.

3. **Plausibilität prüfen:** Wochentag jedes Termins passt zur Reihe; keine doppelten (key, Datum); Datumsformat YYYY-MM-DD.

4. **Erzeugen:** `python3 generate_ics.py` → schreibt `studium-generale-tuebingen.ics`.

5. **Nicht selbst committen.** Der GitHub-Workflow erzeugt die ICS-Datei neu und committet nur, wenn sich `events.json` geändert hat.

6. **Bericht:** Kurz melden, was sich geändert hat (neue/geänderte/abgesagte Termine) oder „keine Änderungen“. Bei Unsicherheiten (unklare Zuordnung, Quelle nicht lesbar) nichts raten, sondern im Bericht nennen.
