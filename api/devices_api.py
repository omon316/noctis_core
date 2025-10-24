"""
Devices API
===========

Central device catalog and detail views.
Device = Central entity (MAC address + metadata)
"""

from collections import defaultdict
from datetime import datetime, timedelta
from api.utils import (
    get_parsed_logs,
    filter_logs_by_time,
    filter_logs_by_mac,
    get_mac_statistics,
    is_valid_mac,
    format_mac
)
import json
from pathlib import Path

# Device Tags Storage
BASE_DIR = Path(__file__).parent.parent
TAGS_PATH = BASE_DIR / "device_tags.json"

# ========================= DEVICE DIRECTORY =========================

def get_device_directory(
    page=1,
    limit=50,
    time_filter=None,
    manufacturer=None,
    device_type=None,
    status=None,
    search_query=None,
    sort_by="last_seen",
    sort_order="desc"
):
    """
    Paginated device directory with filters
    
    Args:
        page: Page number (1-based)
        limit: Items per page (max 100)
        time_filter: None, "24h", "7d", "30d"
        manufacturer: Filter by OUI/manufacturer
        device_type: "smartphone", "headset", "wearable", "unknown"
        status: "online", "offline"
        search_query: Search in MAC/Name
        sort_by: "last_seen", "first_seen", "count", "name"
        sort_order: "asc", "desc"
    
    Returns:
        dict: {
            "devices": [...],
            "pagination": {...},
            "filters_applied": {...}
        }
    """
    logs = get_parsed_logs()
    
    # Apply time filter
    if time_filter == "24h":
        logs = filter_logs_by_time(logs, hours=24)
    elif time_filter == "7d":
        logs = filter_logs_by_time(logs, hours=24*7)
    elif time_filter == "30d":
        logs = filter_logs_by_time(logs, hours=24*30)
    
    # Get device statistics
    stats = get_mac_statistics(logs)
    
    # Load tags
    tags_db = load_tags()
    
    # Build device list
    devices = []
    for mac, data in stats.items():
        # Apply filters
        if search_query:
            if search_query.lower() not in mac.lower() and \
               search_query.lower() not in data["name"].lower():
                continue
        
        # Manufacturer filter
        if manufacturer:
            device_manufacturer = lookup_oui(mac)
            if manufacturer.lower() not in device_manufacturer.lower():
                continue
        
        # Device type filter (heuristic)
        if device_type:
            detected_type = detect_device_type(data["name"], mac)
            if device_type != detected_type:
                continue
        
        # Status filter
        if status:
            device_status = get_device_status(data["last"])
            if status != device_status:
                continue
        
        # Build device object
        device = {
            "mac": mac,
            "name": data["name"],
            "manufacturer": lookup_oui(mac),
            "type": detect_device_type(data["name"], mac),
            "count": data["count"],
            "first_seen": data["first"],
            "last_seen": data["last"],
            "status": get_device_status(data["last"]),
            "positions": len(data["positions"]),
            "tags": tags_db.get(mac, []),
            "has_gps": len(data["positions"]) > 0
        }
        
        devices.append(device)
    
    # Sort
    devices = sort_devices(devices, sort_by, sort_order)
    
    # Pagination
    total = len(devices)
    start = (page - 1) * limit
    end = start + limit
    paginated = devices[start:end]
    
    return {
        "devices": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
            "has_next": end < total,
            "has_prev": page > 1
        },
        "filters_applied": {
            "time_filter": time_filter,
            "manufacturer": manufacturer,
            "device_type": device_type,
            "status": status,
            "search_query": search_query
        },
        "stats": {
            "total_devices": total,
            "online": len([d for d in devices if d["status"] == "online"]),
            "with_gps": len([d for d in devices if d["has_gps"]])
        }
    }

# ========================= DEVICE DETAILS =========================

def get_device_details(mac):
    """
    Detailed view of a single device
    
    Args:
        mac: MAC address
    
    Returns:
        dict: Complete device info with history
    """
    # Validate MAC
    if not is_valid_mac(mac):
        return {"error": "Invalid MAC address"}
    
    mac = format_mac(mac)
    
    logs = get_parsed_logs()
    device_logs = filter_logs_by_mac(logs, mac)
    
    if not device_logs:
        return {"error": "Device not found"}
    
    # Load tags
    tags_db = load_tags()
    
    # Build statistics
    positions = []
    rssi_values = []
    
    for log in device_logs:
        if log.get("lat") and log.get("lon"):
            positions.append({
                "lat": log["lat"],
                "lon": log["lon"],
                "timestamp": log["timestamp"]
            })
        
        # Try to extract RSSI (if available in raw)
        raw = log.get("raw", "")
        if "RSSI" in raw or "rssi" in raw:
            try:
                import re
                match = re.search(r'-?\d+', raw)
                if match:
                    rssi = int(match.group())
                    if -120 <= rssi <= 0:
                        rssi_values.append({
                            "value": rssi,
                            "timestamp": log["timestamp"]
                        })
            except:
                pass
    
    # Calculate session info
    sessions = detect_sessions(device_logs)
    
    return {
        "mac": mac,
        "name": device_logs[0]["name"],
        "manufacturer": lookup_oui(mac),
        "type": detect_device_type(device_logs[0]["name"], mac),
        "tags": tags_db.get(mac, []),
        "statistics": {
            "total_scans": len(device_logs),
            "first_seen": device_logs[0]["timestamp"],
            "last_seen": device_logs[-1]["timestamp"],
            "positions_count": len(positions),
            "rssi_samples": len(rssi_values),
            "sessions": len(sessions),
            "status": get_device_status(device_logs[-1]["timestamp"])
        },
        "positions": positions[-50:] if len(positions) > 50 else positions,  # Last 50
        "rssi_timeline": rssi_values[-100:] if len(rssi_values) > 100 else rssi_values,  # Last 100
        "sessions": sessions[-10:] if len(sessions) > 10 else sessions,  # Last 10
        "recent_logs": device_logs[-20:] if len(device_logs) > 20 else device_logs  # Last 20
    }

# ========================= DEVICE TIMELINE =========================

def get_device_timeline(mac, timerange="24h"):
    """
    Timeline view for a device (RSSI, positions over time)
    
    Args:
        mac: MAC address
        timerange: "1h", "24h", "7d", "30d"
    
    Returns:
        dict: Timeline data for charts
    """
    if not is_valid_mac(mac):
        return {"error": "Invalid MAC address"}
    
    mac = format_mac(mac)
    
    logs = get_parsed_logs()
    device_logs = filter_logs_by_mac(logs, mac)
    
    # Apply time filter
    if timerange == "1h":
        device_logs = filter_logs_by_time(device_logs, hours=1)
    elif timerange == "24h":
        device_logs = filter_logs_by_time(device_logs, hours=24)
    elif timerange == "7d":
        device_logs = filter_logs_by_time(device_logs, hours=24*7)
    elif timerange == "30d":
        device_logs = filter_logs_by_time(device_logs, hours=24*30)
    
    if not device_logs:
        return {
            "mac": mac,
            "timerange": timerange,
            "timeline": [],
            "summary": {
                "scans": 0,
                "avg_rssi": None,
                "positions": 0
            }
        }
    
    # Build timeline
    timeline = []
    rssi_sum = 0
    rssi_count = 0
    positions_count = 0
    
    for log in device_logs:
        point = {
            "timestamp": log["timestamp"],
            "name": log["name"]
        }
        
        # GPS
        if log.get("lat") and log.get("lon"):
            point["lat"] = log["lat"]
            point["lon"] = log["lon"]
            positions_count += 1
        
        # RSSI
        raw = log.get("raw", "")
        if "RSSI" in raw or "rssi" in raw:
            try:
                import re
                match = re.search(r'-?\d+', raw)
                if match:
                    rssi = int(match.group())
                    if -120 <= rssi <= 0:
                        point["rssi"] = rssi
                        rssi_sum += rssi
                        rssi_count += 1
            except:
                pass
        
        timeline.append(point)
    
    return {
        "mac": mac,
        "timerange": timerange,
        "timeline": timeline,
        "summary": {
            "scans": len(device_logs),
            "avg_rssi": round(rssi_sum / rssi_count, 1) if rssi_count > 0 else None,
            "positions": positions_count
        }
    }

# ========================= DEVICE SEARCH =========================

def search_devices(query, limit=20):
    """
    Search devices by MAC, name, or manufacturer
    
    Args:
        query: Search string
        limit: Max results
    
    Returns:
        dict: Search results
    """
    logs = get_parsed_logs()
    stats = get_mac_statistics(logs)
    tags_db = load_tags()
    
    query_lower = query.lower()
    results = []
    
    for mac, data in stats.items():
        # Search in MAC
        if query_lower in mac.lower():
            match_field = "mac"
        # Search in name
        elif query_lower in data["name"].lower():
            match_field = "name"
        # Search in manufacturer
        elif query_lower in lookup_oui(mac).lower():
            match_field = "manufacturer"
        # Search in tags
        elif any(query_lower in tag.lower() for tag in tags_db.get(mac, [])):
            match_field = "tags"
        else:
            continue
        
        results.append({
            "mac": mac,
            "name": data["name"],
            "manufacturer": lookup_oui(mac),
            "count": data["count"],
            "last_seen": data["last"],
            "match_field": match_field,
            "tags": tags_db.get(mac, [])
        })
    
    # Sort by last_seen
    results.sort(key=lambda x: x["last_seen"], reverse=True)
    
    return {
        "query": query,
        "results": results[:limit],
        "total": len(results)
    }

# ========================= DEVICE TAGGING =========================

def tag_device(mac, tags):
    """
    Add tags to a device
    
    Args:
        mac: MAC address
        tags: List of tag strings
    
    Returns:
        dict: Success status
    """
    if not is_valid_mac(mac):
        return {"success": False, "error": "Invalid MAC address"}
    
    mac = format_mac(mac)
    
    # Validate tags
    if not isinstance(tags, list):
        return {"success": False, "error": "Tags must be a list"}
    
    # Load existing tags
    tags_db = load_tags()
    
    # Update tags
    tags_db[mac] = tags
    
    # Save
    save_tags(tags_db)
    
    return {
        "success": True,
        "mac": mac,
        "tags": tags
    }

def get_device_tags(mac):
    """Get tags for a device"""
    if not is_valid_mac(mac):
        return {"error": "Invalid MAC address"}
    
    mac = format_mac(mac)
    tags_db = load_tags()
    
    return {
        "mac": mac,
        "tags": tags_db.get(mac, [])
    }

def remove_device_tags(mac):
    """Remove all tags from a device"""
    if not is_valid_mac(mac):
        return {"success": False, "error": "Invalid MAC address"}
    
    mac = format_mac(mac)
    tags_db = load_tags()
    
    if mac in tags_db:
        del tags_db[mac]
        save_tags(tags_db)
    
    return {
        "success": True,
        "mac": mac
    }

# ========================= DEVICE EXPORT =========================

def export_devices(format_type="json", time_filter=None, filters=None):
    """
    Export device directory
    
    Args:
        format_type: "json" or "csv"
        time_filter: None, "24h", "7d", "30d"
        filters: Additional filters dict
    
    Returns:
        dict: Export data
    """
    # Get directory (all devices, no pagination)
    directory = get_device_directory(
        page=1,
        limit=10000,  # Large limit
        time_filter=time_filter,
        manufacturer=filters.get("manufacturer") if filters else None,
        device_type=filters.get("device_type") if filters else None,
        status=filters.get("status") if filters else None
    )
    
    devices = directory["devices"]
    
    if format_type == "csv":
        # CSV format
        csv_lines = ["mac,name,manufacturer,type,count,first_seen,last_seen,status,positions,tags"]
        for device in devices:
            tags_str = "|".join(device["tags"]) if device["tags"] else ""
            csv_lines.append(
                f"{device['mac']},{device['name']},{device['manufacturer']},"
                f"{device['type']},{device['count']},{device['first_seen']},"
                f"{device['last_seen']},{device['status']},{device['positions']},{tags_str}"
            )
        
        return {
            "format": "csv",
            "data": "\n".join(csv_lines),
            "count": len(devices)
        }
    
    # JSON format (default)
    return {
        "format": "json",
        "data": devices,
        "count": len(devices),
        "exported_at": datetime.now().isoformat()
    }

# ========================= HELPER FUNCTIONS =========================

def lookup_oui(mac):
    """Lookup manufacturer from MAC (OUI)"""
    oui = mac[:8].upper()
    
    # Simple OUI database (can be extended)
    oui_db = {
        "00:03:93": "Apple", "00:05:02": "Apple", "00:0A:27": "Apple",
        "0C:47:C9": "Samsung", "10:08:B1": "Samsung", "14:49:E0": "Samsung",
        "00:0C:F1": "Intel", "00:13:E0": "Intel", "00:15:00": "Intel",
        "00:50:F2": "Microsoft", "08:00:27": "VirtualBox",
        "00:1B:63": "Apple", "00:25:00": "Apple", "3C:BD:D8": "Samsung"
    }
    
    return oui_db.get(oui, "Unknown")

def detect_device_type(name, mac):
    """Heuristic device type detection"""
    name_lower = name.lower()
    
    # Smartphone indicators
    if any(x in name_lower for x in ["iphone", "galaxy", "pixel", "oneplus", "xiaomi", "huawei"]):
        return "smartphone"
    
    # Headset indicators
    if any(x in name_lower for x in ["airpods", "buds", "headset", "earbuds", "headphone"]):
        return "headset"
    
    # Wearable indicators
    if any(x in name_lower for x in ["watch", "band", "fit", "tracker"]):
        return "wearable"
    
    # Laptop indicators
    if any(x in name_lower for x in ["macbook", "laptop", "thinkpad"]):
        return "laptop"
    
    # IoT indicators
    if any(x in name_lower for x in ["sensor", "beacon", "tag", "tracker"]):
        return "iot"
    
    return "unknown"

def get_device_status(last_seen_timestamp):
    """Determine if device is online/offline"""
    try:
        # Parse timestamp (format: "14 OCT 1230")
        parts = last_seen_timestamp.split()
        day = int(parts[0])
        month_str = parts[1]
        time_str = parts[2]
        
        months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                 "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
        month = months.get(month_str, 10)
        
        hour = int(time_str[:2])
        minute = int(time_str[2:4])
        
        year = datetime.now().year
        last_seen = datetime(year, month, day, hour, minute)
        
        # Online if seen within last hour
        now = datetime.now()
        diff = (now - last_seen).total_seconds()
        
        if diff < 3600:  # 1 hour
            return "online"
        else:
            return "offline"
    except:
        return "unknown"

def detect_sessions(logs):
    """
    Detect device presence sessions
    (Group scans with < 30min gap)
    """
    if not logs:
        return []
    
    sessions = []
    current_session = {
        "start": logs[0]["timestamp"],
        "end": logs[0]["timestamp"],
        "scans": 1
    }
    
    for i in range(1, len(logs)):
        # Simple heuristic: if same day/hour, continue session
        # Otherwise start new session
        prev_parts = logs[i-1]["timestamp"].split()
        curr_parts = logs[i]["timestamp"].split()
        
        if prev_parts[:2] == curr_parts[:2]:  # Same day
            current_session["end"] = logs[i]["timestamp"]
            current_session["scans"] += 1
        else:
            sessions.append(current_session)
            current_session = {
                "start": logs[i]["timestamp"],
                "end": logs[i]["timestamp"],
                "scans": 1
            }
    
    # Add last session
    sessions.append(current_session)
    
    return sessions

def sort_devices(devices, sort_by, sort_order):
    """Sort device list"""
    reverse = (sort_order == "desc")
    
    if sort_by == "last_seen":
        devices.sort(key=lambda d: d["last_seen"], reverse=reverse)
    elif sort_by == "first_seen":
        devices.sort(key=lambda d: d["first_seen"], reverse=reverse)
    elif sort_by == "count":
        devices.sort(key=lambda d: d["count"], reverse=reverse)
    elif sort_by == "name":
        devices.sort(key=lambda d: d["name"].lower(), reverse=reverse)
    
    return devices

# ========================= TAGS STORAGE =========================

def load_tags():
    """Load tags from JSON file"""
    if TAGS_PATH.exists():
        try:
            return json.loads(TAGS_PATH.read_text())
        except:
            return {}
    return {}

def save_tags(tags_db):
    """Save tags to JSON file"""
    TAGS_PATH.write_text(json.dumps(tags_db, indent=2))

# ========================= AGGREGATIONS =========================

def get_device_aggregations():
    """
    Get aggregated device statistics
    
    Returns:
        dict: Aggregated stats
    """
    logs = get_parsed_logs()
    stats = get_mac_statistics(logs)
    
    # Count by manufacturer
    manufacturer_counts = defaultdict(int)
    for mac in stats.keys():
        manufacturer = lookup_oui(mac)
        manufacturer_counts[manufacturer] += 1
    
    # Count by type
    type_counts = defaultdict(int)
    for mac, data in stats.items():
        device_type = detect_device_type(data["name"], mac)
        type_counts[device_type] += 1
    
    # Count by status
    status_counts = defaultdict(int)
    for data in stats.values():
        status = get_device_status(data["last"])
        status_counts[status] += 1
    
    return {
        "total_devices": len(stats),
        "by_manufacturer": dict(sorted(manufacturer_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "by_type": dict(type_counts),
        "by_status": dict(status_counts),
        "with_gps": len([d for d in stats.values() if len(d["positions"]) > 0]),
        "tagged": len(load_tags())
    }
