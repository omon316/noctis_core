"""
Statistics API
==============

Backend für Statistik-Modul
Migriert von noctis_stats.py (Streamlit → Flask)
"""

from datetime import datetime, timedelta
from collections import Counter
from api.utils import (
    get_parsed_logs,
    get_device_count,
    get_top_devices,
    get_mac_statistics,
    get_hourly_activity,
    get_daily_activity,
    get_weekday_activity,
    filter_logs_by_time
)

# ========================= OVERVIEW STATS =========================

def get_overview_stats():
    """
    Übersichts-Metriken für Dashboard
    
    Returns:
        dict: {
            "total_scans": int,
            "unique_devices": int,
            "last_24h": int,
            "last_hour": int
        }
    """
    logs = get_parsed_logs()
    logs_24h = filter_logs_by_time(logs, hours=24)
    logs_1h = filter_logs_by_time(logs, hours=1)
    
    return {
        "total_scans": len(logs),
        "unique_devices": get_device_count(logs),
        "last_24h": len(logs_24h),
        "last_hour": len(logs_1h)
    }

# ========================= TOP DEVICES =========================

def get_top_devices_data(n=10, time_filter=None):
    """
    Top-N Geräte nach Anzahl
    
    Args:
        n: Anzahl der Top-Geräte
        time_filter: None, "24h", "7d", "30d"
    
    Returns:
        dict: {
            "devices": [
                {"rank": 1, "mac": "...", "name": "...", "count": 42},
                ...
            ],
            "total": int
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
    
    top = get_top_devices(n, logs)
    
    devices = []
    for rank, (mac, name, count) in enumerate(top, 1):
        devices.append({
            "rank": rank,
            "mac": mac,
            "name": name,
            "count": count
        })
    
    return {
        "devices": devices,
        "total": len(logs)
    }

# ========================= DETAILED STATS =========================

def get_detailed_device_stats(time_filter=None):
    """
    Detaillierte Statistiken pro Gerät
    
    Returns:
        dict: {
            "devices": [
                {
                    "mac": "...",
                    "name": "...",
                    "count": int,
                    "first_seen": "...",
                    "last_seen": "...",
                    "positions": int
                },
                ...
            ]
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
    
    stats = get_mac_statistics(logs)
    
    devices = []
    for mac, data in stats.items():
        devices.append({
            "mac": mac,
            "name": data["name"],
            "count": data["count"],
            "first_seen": data["first"],
            "last_seen": data["last"],
            "positions": len(data["positions"])
        })
    
    # Sortiere nach Count
    devices.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "devices": devices[:20]  # Top 20
    }

# ========================= TIME ANALYSIS =========================

def get_hourly_stats(time_filter=None):
    """
    Stündliche Aktivität
    
    Returns:
        dict: {
            "hours": [0, 1, 2, ..., 23],
            "counts": [12, 5, 3, ..., 15],
            "peak_hour": int,
            "quiet_hour": int
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
    
    hourly = get_hourly_activity(logs)
    
    hours = list(range(24))
    counts = [hourly[h] for h in hours]
    
    peak_hour = max(hourly, key=hourly.get) if hourly else 0
    quiet_hour = min(hourly, key=hourly.get) if hourly else 0
    
    return {
        "hours": hours,
        "counts": counts,
        "peak_hour": peak_hour,
        "quiet_hour": quiet_hour,
        "average": sum(counts) / 24 if counts else 0
    }

def get_daily_stats(days=30, time_filter=None):
    """
    Tägliche Aktivität
    
    Returns:
        dict: {
            "dates": ["14", "15", ...],
            "counts": [42, 38, ...],
            "average": float,
            "max_day": str
        }
    """
    logs = get_parsed_logs()
    
    # Filter anwenden
    if time_filter == "7d":
        logs = filter_logs_by_time(logs, hours=24*7)
        days = 7
    elif time_filter == "30d":
        logs = filter_logs_by_time(logs, hours=24*30)
        days = 30
    
    daily = get_daily_activity(logs, days)
    
    # Sortiere nach Datum
    sorted_days = sorted(daily.items())
    
    dates = [day for day, _ in sorted_days]
    counts = [count for _, count in sorted_days]
    
    max_day = max(daily, key=daily.get) if daily else None
    
    return {
        "dates": dates,
        "counts": counts,
        "average": sum(counts) / len(counts) if counts else 0,
        "max_day": max_day,
        "total": sum(counts)
    }

def get_weekday_stats(time_filter=None):
    """
    Wochentags-Aktivität
    
    Returns:
        dict: {
            "weekdays": ["Mon", "Tue", ...],
            "counts": [42, 38, ...],
            "most_active": str,
            "least_active": str
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
    
    weekday_data = get_weekday_activity(logs)
    
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = [weekday_data[i] for i in range(7)]
    
    most_active_idx = max(range(7), key=lambda i: weekday_data[i])
    least_active_idx = min(range(7), key=lambda i: weekday_data[i])
    
    return {
        "weekdays": weekday_names,
        "counts": counts,
        "most_active": weekday_names[most_active_idx],
        "least_active": weekday_names[least_active_idx],
        "weekday_total": sum(counts[:5]),
        "weekend_total": sum(counts[5:])
    }

# ========================= HEATMAP =========================

def get_activity_heatmap(time_filter=None):
    """
    Aktivitäts-Heatmap (Stunde × Wochentag)
    
    Returns:
        dict: {
            "matrix": [[h0_mon, h0_tue, ...], [h1_mon, h1_tue, ...], ...],
            "hours": [0, 1, ..., 23],
            "weekdays": ["Mon", "Tue", ...]
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
    
    # Zähle pro Stunde und Wochentag
    heatmap_data = {}
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
            
            year = datetime.now().year
            date = datetime(year, month, day)
            weekday = date.weekday()
            
            key = (hour, weekday)
            heatmap_data[key] = heatmap_data.get(key, 0) + 1
            
        except (ValueError, IndexError, KeyError):
            continue
    
    # Erstelle Matrix
    matrix = []
    for hour in range(24):
        row = [heatmap_data.get((hour, wd), 0) for wd in range(7)]
        matrix.append(row)
    
    return {
        "matrix": matrix,
        "hours": list(range(24)),
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    }

# ========================= ADVANCED STATS =========================

def get_advanced_stats(time_filter=None):
    """
    Erweiterte Statistiken
    
    Returns:
        dict: {
            "timespan_days": float,
            "avg_scans_per_device": float,
            "median_scans": int,
            "growth_rate_24h": float
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
            "timespan_days": 0,
            "avg_scans_per_device": 0,
            "median_scans": 0,
            "growth_rate_24h": 0
        }
    
    # Zeitspanne berechnen
    try:
        first_timestamp = logs[0]["timestamp"]
        last_timestamp = logs[-1]["timestamp"]
        
        # Simplified - assume same year
        parts_first = first_timestamp.split()
        parts_last = last_timestamp.split()
        
        day_first = int(parts_first[0])
        day_last = int(parts_last[0])
        
        timespan_days = max(1, day_last - day_first)
    except:
        timespan_days = 1
    
    # Scans pro Gerät
    stats = get_mac_statistics(logs)
    counts = [data["count"] for data in stats.values()]
    
    avg_scans = sum(counts) / len(counts) if counts else 0
    
    # Median
    sorted_counts = sorted(counts)
    median_idx = len(sorted_counts) // 2
    median_scans = sorted_counts[median_idx] if sorted_counts else 0
    
    # Wachstumsrate (letzten 24h vs. davor)
    logs_24h = filter_logs_by_time(get_parsed_logs(), hours=24)
    logs_48h = filter_logs_by_time(get_parsed_logs(), hours=48)
    logs_24_48h = [l for l in logs_48h if l not in logs_24h]
    
    count_now = len(logs_24h)
    count_before = len(logs_24_48h)
    
    if count_before > 0:
        growth_rate = ((count_now - count_before) / count_before) * 100
    else:
        growth_rate = 0
    
    return {
        "timespan_days": timespan_days,
        "avg_scans_per_device": round(avg_scans, 2),
        "median_scans": median_scans,
        "growth_rate_24h": round(growth_rate, 2)
    }

# ========================= COMBINED STATS =========================

def get_all_stats(time_filter=None):
    """
    Alle Statistiken auf einmal
    
    Returns:
        dict: Kombinierte Stats
    """
    return {
        "overview": get_overview_stats(),
        "top_devices": get_top_devices_data(10, time_filter),
        "detailed": get_detailed_device_stats(time_filter),
        "hourly": get_hourly_stats(time_filter),
        "daily": get_daily_stats(30, time_filter),
        "weekday": get_weekday_stats(time_filter),
        "heatmap": get_activity_heatmap(time_filter),
        "advanced": get_advanced_stats(time_filter)
    }
