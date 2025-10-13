Noctis Core

Noctis Core is a unified, modular signal-intelligence orchestration framework.
It coordinates multiple RF and sensor tools (e.g. KrakenSDR, ADS-B decoders, rtl_433, Kismet, GR-GSM), ingests their outputs into a common schema, stores them across time-series and spatial databases, and presents them through a web dashboard with maps, charts, search, and export capabilities.

🏗 Architecture & Components

Noctis Core connects to external tools like KrakenSDR, tar1090, Kismet, rtl_433 and GR-GSM.
These tools feed data via HTTP, MQTT, CLI or REST into the Noctis Core backend.
The backend normalizes and stores data in InfluxDB, PostgreSQL/PostGIS and NDJSON/Parquet archives.
The frontend visualizes this information via a unified web dashboard.

Key modules include:

Collector adapters for ADS-B, rtl_433, Kismet, GSM, Kraken

Normalizer to transform raw responses into a unified Observation schema

Storage layers:

Time-series (InfluxDB or Timescale)

Spatial (PostgreSQL + PostGIS)

Archive (NDJSON + Parquet)

REST / WebSocket API for summary, events, search, health, scan control

Frontend dashboard with tiles, map, charts, search and service links

Export pipeline for live (WebSocket/MQTT/optional CoT) and post-scan data (CoT, GeoJSON, CSV, Parquet, SensorThings)

📦 Quick Start

Clone the repository

Create and activate a Python virtual environment

Install backend dependencies using
pip install -r requirements.txt

Run the backend server:
uvicorn noctis_core.backend.app.main:app --reload

Serve the frontend/ directory as static files (via backend or simple HTTP server)

Open the dashboard in a browser and configure collector endpoints / external tool URLs

🧠 Data Model (Observation & Session)

Each collected event is normalized into a JSON observation:

ts – ISO timestamp
session_id – e.g. S2025-10-13-001
source – adsb, gsm, ism, bt, kismet, kraken
device_id – identifier (e.g. ICAO, cell ID, MAC)
event – contact, bcch_update, door_open, present, bearing, health
value – numeric or string data
loc – object with lat/lon/alt
meta – additional metadata like frequency, RSSI, band, raw payload

A ScanSession stores metadata about each scan (start/end time, receivers, flags, export options, etc.).

🔍 Search & Query Capabilities

Quicksearch / full-text over device IDs and metadata

Faceted filters (source, event, session, frequency band)

Time range filtering

Geo search using polygons or radius

Saved query templates (e.g. “ADS-B flights over my location in last 24 h”)

🗂 Storage & Export Formats

Time-series: InfluxDB or TimescaleDB

Spatial: PostgreSQL + PostGIS

Archive: NDJSON & Parquet per session/day

Exports: CoT ZIP, GeoJSON FeatureCollections, CSV/NDJSON, Parquet, SensorThings bundles

🚀 Next Milestones

Implement and integrate collector adapters

Connect them to storage pipelines

Complete API logic for each endpoint

Improve frontend: map, charts, search UI

Build export engine

Add health monitoring, logging, error handling, and security

📚 Standards & References

OGC SensorThings API – open spatial standard for observations

MQTT extension for SensorThings – publish/subscribe for observations

Sensor Observation Service (SOS) – earlier OGC standard in the same domain

🛡 Security & Network Model

All backend and collector services bind only to the ZeroTier interface

Authentication and authorization for API and UI

Health checks, logging, fallback handling, provenance metadata



-------------------------------------------------------------------

⚠️ Disclaimer

Noctis Core is intended for research and laboratory use only.
It does not perform or enable active interception, decoding, or manipulation of any protected communication.
All signal collection, monitoring, and analysis should comply with local laws and frequency regulations.
The authors and contributors assume no liability for misuse, data collection outside permitted frequency bands, or any activity violating applicable regulations.

Use responsibly — this project is designed for testing, education, and controlled lab environments only.


-------------------------------------------------------------------



🏷 License & Contributions

Noctis Core is open for extension.
Contributions such as new collectors, UI modules, or integrations are welcome.
