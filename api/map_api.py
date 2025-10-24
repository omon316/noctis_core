"""
Map API
=======

Backend für GPS-Karten-Modul
Migriert von noctis_map.py (Streamlit → Flask)
"""

from collections import defaultdict
from api.utils import (
    get_parsed_logs,
    get_gps_data,
    haversine_distance,
    filter_logs_by_mac
)

# ========================= GPS STATISTICS =========================

def get_gps_statistics():
    """
    GPS-Übersichts-Statistiken
    
    Returns:
        dict: {
            "total_points": int,
            "unique_devices": int,
            "avg_lat": float,
            "avg_lon": float,
            "has_data": bool
        }
    """
    gps_data = get_gps_data()
    
    if not gps_data:
        return {
            "total_points": 0,
            "unique_devices": 0,
            "avg_lat": 0,
            "avg_lon": 0,
            "has_data": False
        }
    
    unique_macs = set(point["mac"] for point in gps_data)
    
    avg_lat = sum(point["lat"] for point in gps_data) / len(gps_data)
    avg_lon = sum(point["lon"] for point in gps_data) / len(gps_data)
    
    return {
        "total_points": len(gps_data),
        "unique_devices": len(unique_macs),
        "avg_lat": round(avg_lat, 6),
        "avg_lon": round(avg_lon, 6),
        "has_data": True
    }

# ========================= MAP DATA =========================

def get_map_markers(device_filter="all"):
    """
    Marker-Daten für Karte
    
    Args:
        device_filter: "all", "named", "unknown"
    
    Returns:
        dict: {
            "markers": [
                {
                    "lat": float,
                    "lon": float,
                    "mac": str,
                    "name": str,
                    "timestamp": str,
                    "popup": str
                },
                ...
            ],
            "count": int,
            "bounds": {
                "min_lat": float,
                "max_lat": float,
                "min_lon": float,
                "max_lon": float
            }
        }
    """
    gps_data = get_gps_data()
    
    # Filter anwenden
    if device_filter == "named":
        gps_data = [p for p in gps_data if p["name"] != "Unknown"]
    elif device_filter == "unknown":
        gps_data = [p for p in gps_data if p["name"] == "Unknown"]
    
    if not gps_data:
        return {
            "markers": [],
            "count": 0,
            "bounds": None
        }
    
    # Erstelle Marker
    markers = []
    for point in gps_data:
        popup = f"<b>{point['name']}</b><br>" \
                f"MAC: {point['mac']}<br>" \
                f"Time: {point['timestamp']}<br>" \
                f"Pos: {point['lat']:.6f}, {point['lon']:.6f}"
        
        markers.append({
            "lat": point["lat"],
            "lon": point["lon"],
            "mac": point["mac"],
            "name": point["name"],
            "timestamp": point["timestamp"],
            "popup": popup
        })
    
    # Berechne Bounds
    lats = [m["lat"] for m in markers]
    lons = [m["lon"] for m in markers]
    
    bounds = {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons)
    }
    
    return {
        "markers": markers,
        "count": len(markers),
        "bounds": bounds
    }

# ========================= DEVICE POSITIONS =========================

def get_device_positions():
    """
    Positionen gruppiert nach Gerät
    
    Returns:
        dict: {
            "devices": [
                {
                    "mac": str,
                    "name": str,
                    "positions": int,
                    "first_pos": {"lat": float, "lon": float, "time": str},
                    "last_pos": {"lat": float, "lon": float, "time": str},
                    "movement_km": float
                },
                ...
            ]
        }
    """
    gps_data = get_gps_data()
    
    # Gruppiere nach MAC
    device_positions = defaultdict(list)
    for point in gps_data:
        device_positions[point["mac"]].append(point)
    
    devices = []
    for mac, positions in device_positions.items():
        # Sortiere nach Zeit
        positions.sort(key=lambda p: p["timestamp"])
        
        first = positions[0]
        last = positions[-1]
        
        # Berechne Bewegung
        movement = 0
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                dist = haversine_distance(
                    positions[i]["lat"], positions[i]["lon"],
                    positions[i+1]["lat"], positions[i+1]["lon"]
                )
                movement += dist
        
        devices.append({
            "mac": mac,
            "name": first["name"],
            "positions": len(positions),
            "first_pos": {
                "lat": first["lat"],
                "lon": first["lon"],
                "time": first["timestamp"]
            },
            "last_pos": {
                "lat": last["lat"],
                "lon": last["lon"],
                "time": last["timestamp"]
            },
            "movement_km": round(movement, 2)
        })
    
    # Sortiere nach Anzahl Positionen
    devices.sort(key=lambda d: d["positions"], reverse=True)
    
    return {
        "devices": devices
    }

# ========================= HEATMAP DATA =========================

def get_heatmap_data():
    """
    Daten für Heatmap (Dichte-Visualisierung)
    
    Returns:
        dict: {
            "points": [
                [lat, lon, intensity],
                ...
            ]
        }
    """
    gps_data = get_gps_data()
    
    if not gps_data:
        return {"points": []}
    
    # Zähle Punkte an gleichen Koordinaten (gerundet)
    point_counts = defaultdict(int)
    for point in gps_data:
        # Runde auf 4 Dezimalstellen (~11m Genauigkeit)
        lat_rounded = round(point["lat"], 4)
        lon_rounded = round(point["lon"], 4)
        point_counts[(lat_rounded, lon_rounded)] += 1
    
    # Erstelle Heatmap-Punkte
    points = []
    for (lat, lon), count in point_counts.items():
        points.append([lat, lon, count])
    
    return {
        "points": points
    }

# ========================= LOCATION ANALYSIS =========================

def get_location_hotspots(min_points=3):
    """
    Findet GPS-Hotspots (Bereiche mit vielen Geräten)
    
    Args:
        min_points: Minimum Punkte für Hotspot
    
    Returns:
        dict: {
            "hotspots": [
                {
                    "lat": float,
                    "lon": float,
                    "device_count": int,
                    "total_points": int
                },
                ...
            ]
        }
    """
    gps_data = get_gps_data()
    
    if not gps_data:
        return {"hotspots": []}
    
    # Gruppiere Punkte in 100m Radius
    clusters = []
    used_points = set()
    
    for i, point in enumerate(gps_data):
        if i in used_points:
            continue
        
        cluster = [point]
        used_points.add(i)
        
        # Finde nahegelegene Punkte
        for j, other in enumerate(gps_data):
            if j in used_points or i == j:
                continue
            
            dist = haversine_distance(
                point["lat"], point["lon"],
                other["lat"], other["lon"]
            )
            
            if dist <= 0.1:  # 100m
                cluster.append(other)
                used_points.add(j)
        
        if len(cluster) >= min_points:
            clusters.append(cluster)
    
    # Berechne Hotspot-Zentren
    hotspots = []
    for cluster in clusters:
        avg_lat = sum(p["lat"] for p in cluster) / len(cluster)
        avg_lon = sum(p["lon"] for p in cluster) / len(cluster)
        unique_devices = len(set(p["mac"] for p in cluster))
        
        hotspots.append({
            "lat": round(avg_lat, 6),
            "lon": round(avg_lon, 6),
            "device_count": unique_devices,
            "total_points": len(cluster)
        })
    
    # Sortiere nach Anzahl Geräte
    hotspots.sort(key=lambda h: h["device_count"], reverse=True)
    
    return {
        "hotspots": hotspots
    }

# ========================= MOVEMENT ANALYSIS =========================

def get_movement_analysis():
    """
    Bewegungsanalyse für Geräte
    
    Returns:
        dict: {
            "moving_devices": [
                {
                    "mac": str,
                    "name": str,
                    "total_distance_km": float,
                    "positions": int,
                    "avg_speed_kmh": float
                },
                ...
            ],
            "stationary_devices": [
                {
                    "mac": str,
                    "name": str,
                    "lat": float,
                    "lon": float,
                    "positions": int
                },
                ...
            ]
        }
    """
    gps_data = get_gps_data()
    
    if not gps_data:
        return {
            "moving_devices": [],
            "stationary_devices": []
        }
    
    # Gruppiere nach MAC
    device_positions = defaultdict(list)
    for point in gps_data:
        device_positions[point["mac"]].append(point)
    
    moving = []
    stationary = []
    
    for mac, positions in device_positions.items():
        if len(positions) < 2:
            # Nur 1 Position = stationär
            pos = positions[0]
            stationary.append({
                "mac": mac,
                "name": pos["name"],
                "lat": pos["lat"],
                "lon": pos["lon"],
                "positions": 1
            })
            continue
        
        # Sortiere nach Zeit
        positions.sort(key=lambda p: p["timestamp"])
        
        # Berechne Gesamtdistanz
        total_distance = 0
        for i in range(len(positions) - 1):
            dist = haversine_distance(
                positions[i]["lat"], positions[i]["lon"],
                positions[i+1]["lat"], positions[i+1]["lon"]
            )
            total_distance += dist
        
        # Bewegung > 100m = moving
        if total_distance > 0.1:
            moving.append({
                "mac": mac,
                "name": positions[0]["name"],
                "total_distance_km": round(total_distance, 2),
                "positions": len(positions),
                "avg_speed_kmh": 0  # Kann berechnet werden wenn Zeitstempel verfügbar
            })
        else:
            # Statisch (alle Positionen im gleichen Bereich)
            avg_lat = sum(p["lat"] for p in positions) / len(positions)
            avg_lon = sum(p["lon"] for p in positions) / len(positions)
            
            stationary.append({
                "mac": mac,
                "name": positions[0]["name"],
                "lat": round(avg_lat, 6),
                "lon": round(avg_lon, 6),
                "positions": len(positions)
            })
    
    # Sortiere
    moving.sort(key=lambda d: d["total_distance_km"], reverse=True)
    stationary.sort(key=lambda d: d["positions"], reverse=True)
    
    return {
        "moving_devices": moving,
        "stationary_devices": stationary
    }

# ========================= DEVICE TRACKING =========================

def get_device_track(mac):
    """
    Bewegungsspur für ein spezifisches Gerät
    
    Args:
        mac: MAC-Adresse
    
    Returns:
        dict: {
            "mac": str,
            "name": str,
            "track": [
                {"lat": float, "lon": float, "timestamp": str, "order": int},
                ...
            ],
            "total_distance_km": float
        }
    """
    logs = get_parsed_logs()
    device_logs = filter_logs_by_mac(logs, mac)
    
    track = []
    for log in device_logs:
        if log.get("lat") and log.get("lon"):
            track.append({
                "lat": log["lat"],
                "lon": log["lon"],
                "timestamp": log["timestamp"],
                "order": len(track)
            })
    
    if not track:
        return {
            "mac": mac,
            "name": "Unknown",
            "track": [],
            "total_distance_km": 0
        }
    
    # Berechne Gesamtdistanz
    total_distance = 0
    for i in range(len(track) - 1):
        dist = haversine_distance(
            track[i]["lat"], track[i]["lon"],
            track[i+1]["lat"], track[i+1]["lon"]
        )
        total_distance += dist
    
    return {
        "mac": mac,
        "name": device_logs[0]["name"] if device_logs else "Unknown",
        "track": track,
        "total_distance_km": round(total_distance, 2)
    }

# ========================= COMBINED MAP DATA =========================

def get_all_map_data(device_filter="all"):
    """
    Alle Karten-Daten auf einmal
    
    Returns:
        dict: Kombinierte Map-Daten
    """
    return {
        "statistics": get_gps_statistics(),
        "markers": get_map_markers(device_filter),
        "devices": get_device_positions(),
        "heatmap": get_heatmap_data(),
        "hotspots": get_location_hotspots(),
        "movement": get_movement_analysis()
    }
