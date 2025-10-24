"""
Bluetooth Scanner API
=====================

Verbindet das Flask-Backend mit dem Bluetooth-Scanner
"""

import threading
import time
from datetime import datetime
from pathlib import Path
import json

# Import deines existierenden Scanners
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    import bluetooth_scan
    SCANNER_AVAILABLE = True
except ImportError as e:
    SCANNER_AVAILABLE = False
    print(f"⚠️ Bluetooth-Scanner nicht verfügbar: {e}")

# Globaler State
bluetooth_state = {
    "running": False,
    "thread": None,
    "stop_event": None,
    "last_scan": None,
    "device_count": 0,
    "devices": [],
    "scan_interval": 900  # 15 Minuten
}

# ========================= SCANNER CONTROL =========================

def start_bluetooth_scan(interval=900):
    """Startet den Bluetooth-Scanner"""
    if not SCANNER_AVAILABLE:
        return {"success": False, "error": "Scanner not available"}
    
    if bluetooth_state["running"]:
        return {"success": False, "error": "Scanner already running"}
    
    # Stop-Event erstellen
    stop_event = threading.Event()
    bluetooth_state["stop_event"] = stop_event
    bluetooth_state["scan_interval"] = interval
    
    # Scanner-Thread starten
    thread = threading.Thread(
        target=_scan_loop,
        args=(stop_event, interval),
        daemon=True
    )
    thread.start()
    
    bluetooth_state["thread"] = thread
    bluetooth_state["running"] = True
    bluetooth_state["last_scan"] = datetime.now().isoformat()
    
    print("✅ Bluetooth-Scanner gestartet")
    return {"success": True, "interval": interval}

def stop_bluetooth_scan():
    """Stoppt den Bluetooth-Scanner"""
    if not bluetooth_state["running"]:
        return {"success": False, "error": "Scanner not running"}
    
    # Stop-Event setzen
    if bluetooth_state["stop_event"]:
        bluetooth_state["stop_event"].set()
    
    # Warten bis Thread stoppt (max 5 Sekunden)
    if bluetooth_state["thread"]:
        bluetooth_state["thread"].join(timeout=5)
    
    bluetooth_state["running"] = False
    bluetooth_state["thread"] = None
    bluetooth_state["stop_event"] = None
    
    print("⏹️ Bluetooth-Scanner gestoppt")
    return {"success": True}

def get_bluetooth_status():
    """Gibt den aktuellen Status zurück"""
    return {
        "running": bluetooth_state["running"],
        "last_scan": bluetooth_state["last_scan"],
        "device_count": bluetooth_state["device_count"],
        "devices": bluetooth_state["devices"][-50:],  # Letzte 50 Geräte
        "interval": bluetooth_state["scan_interval"]
    }

# ========================= SCAN LOOP =========================

def _scan_loop(stop_event, interval):
    """Haupt-Scan-Loop (läuft im Thread)"""
    print(f"🔄 Scan-Loop gestartet (Intervall: {interval}s)")
    
    while not stop_event.is_set():
        try:
            # Scan durchführen
            print("📡 Bluetooth-Scan wird durchgeführt...")
            devices = _perform_scan()
            
            # State aktualisieren
            bluetooth_state["last_scan"] = datetime.now().isoformat()
            bluetooth_state["device_count"] = len(devices)
            
            # Geräte hinzufügen (max 1000 behalten)
            bluetooth_state["devices"].extend(devices)
            if len(bluetooth_state["devices"]) > 1000:
                bluetooth_state["devices"] = bluetooth_state["devices"][-1000:]
            
            print(f"✅ Scan abgeschlossen: {len(devices)} Geräte gefunden")
            
        except Exception as e:
            print(f"❌ Scan-Fehler: {e}")
        
        # Warten (mit Stop-Check)
        stop_event.wait(timeout=interval)
    
    print("⏹️ Scan-Loop beendet")

def _perform_scan():
    """Führt einen einzelnen Scan durch"""
    if not SCANNER_AVAILABLE:
        # Demo-Daten
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "mac": "AA:BB:CC:DD:EE:FF",
                "name": "BT-Headset (Demo)",
                "rssi": -45,
                "scanner": "bluetooth"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "mac": "11:22:33:44:55:66",
                "name": "Smartwatch (Demo)",
                "rssi": -62,
                "scanner": "bluetooth"
            }
        ]
    
    # Echter Scan mit deinem bluetooth_scan.py
    try:
        # Rufe deine scan_and_store Funktion auf
        devices = bluetooth_scan.scan_and_store()
        
        # Konvertiere zu einheitlichem Format
        result = []
        for device in devices:
            result.append({
                "timestamp": datetime.now().isoformat(),
                "mac": device.get("mac", "Unknown"),
                "name": device.get("name", "Unknown"),
                "rssi": device.get("rssi", 0),
                "scanner": "bluetooth"
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Scan-Fehler: {e}")
        return []

# ========================= MANUAL SCAN =========================

def perform_manual_scan():
    """Führt einen manuellen Scan durch (einmalig)"""
    if not SCANNER_AVAILABLE:
        return {
            "success": False,
            "error": "Scanner not available"
        }
    
    try:
        devices = _perform_scan()
        
        bluetooth_state["last_scan"] = datetime.now().isoformat()
        bluetooth_state["device_count"] = len(devices)
        bluetooth_state["devices"].extend(devices)
        
        return {
            "success": True,
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
