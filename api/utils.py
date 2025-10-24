"""
NoctisCore Utilities
====================

Shared functions migriert von Streamlit noctis_utils.py
Funktioniert mit Flask Backend
"""

from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
import re

# ========================= PATHS =========================

BASE_DIR = Path(__file__).parent.parent
LOG_PATH = BASE_DIR / "logs" / "bluetooth_scan.log"
CONFIG_PATH = BASE_DIR / "config.json"
WATCHLIST_PATH = BASE_DIR / "watchlist.json"

# ========================= PARSING =========================

def parse_device_string(device_str: str) -> dict:
    """
    Parst Device-String aus Logs
    
    Format: "001 14 1230 OCT AA:BB:CC:DD:EE:FF Device_Name [lat lon]"
    """
    parts = device_str.strip().split()
    
    if len(parts) < 6:
        return None
    
    result = {
        "id": parts[0],
        "day": parts[1],
        "time": parts[2],
        "month": parts[3],
        "mac": parts[4],
        "name": " ".join(parts[5:]) if len(parts) > 5 else "Unknown",
        "timestamp": f"{parts[1]} {parts[3]} {parts[2]}",
        "lat": None,
        "lon": None
    }
    
    # GPS-Daten extrahieren (wenn vorhanden)
    if len(parts) >= 7:
        try:
            lat = float(parts[-2])
            lon = float(parts[-1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                result["lat"] = lat
                result["lon"] = lon
                result["name"] = " ".join(parts[5:-2])
        except (ValueError, IndexError):
            pass
    
    return result

def parse_log_line(line: str) -> dict:
    """Parst eine komplette Log-Zeile"""
    try:
        device = parse_device_string(line)
        if device:
            return {
                "timestamp": device["timestamp"],
                "mac": device["mac"],
                "name": device["name"],
                "lat": device.get("lat"),
                "lon": device.get("lon"),
                "raw": line.strip()
            }
    except Exception as e:
        print(f"Parse error: {e}")
    return None

def get_parsed_logs(limit=None):
    """
    Liest und parst alle Logs
    
    Returns:
        List[dict]: Geparste Log-Einträge
    """
    if not LOG_PATH.exists():
        return []
    
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    if limit:
        lines = lines[-limit:]
    
    parsed = []
    for line in lines:
        entry = parse_log_line(line)
        if entry:
            parsed.append(entry)
    
    return parsed

# ========================= STATISTICS =========================

def get_device_count(logs=None):
    """Zählt eindeutige Geräte"""
    if logs is None:
        logs = get_parsed_logs()
    
    macs = set(log["mac"] for log in logs)
    return len(macs)

def get_top_devices(n=10, logs=None):
    """
    Gibt Top-N Geräte nach Anzahl zurück
    
    Returns:
        List[tuple]: [(mac, name, count), ...]
    """
    if logs is None:
        logs = get_parsed_logs()
    
    device_counts = Counter()
    device_names = {}
    
    for log in logs:
        mac = log["mac"]
        device_counts[mac] += 1
        if log["name"] != "Unknown":
            device_names[mac] = log["name"]
    
    top = []
    for mac, count in device_counts.most_common(n):
        name = device_names.get(mac, "Unknown")
        top.append((mac, name, count))
    
    return top

def get_mac_statistics(logs=None):
    """
    Detaillierte Statistiken pro MAC
    
    Returns:
        dict: {mac: {"name": str, "count": int, "first": str, "last": str}}
    """
    if logs is None:
        logs = get_parsed_logs()
    
    stats = defaultdict(lambda: {
        "name": "Unknown",
        "count": 0,
        "first": None,
        "last": None,
        "positions": []
    })
    
    for log in logs:
        mac = log["mac"]
        stats[mac]["count"] += 1
        
        if log["name"] != "Unknown":
            stats[mac]["name"] = log["name"]
        
        timestamp = log["timestamp"]
        if stats[mac]["first"] is None:
            stats[mac]["first"] = timestamp
        stats[mac]["last"] = timestamp
        
        if log.get("lat") and log.get("lon"):
            stats[mac]["positions"].append({
                "lat": log["lat"],
                "lon": log["lon"],
                "timestamp": timestamp
            })
    
    return dict(stats)

# ========================= TIME ANALYSIS =========================

def get_hourly_activity(logs=None):
    """
    Aktivität nach Stunden
    
    Returns:
        dict: {hour: count}
    """
    if logs is None:
        logs = get_parsed_logs()
    
    hourly = Counter()
    
    for log in logs:
        try:
            # Extract hour from timestamp
            time_str = log["timestamp"].split()[2]  # "1230"
            hour = int(time_str[:2])
            hourly[hour] += 1
        except (ValueError, IndexError):
            continue
    
    # Fill missing hours with 0
    return {hour: hourly.get(hour, 0) for hour in range(24)}

def get_daily_activity(logs=None, days=30):
    """
    Aktivität nach Tagen
    
    Returns:
        dict: {date: count}
    """
    if logs is None:
        logs = get_parsed_logs()
    
    daily = Counter()
    
    for log in logs:
        try:
            # Extract day from timestamp
            day = log["timestamp"].split()[0]
            daily[day] += 1
        except (ValueError, IndexError):
            continue
    
    return dict(daily)

def get_weekday_activity(logs=None):
    """
    Aktivität nach Wochentag
    
    Returns:
        dict: {weekday: count} (0=Montag, 6=Sonntag)
    """
    if logs is None:
        logs = get_parsed_logs()
    
    weekday = Counter()
    
    for log in logs:
        try:
            # Parse timestamp to get weekday
            # Format: "14 OCT 1230"
            parts = log["timestamp"].split()
            day = int(parts[0])
            month_str = parts[1]
            
            # Simple month mapping
            months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                     "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
            month = months.get(month_str, 10)
            
            # Assume current year
            year = datetime.now().year
            date = datetime(year, month, day)
            weekday[date.weekday()] += 1
        except (ValueError, IndexError, KeyError):
            continue
    
    return {i: weekday.get(i, 0) for i in range(7)}

# ========================= WATCHLIST =========================

def load_watchlist():
    """Lädt Watchlist"""
    if WATCHLIST_PATH.exists():
        return json.loads(WATCHLIST_PATH.read_text())
    return []

def save_watchlist(watchlist):
    """Speichert Watchlist"""
    WATCHLIST_PATH.write_text(json.dumps(watchlist, indent=2))

def is_on_watchlist(mac):
    """Prüft ob MAC auf Watchlist"""
    watchlist = load_watchlist()
    return mac in watchlist

# ========================= VALIDATION =========================

def is_valid_mac(mac: str) -> bool:
    """Validiert MAC-Adresse Format"""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def format_mac(mac: str) -> str:
    """Formatiert MAC-Adresse einheitlich"""
    mac = mac.upper().replace("-", ":").replace(".", ":")
    
    if is_valid_mac(mac):
        return mac
    
    return mac

# ========================= FILTERS =========================

def filter_logs_by_time(logs, hours=24):
    """
    Filtert Logs nach Zeitraum
    
    Args:
        logs: Liste von Log-Einträgen
        hours: Anzahl Stunden rückwärts
    
    Returns:
        List[dict]: Gefilterte Logs
    """
    cutoff = datetime.now() - timedelta(hours=hours)
    
    filtered = []
    for log in logs:
        try:
            # Parse timestamp
            parts = log["timestamp"].split()
            day = int(parts[0])
            month_str = parts[1]
            time_str = parts[2]
            
            months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                     "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
            month = months.get(month_str, 10)
            
            hour = int(time_str[:2])
            minute = int(time_str[2:4])
            
            year = datetime.now().year
            log_time = datetime(year, month, day, hour, minute)
            
            if log_time >= cutoff:
                filtered.append(log)
        except (ValueError, IndexError, KeyError):
            continue
    
    return filtered

def filter_logs_by_mac(logs, mac):
    """Filtert Logs nach MAC-Adresse"""
    return [log for log in logs if log["mac"] == mac]

def search_logs(logs, query):
    """
    Sucht in Logs
    
    Args:
        logs: Liste von Log-Einträgen
        query: Suchbegriff
    
    Returns:
        List[dict]: Gefundene Logs
    """
    query = query.lower()
    results = []
    
    for log in logs:
        if (query in log["mac"].lower() or 
            query in log["name"].lower()):
            results.append(log)
    
    return results

# ========================= EXPORT =========================

def prepare_export_data(logs):
    """
    Bereitet Daten für Export vor
    
    Returns:
        List[dict]: Export-Ready Daten
    """
    export = []
    
    for log in logs:
        entry = {
            "timestamp": log["timestamp"],
            "mac": log["mac"],
            "name": log["name"]
        }
        
        if log.get("lat") and log.get("lon"):
            entry["latitude"] = log["lat"]
            entry["longitude"] = log["lon"]
        
        export.append(entry)
    
    return export

# ========================= GPS HELPERS =========================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Berechnet Distanz zwischen zwei GPS-Punkten (km)
    
    Uses Haversine formula
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def get_gps_data(logs=None):
    """
    Extrahiert GPS-Daten aus Logs
    
    Returns:
        List[dict]: GPS-Punkte mit {mac, name, lat, lon, timestamp}
    """
    if logs is None:
        logs = get_parsed_logs()
    
    gps_data = []
    
    for log in logs:
        if log.get("lat") and log.get("lon"):
            gps_data.append({
                "mac": log["mac"],
                "name": log["name"],
                "lat": log["lat"],
                "lon": log["lon"],
                "timestamp": log["timestamp"]
            })
    
    return gps_data
