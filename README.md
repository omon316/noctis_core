````markdown
# 🌌 Noctis Core

Noctis Core is a modular data-collection and visualization platform designed to orchestrate multiple RF- and sensor-based tools and It provides a unified interface to launch, monitor, and aggregate results from these systems into a structured, searchable, and visually rich dashboard.
---

## 🏗️ Architecture & Components

**Noctis Core** acts as the central hub connecting to external tools such as **KrakenSDR**, **tar1090**, **Kismet**, **rtl_433**, and **GR-GSM**.  
These tools feed their data into the backend via **HTTP, MQTT, CLI, or REST**.  
The backend normalizes, indexes, and stores data in **InfluxDB**, **PostgreSQL/PostGIS**, and **NDJSON/Parquet** archives.  
The frontend provides a **unified dashboard** for visualization and control.

### 🔧 Core Modules
- **Collector Adapters** for ADS-B, rtl_433, Kismet, GSM, Kraken  
- **Normalizer** to unify raw data into a common Observation schema  
- **Storage Layers:**
  - 🕒 Time-series: InfluxDB / TimescaleDB  
  - 🌍 Spatial: PostgreSQL + PostGIS  
  - 📦 Archive: NDJSON + Parquet  
- **API Layer:** REST / WebSocket for summary, events, search, health, and scan control  
- **Frontend Dashboard:** Tiles, map, charts, search, and service links  
- **Export Engine:** Live (WebSocket/MQTT/CoT) and post-scan (CoT, GeoJSON, CSV, Parquet, SensorThings)

---

## ⚡ Quick Start

```bash
# 1️⃣ Clone the repository
git clone https://github.com/yourusername/noctis-core.git
cd noctis-core

# 2️⃣ Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the backend server
uvicorn noctis_core.backend.app.main:app --reload

# 5️⃣ Serve the frontend
cd frontend
python3 -m http.server 8080
````

Then open **[http://localhost:8080](http://localhost:8080)** and configure your collector endpoints or external tool URLs.

---

## 🧠 Data Model

Each collected event is normalized into a standard **Observation** object:

| Field        | Description                                               |
| ------------ | --------------------------------------------------------- |
| `ts`         | ISO timestamp                                             |
| `session_id` | e.g. `S2025-10-13-001`                                    |
| `source`     | adsb, gsm, ism, bt, kismet, kraken                        |
| `device_id`  | Unique identifier (ICAO, cell ID, MAC, etc.)              |
| `event`      | contact, bcch_update, door_open, present, bearing, health |
| `value`      | Numeric or string payload                                 |
| `loc`        | `{ lat, lon, alt }`                                       |
| `meta`       | Metadata: frequency, RSSI, band, raw payload              |

🗃️ **ScanSession** stores metadata about each scan, including:

* Start & end time
* Receiver configuration
* Flags, export options
* Environment metadata

---

## 🔍 Search & Query Capabilities

* **Quicksearch** / full-text search across IDs and metadata
* **Faceted filters**: source, event, session, frequency band
* **Time range** filtering
* **Geo search** (polygon / radius)
* **Saved queries** for common views

  > Example: “ADS-B flights over my location in the last 24h”

---

## 🗂️ Storage & Export Formats

| Type           | Technology                               | Description            |
| -------------- | ---------------------------------------- | ---------------------- |
| ⏱️ Time-Series | InfluxDB / TimescaleDB                   | Fast temporal storage  |
| 🗺️ Spatial    | PostgreSQL + PostGIS                     | Geospatial indexing    |
| 💾 Archive     | NDJSON / Parquet                         | Long-term session data |
| 📤 Exports     | CoT, GeoJSON, CSV, Parquet, SensorThings | Flexible data sharing  |

---

## 🚀 Roadmap / Next Milestones

* [ ] Implement and integrate collector adapters
* [ ] Connect adapters to unified storage pipelines
* [ ] Finalize REST / WebSocket API logic
* [ ] Enhance frontend map, charts, and search UI
* [ ] Build export engine (CoT, GeoJSON, Parquet)
* [ ] Add health monitoring, logging, and security layers

---

## 📚 Standards & References

* [OGC SensorThings API](https://www.ogc.org/standards/sensorthings) — Open standard for IoT observations
* MQTT extensions for SensorThings
* OGC Sensor Observation Service (SOS) — legacy standard reference

---

## 🛡️ Security & Network Model

* All backend & collector services bind to the **ZeroTier interface**
* API and UI protected with **authentication & authorization**
* Built-in **health checks**, structured **logging**, and **provenance metadata**

---

## ⚠️ Disclaimer

> **Noctis Core** is intended for **research and laboratory use only**.
> It does **not** perform or enable active interception, decoding, or manipulation of any protected communication.
> Always comply with **local laws** and **frequency regulations** when collecting or processing signals.
>
> The authors and contributors assume **no liability** for misuse or illegal activities.

🧭 Use responsibly — this framework is built for **testing, education, and controlled lab environments** only.

---

## 🏷️ License & Contributions

**Contributions welcome!**
New collectors, UI modules, integrations, or documentation improvements are highly appreciated.

📄 License: *[Insert your license here — e.g. MIT, GPLv3, Apache 2.0]*
🤝 Pull requests and issues are welcome at:
[https://github.com/yourusername/noctis-core](https://github.com/yourusername/noctis-core)

---

> Made with ❤️ by signal intelligence enthusiasts
> *“Observe, not interfere.”*

```
