"""
Autodarts MQTT Bridge (Example Configuration)
=============================================

This script bridges Autodarts to MQTT and Home Assistant using MQTT 
Discovery.

⚠️ This is an EXAMPLE file.
Copy this file to `autodarts_mqtt.py` and fill in the CONFIG section.

Features:
- Dart 1 / Dart 2 / Dart 3 sensors
- Throw Summary (T20 | 20 | 5)
- Throw Total (85 / 140 / 180)
- 180 detection (binary sensor)
- Home Assistant MQTT Discovery
- Auto reconnect
- macOS & Linux compatible

License: MIT
"""

import json
import time
import requests
import websocket
import paho.mqtt.client as mqtt

# ==================================================
# ================== CONFIG ========================
# ==================================================

# Autodarts configuration
AUTODARTS_WS_URL = "ws://AUTODARTS_IP:3180/api/events"
AUTODARTS_HTTP_URL = "http://AUTODARTS_IP:3180"

# MQTT configuration
MQTT_HOST = "MQTT_BROKER_IP"
MQTT_PORT = 1883
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"

# MQTT topic for publishing game state
MQTT_STATE_TOPIC = "autodarts/game/state"

# ==================================================
# ==================================================

GAME_STATE_ENDPOINTS = [
    "/api/game/state",
    "/api/game",
    "/api/game/current",
    "/api/match",
    "/api/state",
]

# ==================================================
# MQTT SETUP
# ==================================================
mqttc = mqtt.Client()
mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttc.connect(MQTT_HOST, MQTT_PORT)
mqttc.loop_start()

# ==================================================
# MQTT DISCOVERY (HOME ASSISTANT)
# ==================================================
def publish_discovery():
    device = {
        "identifiers": ["autodarts"],
        "name": "Autodarts",
        "manufacturer": "Autodarts",
        "model": "Camera Dartboard",
    }

    sensors = {
        "autodarts_dart_1": {
            "name": "Autodarts Dart 1",
            "value_template": "{{ value_json.throws[0].segment.number if 
value_json.throws | length > 0 else 'unknown' }}"
        },
        "autodarts_dart_2": {
            "name": "Autodarts Dart 2",
            "value_template": "{{ value_json.throws[1].segment.number if 
value_json.throws | length > 1 else 'unknown' }}"
        },
        "autodarts_dart_3": {
            "name": "Autodarts Dart 3",
            "value_template": "{{ value_json.throws[2].segment.number if 
value_json.throws | length > 2 else 'unknown' }}"
        },
        "autodarts_throw_summary": {
            "name": "Autodarts Throw Summary",
            "value_template": (
                "{{ (value_json.throws[0].segment.multiplier == 3 and 'T' 
~ value_json.throws[0].segment.number) "
                "or (value_json.throws[0].segment.multiplier == 2 and 'D' 
~ value_json.throws[0].segment.number) "
                "or value_json.throws[0].segment.number }} | "
                "{{ (value_json.throws[1].segment.multiplier == 3 and 'T' 
~ value_json.throws[1].segment.number) "
                "or (value_json.throws[1].segment.multiplier == 2 and 'D' 
~ value_json.throws[1].segment.number) "
                "or value_json.throws[1].segment.number }} | "
                "{{ (value_json.throws[2].segment.multiplier == 3 and 'T' 
~ value_json.throws[2].segment.number) "
                "or (value_json.throws[2].segment.multiplier == 2 and 'D' 
~ value_json.throws[2].segment.number) "
                "or value_json.throws[2].segment.number }}"
            )
        },
        "autodarts_throw_total": {
            "name": "Autodarts Throw Total",
            "unit_of_measurement": "pts",
            "value_template": (
                "{{ (value_json.throws[0].segment.number * 
value_json.throws[0].segment.multiplier "
                "if value_json.throws | length > 0 else 0) + "
                "(value_json.throws[1].segment.number * 
value_json.throws[1].segment.multiplier "
                "if value_json.throws | length > 1 else 0) + "
                "(value_json.throws[2].segment.number * 
value_json.throws[2].segment.multiplier "
                "if value_json.throws | length > 2 else 0) }}"
            )
        },
    }

    for uid, cfg in sensors.items():
        payload = {
            "name": cfg["name"],
            "state_topic": MQTT_STATE_TOPIC,
            "value_template": cfg["value_template"],
            "unique_id": uid,
            "device": device,
        }

        if "unit_of_measurement" in cfg:
            payload["unit_of_measurement"] = cfg["unit_of_measurement"]

        mqttc.publish(
            f"homeassistant/sensor/{uid}/config",
            json.dumps(payload),
            retain=True,
        )

    payload_180 = {
        "name": "Autodarts 180",
        "state_topic": MQTT_STATE_TOPIC,
        "value_template": (
            "{{ value_json.throws | length == 3 and "
            "value_json.throws[0].segment.multiplier == 3 and 
value_json.throws[0].segment.number == 20 and "
            "value_json.throws[1].segment.multiplier == 3 and 
value_json.throws[1].segment.number == 20 and "
            "value_json.throws[2].segment.multiplier == 3 and 
value_json.throws[2].segment.number == 20 }}"
        ),
        "payload_on": "True",
        "payload_off": "False",
        "device_class": "sound",
        "unique_id": "autodarts_180",
        "device": device,
    }

    mqttc.publish(
        "homeassistant/binary_sensor/autodarts_180/config",
        json.dumps(payload_180),
        retain=True,
    )


publish_discovery()

# ==================================================
# HELPERS
# ==================================================
def fetch_game_state():
    for path in GAME_STATE_ENDPOINTS:
        try:
            r = requests.get(AUTODARTS_HTTP_URL + path, timeout=1)
            if r.status_code == 200 and r.text.strip().startswith("{"):
                return r.json()
        except Exception:
            pass
    return None

# ==================================================
# WEBSOCKET CALLBACKS
# ==================================================
def on_message(ws, message):
    try:
        data = json.loads(message)

        if data.get("type") == "motion_state":
            time.sleep(0.3)
            state = fetch_game_state()
            if state:
                mqttc.publish(MQTT_STATE_TOPIC, json.dumps(state))
                print("🎯 Throw published")

    except Exception as e:
        print("❌ Error:", e)

def on_open(ws):
    print("✅ Connected to Autodarts WebSocket")

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, *args):
    print("🔌 WebSocket closed")

# ==================================================
# MAIN LOOP (AUTO RECONNECT)
# ==================================================
while True:
    ws = websocket.WebSocketApp(
        AUTODARTS_WS_URL,
        on_message=on_message,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
    time.sleep(2)

