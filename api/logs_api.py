"""
Logs API
========

Backend für Log-Viewer-Modul
Migriert von noctis_log.py (Streamlit → Flask)
"""

from api.utils import (
    get_parsed_logs,
    filter_logs_by_time,
    filter_logs_by_mac,
    search_logs,
    prepare_export_data
)

# ========================= LOG DATA =========================

def get_logs_data(limit=100, time_filter=None):
    """
    Log-Daten mit optionalem Filter
    
    Args:
        limit: Anzahl Einträge
        time_filter: None, "24h", "7d", "30d"
    
    Returns:
        dict: {
            "logs": [...],
            "total": int,
            "filtered": int
        }
    """
    logs = get_parsed_logs()
    total = len(logs)
    
    # Filter anwenden
    if time_filter == "24h":
        logs = filter_logs_by_time(logs, hours=24)
    elif time_filter == "7d":
        logs = filter_logs_by_time(logs, hours=24*7)
    elif time_filter == "30d":
        logs = filter_logs_by_time(logs, hours=24*30)
    
    # Limit anwenden
    if limit:
        logs = logs[-limit:]
    
    return {
        "logs": logs,
        "total": total,
        "filtered": len(logs)
    }

# ========================= RECENT LOGS =========================

def get_recent_logs(n=50):
    """
    Letzte N Log-Einträge
    
    Returns:
        dict: {
            "logs": [...],
            "count": int
        }
    """
    logs = get_parsed_logs()
    recent = logs[-n:] if len(logs) > n else logs
    
    # Reverse für neueste zuerst
    recent.reverse()
    
    return {
        "logs": recent,
        "count": len(recent)
    }

# ========================= SEARCH =========================

def search_logs_api(query):
    """
    Suche in Logs
    
    Args:
        query: Suchbegriff
    
    Returns:
        dict: {
            "results": [...],
            "count": int,
            "query": str
        }
    """
    logs = get_parsed_logs()
    results = search_logs(logs, query)
    
    return {
        "results": results,
        "count": len(results),
        "query": query
    }

# ========================= STATISTICS =========================

def get_log_statistics(time_filter=None):
    """
    Log-Statistiken
    
    Returns:
        dict: {
            "total_entries": int,
            "unique_devices": int,
            "date_range": {
                "first": str,
                "last": str
            }
        }
    """
    logs = get_parsed_logs()
    
    # Filter anwenden
    if time_filter == "24h":
        logs = filter_logs_by_time(logs, hours=24)
    elif time_filter == "7d":
        logs = filter_logs_by_time(logs, hours=24*7)
    elif time_filter == "30d":
        logs = filter_logs_by_time(logs, hours=24*30)
    
    if not logs:
        return {
            "total_entries": 0,
            "unique_devices": 0,
            "date_range": None
        }
    
    unique_macs = set(log["mac"] for log in logs)
    
    return {
        "total_entries": len(logs),
        "unique_devices": len(unique_macs),
        "date_range": {
            "first": logs[0]["timestamp"],
            "last": logs[-1]["timestamp"]
        }
    }

# ========================= DEVICE LOGS =========================

def get_device_logs(mac, limit=None):
    """
    Logs für ein spezifisches Gerät
    
    Args:
        mac: MAC-Adresse
        limit: Optional limit
    
    Returns:
        dict: {
            "mac": str,
            "logs": [...],
            "count": int
        }
    """
    logs = get_parsed_logs()
    device_logs = filter_logs_by_mac(logs, mac)
    
    if limit:
        device_logs = device_logs[-limit:]
    
    return {
        "mac": mac,
        "logs": device_logs,
        "count": len(device_logs)
    }

# ========================= EXPORT =========================

def export_logs(format_type='json', time_filter=None):
    """
    Export Logs in verschiedenen Formaten
    
    Args:
        format_type: "json" oder "csv"
        time_filter: None, "24h", "7d", "30d"
    
    Returns:
        dict: Export-Daten
    """
    logs = get_parsed_logs()
    
    # Filter anwenden
    if time_filter == "24h":
        logs = filter_logs_by_time(logs, hours=24)
    elif time_filter == "7d":
        logs = filter_logs_by_time(logs, hours=24*7)
    elif time_filter == "30d":
        logs = filter_logs_by_time(logs, hours=24*30)
    
    export_data = prepare_export_data(logs)
    
    if format_type == 'csv':
        # CSV-Format
        csv_lines = ["timestamp,mac,name,latitude,longitude"]
        for entry in export_data:
            lat = entry.get("latitude", "")
            lon = entry.get("longitude", "")
            csv_lines.append(f"{entry['timestamp']},{entry['mac']},{entry['name']},{lat},{lon}")
        
        return {
            "format": "csv",
            "data": "\n".join(csv_lines),
            "count": len(export_data)
        }
    
    # JSON-Format (default)
    return {
        "format": "json",
        "data": export_data,
        "count": len(export_data)
    }

# ========================= LOG FILTERS =========================

def get_available_filters():
    """
    Verfügbare Filter-Optionen
    
    Returns:
        dict: {
            "time_filters": [...],
            "device_names": [...],
            "macs": [...]
        }
    """
    logs = get_parsed_logs()
    
    # Sammle eindeutige Werte
    device_names = set()
    macs = set()
    
    for log in logs:
        if log["name"] != "Unknown":
            device_names.add(log["name"])
        macs.add(log["mac"])
    
    return {
        "time_filters": [
            {"value": None, "label": "Alle"},
            {"value": "24h", "label": "Letzte 24h"},
            {"value": "7d", "label": "Letzte 7 Tage"},
            {"value": "30d", "label": "Letzte 30 Tage"}
        ],
        "device_names": sorted(list(device_names)),
        "macs": sorted(list(macs))
    }

# ========================= COMBINED LOGS DATA =========================

def get_all_logs_data(limit=100, time_filter=None):
    """
    Alle Log-Daten auf einmal
    
    Returns:
        dict: Kombinierte Log-Daten
    """
    return {
        "data": get_logs_data(limit, time_filter),
        "statistics": get_log_statistics(time_filter),
        "filters": get_available_filters()
    }
