
API-Module (bestehende) — Rolle & Wishlist
1) api/bluetooth_api.py

Rolle: Steuerung/Trigger für BT-Scans, Quick-Status, manuelle Scans.
Ist-Funktionalität (laut dir):

start_bluetooth_scan()

stop_bluetooth_scan()

perform_manual_scan()

Wishlist:

Scan-Sessions: Sitzungs-IDs, Start/Ende, Metadaten (Adapter, Dauer, Quelle).

Scan-Status: aktueller State (running, last_heartbeat, devices_seen_last_x_min).

Adapter-Info: verfügbare Adapter, MAC, Name, TX-Power/Capabilities (wenn verfügbar).

Scan-Profile: Presets (Classic, BLE-only, Classic+BLE+GPS), Timeouts, Intervallsteuerung.

Quoten & Limits: Rate-Limits pro Minute, Cooldowns, Safety-Schalter.

Telemetry: Stats pro Session (Anzahl Geräte, Watchlist-Treffer, Fehler).

Export Hooks: Session-Export (CSV/JSON) mit Filter (Zeitraum, RSSI-Min, Watchlist-only).

Event Hooks: On-Scan-Complete → Notify (z. B. WebSocket/Server-Sent Events).

2) api/logs_api.py

Rolle: Log-Backend (Viewer, Suche, Export).
Ist-Funktionalität:

get_logs_data()

get_recent_logs()

search_logs_api()

get_log_statistics()

export_logs()

Wishlist:

Facettierte Suche: Filter nach Quelle (bt/wifi/rf), Level (info/warn/error), Session-ID.

Zeit-Range-Presets: last 1h/24h/7d/30d.

Aggregation: Top-Fehlertypen, häufigste Watchlist-Treffer, häufigste Adapter-Fehler.

Anreicherungen: OUI/Hersteller, Device-Type-Heuristik in Logzeilen.

Retention-Policy: Lösch- und Archivregeln, Audit-Log für Exporte.

Diff-/Vergleich: zwei Zeitfenster gegenüberstellen.

Live-Stream: SSE/WebSocket-Feed für neue Logevents (für logs.html).

3) api/map_api.py

Rolle: Karten-/Geo-Backend (Marker, Heatmaps, Tracks).
Ist-Funktionalität:

get_map_markers()

get_device_positions()

get_heatmap_data()

get_location_hotspots()

get_movement_analysis()

get_device_track()

Wishlist:

Geo-Filter: bounding box, polygon, radius, plus Zeitfenster.

Clustering: serverseitige Marker-Clustering (zoombasierte Auflösung).

Geo-Alerts: Geofences + Watchlist (enter/leave), Quiet Hours.

Confidence: Unsicherheiten (RSSI→Distanz Heuristik), Qualitätsindikatoren pro Marker.

Snap-to-Session: Tracks pro Scan-Session; Session-Fokus in map.html.

Export Geo: GeoJSON/KML mit Metadaten (Quelle, Zeit, Confidence).

Multi-Source-Fusion: BT/WiFi/RF-Layer gemeinsam rendern (ein-/ausblendbar).

(Optional) DF/Azimuth-Layer: spätere Integration von Richtungslinien (KrakenSDR).

4) api/stats_api.py

Rolle: Kernstatistiken / KPIs für Dashboard & Stats-Seite.
Ist-Funktionalität (laut dir):

get_overview_stats() – Total Scans, Unique Devices, Last 24h

get_top_devices_data() – Top 10 Geräte

get_hourly_stats() – 24h stündlich

get_daily_stats() – 30d täglich

get_weekday_stats() – Wochentage

get_activity_heatmap() – Stunde × Wochentag

get_all_stats() – Sammelaufruf

Wishlist:

OUI/Hersteller KPIs: Top Hersteller, Anteil Randomized MACs.

RSSI-Analytik: Distributionen (Median/Quartile), Top-N nach RSSI.

Gerätetypen: Phone/Headset/Wearable/IoT (Heuristik), Anteil pro Tag.

Protocol-Mix: BLE vs. Classic vs. WiFi (sofern Messbar).

Trend-Detektion: 7-Tage & 30-Tage Trends, „Rising Devices“.

Saisonale Muster: Wochen-/Wochenend-Pattern, Uhrzeit-Heatmaps je Gerätetyp.

Anomalie-Flags: Ausreißer in Aktivität (StdDev-basiert), peaky hours.

Export: CSV/JSON-Bulk für BI.

5) api/stats_extensions.py

Rolle: Erweiterte/komplexe Statistiken; Rechenlast-Bündelung.
Wishlist:

Correlation Views: Korrelation zwischen Zeitfenstern, Frequenzbändern, Standorten.

Occupancy (RF): Kanalbelegung (2.4/5 GHz), Spektral-Heatmaps (falls RF-Daten vorliegen).

Forecasts: einfache Vorhersagen (z. B. nächste Stunde Aktivität).

Clustering: Geräte-Cluster nach Verhalten (Anwesenheitsprofile).

Baseline/Drift: abgeleitete Normalwerte und Abweichungen.

6) api/utils.py

Rolle: Hilfsfunktionen, gemeinsame Validatoren, DTO-Bausteine, Zeit-/Format-Helfer.
Wishlist:

Einheitliche DTOs (dict-Strukturen) für Devices, Logs, Marker, Stats.

Input-Validierung: Zeitfenster, MAC-Formate, Bounds.

Paging/Rate-Limit-Helper.

OUI-Cache: Herstellerlookup & Caching.

Error-Envelope: standardisierte Fehlerantworten (message, code, hint).

Empfohlene neue API-Module (namenkompatibel zu deinem Tree)

Hinweis: Nur Vorschläge — anlegen unter api/…. Passen zu deinen bestehenden Templates / geplanten Features.

7) api/watch_api.py (für templates/watch.html)

Rolle: Watchlist-CRUD & Alert-Policies.
Wishlist:

CRUD: add/remove/update (MAC, Label, Notes, Level).

Policies: Geo-Fence, Zeitfenster, Quiet Hours, Severity.

Trefferhistorie: letzte Sichtungen, Frequenz, Orte.

Import/Export: CSV/JSON für Watchsets.

Ack/Resolve: Bestätigen/Schließen von Alerts mit Kommentar.

8) api/alerts_api.py

Rolle: Zentrales Alert-Backend (statt verteilter Logik).
Wishlist:

Types: watchlist, new_device, anomaly, system.

Status: open, acknowledged, resolved, muted (mit TTL).

Streams: Live-Feed (SSE/WebSocket) für UI-Bell.

Rules: Suppression, dedupe, cooldowns.

Audit: Wer hat was bestätigt/geschlossen.

9) api/devices_api.py

Rolle: Geräte-Katalog und Detail-Ansicht.
Wishlist:

Directory: Paginierte Geräteliste, Filter (Hersteller, Typ, Status).

Details: Historie, Sessions, RSSI-Timeline, Orte (mit Link zu Map).

Tagging: Labels/Notizen je Gerät.

Merge: Duplikaterkennung (z. B. Random MAC-Rotation → Gruppierung).

Export: Gerätestamm als CSV/JSON.

10) api/rf_api.py

Rolle: RF-/Spektrum-Endpunkte (falls RF schon eingespeist wird).
Wishlist:

Waterfall/Occupancy: Aggregierte Spektren, Kanalbelegung.

Snapshots: Speichern/Listen/Löschen.

Profiles: definierte Scans (2.4 GHz, 5 GHz, ISM 433/868).

Anomalies: Interferenz-Detektion, Bursts, Radar-Likes.

11) api/df_api.py (später, KrakenSDR/DF)

Rolle: Direction Finding / Bearing & Triangulation.
Wishlist:

Bearing: Azimut-Messungen mit Confidence.

Tracks: Intersections/Heatmaps aus mehreren Stationen.

Exports: GeoJSON Linien, Bearing-Fächer.

Calibration: Status/Offsets als Metadaten.

Frontend/Static (Klarheit im Tree)

static/css/noctis.css
Zentrales Theme/Variablen; Wishlist: Variablen für Farben, Abstände, Badges; Utility-Klassen.

static/js/dashboard.js
AJAX/Fetch für Overview + Live-Widgets.

static/js/stats.js
Charts/Heatmaps; Wishlist: modulare Chart-Initialisierung, Reuse für stats.html.

static/js/dashboard.old.js & templates/old/*
Hinweis: perspektivisch archivieren/entfernen, um Verwechslungen zu vermeiden.

Optional: Routing/Ownership-Empfehlung (ohne Code)

Blueprints je API-Modul (klarer Präfix, z. B. /api/stats/*, /api/logs/*, …).

Responsibility:

stats_api.py liefert nur Zahlen/Datensätze für KPIs/Charts.

stats_extensions.py rechenintensive/fortgeschrittene Analysen.

logs_api.py ausschließlich Log-Operationen (keine Device-Logik mischen).

map_api.py rein geo-bezogen (Marker/Heatmap/Tracks).

bluetooth_api.py rein für Scanner-Steuerung + Highlevel-Status.

neu: watch_api.py, alerts_api.py, devices_api.py, rf_api.py, df_api.py.
