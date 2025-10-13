# 🌌 Noctis Core

**Noctis Core** is a **unified, modular signal-intelligence orchestration framework**.  
It coordinates multiple RF and sensor tools (e.g. KrakenSDR, ADS-B decoders, rtl_433, Kismet, GR-GSM), ingests their outputs into a common schema, stores them across time-series and spatial databases, and presents them through a rich web dashboard with maps, charts, search, and export capabilities.

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

# Then open http://localhost:8080


🧠 Data Model

Each collected event is normalized into a standard Observation object:

Field	Description
ts	ISO timestamp
session_id	e.g. S2025-10-13-001
source	adsb, gsm, ism, bt, kismet, kraken
device_id	Unique identifier (ICAO, cell ID, MAC, etc.)
event	contact, bcch_update, door_open, present, bearing, health
value	Numeric or string payload
loc	{ lat, lon, alt }
meta	Metadata: frequency, RSSI, band, raw payload
