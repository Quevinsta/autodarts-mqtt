#!/usr/bin/env python3
# Autodarts MQTT Bridge – Example
# Version: 1.1.5

import json
import time
import threading
import sys
from pathlib import Path

import requests
import websocket
import paho.mqtt.client as mqtt

# ==================================================
# VERSION
# ==================================================

VERSION = "1.1.5"

# ==================================================
# CONFIG LOADING (PyInstaller safe)
# ==================================================

def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def load_config():
    base_path = get_base_path()
    config_path = base_path / "config.json"

    if not config_path.exists():
        print(f"❌ config.json not found at: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    required = [
        "AUTODARTS_WS_URL",
        "AUTODARTS_HTTP_URL",
        "MQTT_HOST",
        "MQTT_PORT"
    ]

    for key in required:
        value = config.get(key)
        if not value or "CHANGEME" in str(value):
            print("❌ config.json is not configured yet.")
            print(f"➡️ Please edit: {config_path}")
            sys.exit(1)

    return config


config = load_config()

AUTODARTS_WS_URL = config["AUTODARTS_WS_URL"]
AUTODARTS_HTTP_URL = config["AUTODARTS_HTTP_URL"]

MQTT_HOST = config["MQTT_HOST"]
MQTT_PORT = int(config.get("MQTT_PORT", 1883))
MQTT_USERNAME = config.get("MQTT_USERNAME", "")
MQTT_PASSWORD = config.get("MQTT_PASSWORD", "")

# ==================================================
# MQTT / HA CONFIG
# ==================================================

MQTT_BASE = "autodarts"
MQTT_STATE_TOPIC = f"{MQTT_BASE}/state"
MQTT_STATUS_TOPIC = f"{MQTT_BASE}/status"

DISCOVERY_PREFIX = "homeassistant"
DEVICE_ID = "autodarts_camera"

STATUS_CHECK_INTERVAL = 10  # seconds

# ==================================================
# MQTT SETUP
# ==================================================

mqttc = mqtt.Client()
mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqttc.will_set(
    MQTT_STATUS_TOPIC,
    payload="offline",
    qos=1,
    retain=True
)

mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.loop_start()

# ==================================================
# MQTT DISCOVERY
# ==================================================

DEVICE_INFO = {
    "identifiers": [DEVICE_ID],
    "name": "Autodarts",
    "manufacturer": "Quevinsta",
    "model": "Autodarts MQTT Bridge",
    "sw_version": VERSION
}


def publish_discovery():
    sensors = {
        "dart1": "Dart 1",
        "dart2": "Dart 2",
        "dart3": "Dart 3",
        "dart1_value": "Dart 1 Value",
        "dart2_value": "Dart 2 Value",
        "dart3_value": "Dart 3 Value",
        "summary": "Throw Summary",
        "total": "Throw Total"
    }

    for key, name in sensors.items():
        payload = {
            "name": name,
            "state_topic": MQTT_STATE_TOPIC,
            "value_template": f"{{{{ value_json.{key} }}}}",
            "unique_id": f"{DEVICE_ID}_{key}",
            "device": DEVICE_INFO
        }

        mqttc.publish(
            f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/{key}/config",
            json.dumps(payload),
            retain=True
        )

    mqttc.publish(
        f"{DISCOVERY_PREFIX}/binary_sensor/{DEVICE_ID}/180/config",
        json.dumps({
            "name": "180",
            "state_topic": MQTT_STATE_TOPIC,
            "value_template": "{{ value_json.is_180 }}",
            "payload_on": True,
            "payload_off": False,
            "unique_id": f"{DEVICE_ID}_180",
            "device": DEVICE_INFO
        }),
        retain=True
    )

    mqttc.publish(
        f"{DISCOVERY_PREFIX}/binary_sensor/{DEVICE_ID}/status/config",
        json.dumps({
            "name": "Autodarts Status",
            "state_topic": MQTT_STATUS_TOPIC,
            "payload_on": "online",
            "payload_off": "offline",
            "unique_id": f"{DEVICE_ID}_status",
            "device": DEVICE_INFO
        }),
        retain=True
    )

    print("📡 MQTT Discovery published")


# ==================================================
# AUTODARTS HELPERS
# ==================================================

def autodarts_is_online():
    try:
        r = requests.get(f"{AUTODARTS_HTTP_URL}/api/state", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def fetch_game_state():
    try:
        r = requests.get(f"{AUTODARTS_HTTP_URL}/api/state", timeout=2)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# ==================================================
# STATE PUBLISHING
# ==================================================

def publish_state(state):
    throws = state.get("throws", [])

    dart_labels = ["M", "M", "M"]
    dart_values = [0, 0, 0]
    total = 0

    for i, t in enumerate(throws[:3]):
        seg = t.get("segment", {})
        mult = seg.get("multiplier", 0)
        num = seg.get("number", 0)
        name = seg.get("name", "M")

        if mult == 0:
            dart_labels[i] = "M"
            dart_values[i] = 0
        else:
            dart_labels[i] = name
            dart_values[i] = num * mult
            total += dart_values[i]

    payload = {
        "dart1": dart_labels[0],
        "dart2": dart_labels[1],
        "dart3": dart_labels[2],
        "dart1_value": dart_values[0],
        "dart2_value": dart_values[1],
        "dart3_value": dart_values[2],
        "summary": " | ".join(dart_labels),
        "total": total,
        "is_180": total == 180
    }

    mqttc.publish(MQTT_STATE_TOPIC, json.dumps(payload), qos=1, retain=False)
    print("🎯 Published:", payload)


# ==================================================
# STATUS LOOP
# ==================================================

def status_loop():
    while True:
        mqttc.publish(
            MQTT_STATUS_TOPIC,
            "online" if autodarts_is_online() else "offline",
            retain=True
        )
        time.sleep(STATUS_CHECK_INTERVAL)


# ==================================================
# WEBSOCKET HANDLERS
# ==================================================

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "motion_state":
            time.sleep(0.3)
            state = fetch_game_state()
            if state:
                publish_state(state)
    except Exception as e:
        print("❌ WS error:", e)


def on_open(ws):
    print("✅ Connected to Autodarts WebSocket")


def on_error(ws, error):
    print("❌ WebSocket error:", error)


def on_close(ws):
    print("🔌 WebSocket closed")


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    print(f"🚀 Autodarts MQTT Bridge v{VERSION}")

    publish_discovery()

    threading.Thread(
        target=status_loop,
        daemon=True
    ).start()

    ws = websocket.WebSocketApp(
        AUTODARTS_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    while True:
        try:
            ws.run_forever()
        except Exception as e:
            print("❌ WebSocket crashed:", e)
        time.sleep(5)
