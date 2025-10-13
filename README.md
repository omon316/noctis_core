---

```markdown
# Noctis Core

**Noctis Core** is a unified, modular signal-intelligence orchestration framework. Its role is to coordinate multiple external RF / sensor tools (e.g. KrakenSDR, ADS-B decoders, rtl_433, Kismet, GR-GSM), ingest their outputs into a common schema, store them in time-series & spatial databases, and present them via a web dashboard with maps, charts, search, and export capabilities.

---

## 🏗 Architecture & Components

```

```
                            +----------------------+
                            | External Tools / UIs |
                            | (Kraken, tar1090,    |
                            |  Kismet, rtl_433, etc)|
                            +-----------+----------+
                                        |
                                        | (HTTP / MQTT / REST / CLI)
                                        |
 +---------------+        +--------------v-------------+     +------------------+
 | Frontend (UI)  | <----> | Noctis Core Backend (API)  | <--> | Storage & Exports |
 | Map, charts,   |        | Collectors, Router, Search |     | Influx / PostGIS /|
 | search, exports|        +-----------------------------+     | NDJSON / Parquet  |
 +---------------+                                              +------------------+
```

````

**Key modules:**

- **Collector adapters** for each data source (ADS-B, rtl_433, Kismet, GSM, Kraken)  
- **Normalizer**: transform raw responses into unified `Observation` schema  
- **Storage layers**:  
  1. Time-series DB (InfluxDB or Timescale)  
  2. Spatial DB (PostgreSQL + PostGIS)  
  3. Archive files (NDJSON, Parquet)  
- **REST / WebSocket API** for summary, events, search, health, scan control  
- **Frontend dashboard**: tiles, map, charts, search, links to external UIs  
- **Export pipeline**: Live (WebSocket/MQTT/optional CoT) & Post-Scan packages (CoT, GeoJSON, CSV, Parquet, optional SensorThings bundles)  

---

## 📦 Quick Start

1. Clone this repository  
2. Setup your Python environment (e.g., `venv`)  
3. Install backend dependencies:  
   ```bash
   cd backend
   pip install -r requirements.txt
````

4. Run backend (development mode):

   ```bash
   uvicorn noctis_core.backend.app.main:app --reload
   ```
5. Serve `frontend/` as static files (e.g., via simple HTTP or via the backend)
6. Open dashboard in browser, configure collectors & external tool URLs

---

## 🧠 Data Model (Observation & Session)

```json
{
  "ts": "YYYY-MM-DDThh:mm:ssZ",
  "session_id": "S2025-10-13-001",
  "source": "adsb|gsm|ism|bt|kismet|kraken|…",
  "device_id": "icao-ABC123|cell-…|mac-…",
  "event": "contact|bcch_update|door_open|present|bearing|health",
  "value": "number|string|null",
  "loc": { "lat": 50.9, "lon": 6.9, "alt": 830 },
  "meta": { "freq": 1090000000, "rssi": -37, "raw": "...", "band": "…" }
}
```

A **ScanSession** also stores metadata about each scanning task (start, end, which receivers, config flags, export options, etc.).

---

## 🔍 Search & Query Capabilities

* **Quicksearch / Full-text** over labels, device IDs, metadata
* **Faceted filters**: by source, event type, session, device, frequency band
* **Time range** filters
* **Geo queries**: draw polygon or use radius → filter observations by spatial relation
* **Saved templates**: e.g. “ADS-B flights over my house in last 24 h”

---

## 🗂 Storage & Export Formats

* **Time-series**: InfluxDB or Timescale (measurements, tags, fields)
* **Spatial**: PostgreSQL + PostGIS for geometry queries
* **Archive**: NDJSON & Parquet per session / day
* **Exports**: CoT ZIP, GeoJSON FeatureCollections, CSV/NDJSON, Parquet, SensorThings bundles

---

## 🚀 Next Milestones

1. Implement and integrate collector adapters
2. Connect them to the storage pipelines
3. Fill out API endpoints with real-data logic
4. Improve frontend: map, charts, search UI
5. Build export engine
6. Add health monitoring, logging, error handling, security

---

## 📚 Standards & References

* **OGC SensorThings API** (Sensing part) — open, spatially enabled standard for observations. ([Wikipedia][1])
* **MQTT extension for SensorThings** (publish/subscribe observations) ([developers.sensorup.com][2])
* **Sensor Observation Service (SOS)**, earlier OGC standard, conceptually related. ([Wikipedia][3])

---

## 🛡 Security & Network Model

* All backend & collector services bind only to ZeroTier interface (no public exposure)
* Authentication / authorization for API & UI
* Health checks, error fallback, logging & provenance

---

## 🏷 License & Contribution

Noctis Core is open for extension. Contributions (plugins, new collector modules, UI enhancements) are welcome.

---

*End of README*

```

Wenn du willst, kann ich dir auch eine **kompakte Version** dieses README (für die GitHub-Startseite) und eine **ausführliche Dokumentation** (für `docs/`) generieren — möchtest du das?
::contentReference[oaicite:3]{index=3}
```

[1]: https://en.wikipedia.org/wiki/SensorThings_API?utm_source=chatgpt.com "SensorThings API"
[2]: https://developers.sensorup.com/tutorials/mqtt/?utm_source=chatgpt.com "SensorThings API - Getting Started with MQTT | SensorUp OGC SensorThings API Developer Centre"
[3]: https://en.wikipedia.org/wiki/Sensor_Observation_Service?utm_source=chatgpt.com "Sensor Observation Service"
