#!/usr/bin/env python3
"""
Autodarts MQTT Bridge (Example)

This example uses config.json for all settings.
It is safe to publish and intended for GitHub releases.
"""

import json
import time
import threading
import sys
from pathlib import Path

import requests
import websocket
import paho.mqtt.client as mqtt

# ==================================================
# LOAD CONFIG
# ==================================================

def load_config():
    config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        print(f"❌ config.json not found at: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    required_keys = [
        "AUTODARTS_WS_URL",
        "AUTODARTS_HTTP_URL",
        "MQTT_HOST",
        "MQTT_PORT"
    ]

    for key in required_keys:
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
MQTT_PORT = int(config["MQTT_PORT"])
MQTT_USERNAME = config.get("MQTT_USERNAME", "")
MQTT_PASSWORD = config.get("MQTT_PASSWORD", "")

MQTT_BASE = "autodarts"
MQTT_STATE_TOPIC = f"{MQTT_BASE}/state"
MQTT_STATUS_TOPIC = f"{MQTT_BASE}/status"

DISCOVERY_PREFIX = "homeassistant"
DEVICE_ID = "autodarts_camera"

STATUS_CHECK_INTERVAL = 10

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
    "name": "Autodarts Camera",
    "manufacturer": "Quevinsta",
    "model": "Autodarts MQTT Bridge",
    "sw_version": "1.1.4"
}


def publish_discovery():
    sensors = {
        "dart1": "Dart 1",
        "dart2": "Dart 2",
        "dart3": "Dart 3",
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

        topic = f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/{key}/config"
        mqttc.publish(topic, json.dumps(payload), retain=True)

    payload_180 = {
        "name": "180",
        "state_topic": MQTT_STATE_TOPIC,
        "value_template": "{{ value_json.is_180 }}",
        "payload_on": True,
        "payload_off": False,
        "unique_id": f"{DEVICE_ID}_180",
        "device": DEVICE_INFO
    }

    mqttc.publish(
        f"{DISCOVERY_PREFIX}/binary_sensor/{DEVICE_ID}/180/config",
        json.dumps(payload_180),
        retain=True
    )

    payload_status = {
        "name": "Autodarts Status",
        "state_topic": MQTT_STATUS_TOPIC,
        "payload_on": "online",
        "payload_off": "offline",
        "unique_id": f"{DEVICE_ID}_status",
        "device": DEVICE_INFO
    }

    mqttc.publish(
        f"{DISCOVERY_PREFIX}/binary_sensor/{DEVICE_ID}/status/config",
        json.dumps(payload_status),
        retain=True
    )

    print("📡 MQTT Discovery published")


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def autodarts_is_online():
    try:
        r = requests.get(f"{AUTODARTS_HTTP_URL}/api/state", timeout=2)
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


def format_dart(segment):
    if not segment:
        return "M", 0

    mult = segment.get("multiplier", 0)
    num = segment.get("number", 0)

    if mult == 0:
        return "M", 0

    label = segment.get("name", "")
    value = num * mult
    return label, value


def publish_state(state):
    throws = state.get("throws", [])

    darts = []
    total = 0

    for t in throws[:3]:
        label, value = format_dart(t.get("segment"))
        darts.append(label)
        total += value

    while len(darts) < 3:
        darts.append("M")

    payload = {
        "dart1": darts[0],
        "dart2": darts[1],
        "dart3": darts[2],
        "summary": " | ".join(darts),
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
        if autodarts_is_online():
            mqttc.publish(MQTT_STATUS_TOPIC, "online", retain=True)
        else:
            mqttc.publish(MQTT_STATUS_TOPIC, "offline", retain=True)
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
    print("🚀 Starting Autodarts MQTT Bridge (example)")

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
