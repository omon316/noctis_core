"""
NoctisCore - Flask Backend (CLEANED)
=====================================

Bereinigte Version:
- Doppelte Routes entfernt
- Alle View-Routes hinzugefügt
- Extended Stats integriert
"""

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime

# ========================= IMPORTS =========================

# Import Scanner APIs
try:
    from api.bluetooth_api import (
        start_bluetooth_scan,
        stop_bluetooth_scan,
        get_bluetooth_status,
        perform_manual_scan
    )
    BT_API_AVAILABLE = True
except ImportError as e:
    BT_API_AVAILABLE = False
    print(f"⚠️ Bluetooth API nicht verfügbar: {e}")

# Import Stats API
try:
    from api.stats_api import (
        get_overview_stats,
        get_top_devices_data,
        get_detailed_device_stats,
        get_hourly_stats,
        get_daily_stats,
        get_weekday_stats,
        get_activity_heatmap,
        get_advanced_stats,
        get_all_stats
    )
    STATS_API_AVAILABLE = True
except ImportError as e:
    STATS_API_AVAILABLE = False
    print(f"⚠️ Stats API nicht verfügbar: {e}")

# Import Stats Extensions
try:
    from api.stats_extensions import get_extended_stats
    STATS_EXTENSIONS_AVAILABLE = True
except ImportError:
    # Fallback: try importing from stats_api if merged
    try:
        from api.stats_api import get_extended_stats
        STATS_EXTENSIONS_AVAILABLE = True
    except ImportError as e:
        STATS_EXTENSIONS_AVAILABLE = False
        print(f"⚠️ Stats Extensions nicht verfügbar: {e}")

# Import Logs API
try:
    from api.logs_api import (
        get_logs_data,
        get_recent_logs,
        search_logs_api,
        export_logs
    )
    LOGS_API_AVAILABLE = True
except ImportError as e:
    LOGS_API_AVAILABLE = False
    print(f"⚠️ Logs API nicht verfügbar: {e}")

# Import Map API
try:
    from api.map_api import (
        get_gps_statistics,
        get_map_markers,
        get_device_positions,
        get_heatmap_data,
        get_location_hotspots,
        get_movement_analysis,
        get_device_track,
        get_all_map_data
    )
    MAP_API_AVAILABLE = True
except ImportError as e:
    MAP_API_AVAILABLE = False
    print(f"⚠️ Map API nicht verfügbar: {e}")

# ========================= FLASK APP =========================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'noctis-core-secret-key'

# Pfade
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_PATH = BASE_DIR / "logs" / "bluetooth_scan.log"

# Globaler State
scanner_state = {
    "bluetooth": {
        "running": False,
        "last_scan": None,
        "device_count": 0,
        "devices": []
    },
    "wifi": {
        "running": False,
        "last_scan": None,
        "device_count": 0,
        "devices": []
    },
    "rf": {
        "running": False,
        "last_scan": None,
        "device_count": 0,
        "devices": []
    }
}

# ========================= HELPER FUNCTIONS =========================

def load_config():
    """Lädt die Konfiguration"""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "demo_mode": False,
        "telegram_token": "",
        "telegram_chat_id": "",
        "gps_enabled": False
    }

def save_config(config):
    """Speichert die Konfiguration"""
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

def read_logs(limit=100):
    """Liest die letzten Log-Einträge"""
    if not LOG_PATH.exists():
        return []
    
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    return lines[-limit:] if len(lines) > limit else lines

def parse_log_entry(line):
    """Parst eine Log-Zeile"""
    try:
        parts = line.strip().split()
        if len(parts) >= 6:
            return {
                "timestamp": f"{parts[1]} {parts[2]}",
                "mac": parts[5],
                "name": " ".join(parts[6:]) if len(parts) > 6 else "Unknown",
                "scanner": "bluetooth"
            }
    except:
        pass
    return None

# ========================= VIEW ROUTES =========================

@app.route('/')
def index():
    """Haupt-Dashboard (HOME)"""
    return render_template('dashboard.html')

@app.route('/stats')
def stats_page():
    """STATS View"""
    return render_template('stats.html')

@app.route('/logs')
def logs_page():
    """LOGS View"""
    return render_template('logs.html')

@app.route('/map')
def map_page():
    """MAP View"""
    return render_template('map.html')

@app.route('/watch')
def watch_page():
    """WATCH View"""
    return render_template('watch.html')

@app.route('/export')
def export_page():
    """EXPORT View"""
    return render_template('export.html')

# ========================= SYSTEM APIS =========================

@app.route('/api/status')
def get_status():
    """System-Status"""
    # Aktualisiere Bluetooth-Status von der API
    if BT_API_AVAILABLE:
        bt_status = get_bluetooth_status()
        scanner_state["bluetooth"].update(bt_status)
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "scanners": scanner_state,
        "apis": {
            "bluetooth": BT_API_AVAILABLE,
            "stats": STATS_API_AVAILABLE,
            "stats_extensions": STATS_EXTENSIONS_AVAILABLE,
            "logs": LOGS_API_AVAILABLE,
            "map": MAP_API_AVAILABLE
        }
    })

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Konfiguration laden/speichern"""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({"success": True})
    
    return jsonify(load_config())

@app.route('/api/logs')
def get_logs():
    """Logs abrufen (Legacy)"""
    limit = request.args.get('limit', 100, type=int)
    lines = read_logs(limit)
    
    logs = []
    for line in lines:
        entry = parse_log_entry(line)
        if entry:
            logs.append(entry)
    
    return jsonify(logs)

@app.route('/api/devices')
def get_devices():
    """Alle Geräte abrufen"""
    all_devices = []
    
    # Bluetooth-Geräte
    if BT_API_AVAILABLE:
        bt_status = get_bluetooth_status()
        all_devices.extend(bt_status.get("devices", []))
    
    # Logs als Fallback
    if not all_devices:
        logs = read_logs(1000)
        devices = {}
        
        for line in logs:
            entry = parse_log_entry(line)
            if entry:
                mac = entry['mac']
                if mac not in devices:
                    devices[mac] = entry
        
        all_devices = list(devices.values())
    
    return jsonify(all_devices)

@app.route('/api/search')
def search():
    """Volltext-Suche"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    logs = read_logs(1000)
    results = []
    
    for line in logs:
        entry = parse_log_entry(line)
        if entry:
            if query in entry['mac'].lower() or query in entry['name'].lower():
                results.append(entry)
    
    return jsonify(results[:10])

# ========================= SCANNER ENDPOINTS =========================

@app.route('/api/scanner/<scanner_type>/start', methods=['POST'])
def start_scanner(scanner_type):
    """Scanner starten"""
    if scanner_type == "bluetooth" and BT_API_AVAILABLE:
        result = start_bluetooth_scan()
        if result["success"]:
            scanner_state[scanner_type]["running"] = True
            scanner_state[scanner_type]["last_scan"] = datetime.now().isoformat()
        return jsonify(result)
    
    return jsonify({"success": False, "error": "Scanner not available"}), 400

@app.route('/api/scanner/<scanner_type>/stop', methods=['POST'])
def stop_scanner(scanner_type):
    """Scanner stoppen"""
    if scanner_type == "bluetooth" and BT_API_AVAILABLE:
        result = stop_bluetooth_scan()
        if result["success"]:
            scanner_state[scanner_type]["running"] = False
        return jsonify(result)
    
    return jsonify({"success": False, "error": "Scanner not available"}), 400

@app.route('/api/scanner/bluetooth/manual', methods=['POST'])
def manual_bluetooth_scan():
    """Manueller Bluetooth-Scan"""
    if not BT_API_AVAILABLE:
        return jsonify({"success": False, "error": "Scanner not available"}), 400
    
    result = perform_manual_scan()
    return jsonify(result)

# ========================= STATS ENDPOINTS =========================

@app.route('/api/stats/overview')
def stats_overview():
    """Übersichts-Statistiken"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    return jsonify(get_overview_stats())

@app.route('/api/stats/top-devices')
def stats_top_devices():
    """Top-Geräte"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    n = request.args.get('n', 10, type=int)
    time_filter = request.args.get('time_filter', None)
    
    return jsonify(get_top_devices_data(n, time_filter))

@app.route('/api/stats/detailed')
def stats_detailed():
    """Detaillierte Geräte-Statistiken"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_detailed_device_stats(time_filter))

@app.route('/api/stats/hourly')
def stats_hourly():
    """Stündliche Aktivität"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_hourly_stats(time_filter))

@app.route('/api/stats/daily')
def stats_daily():
    """Tägliche Aktivität"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    days = request.args.get('days', 30, type=int)
    time_filter = request.args.get('time_filter', None)
    
    return jsonify(get_daily_stats(days, time_filter))

@app.route('/api/stats/weekday')
def stats_weekday():
    """Wochentags-Aktivität"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_weekday_stats(time_filter))

@app.route('/api/stats/heatmap')
def stats_heatmap():
    """Aktivitäts-Heatmap"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_activity_heatmap(time_filter))

@app.route('/api/stats/advanced')
def stats_advanced():
    """Erweiterte Statistiken"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_advanced_stats(time_filter))

@app.route('/api/stats/extended')
def stats_extended():
    """Extended Stats (RSSI, OUI, Protocol, Lifetime)"""
    if not STATS_EXTENSIONS_AVAILABLE:
        return jsonify({"error": "Stats Extensions not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_extended_stats(time_filter))

@app.route('/api/stats/all')
def stats_all():
    """Alle Statistiken"""
    if not STATS_API_AVAILABLE:
        return jsonify({"error": "Stats API not available"}), 503
    
    time_filter = request.args.get('time_filter', None)
    return jsonify(get_all_stats(time_filter))

# ========================= LOGS ENDPOINTS =========================

@app.route('/api/logs/data')
def logs_data():
    """Log-Daten mit Filtern"""
    if not LOGS_API_AVAILABLE:
        return jsonify({"error": "Logs API not available"}), 503
    
    limit = request.args.get('limit', 100, type=int)
    time_filter = request.args.get('time_filter', None)
    
    return jsonify(get_logs_data(limit, time_filter))

@app.route('/api/logs/recent')
def logs_recent():
    """Letzte Log-Einträge"""
    if not LOGS_API_AVAILABLE:
        return jsonify({"error": "Logs API not available"}), 503
    
    n = request.args.get('n', 50, type=int)
    return jsonify(get_recent_logs(n))

@app.route('/api/logs/search')
def logs_search():
    """Log-Suche"""
    if not LOGS_API_AVAILABLE:
        return jsonify({"error": "Logs API not available"}), 503
    
    query = request.args.get('q', '')
    return jsonify(search_logs_api(query))

@app.route('/api/logs/export')
def logs_export():
    """Log-Export"""
    if not LOGS_API_AVAILABLE:
        return jsonify({"error": "Logs API not available"}), 503
    
    format_type = request.args.get('format', 'json')
    time_filter = request.args.get('time_filter', None)
    
    return jsonify(export_logs(format_type, time_filter))

# ========================= MAP ENDPOINTS =========================

@app.route('/api/map/statistics')
def map_statistics():
    """GPS-Statistiken"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    return jsonify(get_gps_statistics())

@app.route('/api/map/markers')
def map_markers():
    """Karten-Marker"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    device_filter = request.args.get('filter', 'all')
    return jsonify(get_map_markers(device_filter))

@app.route('/api/map/devices')
def map_devices():
    """Geräte mit Positionen"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    return jsonify(get_device_positions())

@app.route('/api/map/heatmap')
def map_heatmap():
    """Heatmap-Daten"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    return jsonify(get_heatmap_data())

@app.route('/api/map/hotspots')
def map_hotspots():
    """GPS-Hotspots"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    min_points = request.args.get('min', 3, type=int)
    return jsonify(get_location_hotspots(min_points))

@app.route('/api/map/movement')
def map_movement():
    """Bewegungsanalyse"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    return jsonify(get_movement_analysis())

@app.route('/api/map/track/<mac>')
def map_track(mac):
    """Bewegungsspur für Gerät"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    return jsonify(get_device_track(mac))

@app.route('/api/map/all')
def map_all():
    """Alle Karten-Daten"""
    if not MAP_API_AVAILABLE:
        return jsonify({"error": "Map API not available"}), 503
    
    device_filter = request.args.get('filter', 'all')
    return jsonify(get_all_map_data(device_filter))

# ========================= MAIN =========================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║      NoctisCore Dashboard            ║
    ║      Gotham Tactical Interface       ║
    ╚══════════════════════════════════════╝
    
    🌐 Dashboard: http://localhost:5000
    📊 Stats:     http://localhost:5000/stats
    📋 Logs:      http://localhost:5000/logs
    🗺️  Map:       http://localhost:5000/map
    👁️  Watch:     http://localhost:5000/watch
    📤 Export:    http://localhost:5000/export
    
    🔧 API Docs:  http://localhost:5000/api/status
    
    Press CTRL+C to stop
    """)
    
    # Starte Flask-Server
    app.run(host='0.0.0.0', port=5000, debug=True)
