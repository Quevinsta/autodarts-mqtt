"""
Autodarts MQTT Bridge
====================

Final running version with REAL Autodarts status detection.

Status logic:
- ON  -> Autodarts HTTP API reachable
- OFF -> Autodarts stopped / unreachable
- OFF -> script crash or Mac shutdown (MQTT LWT)

Features:
- Dart 1 / 2 / 3 sensors (T20 / D16 / 5 / M)
- Throw Summary (T20 | M | 5)
- Throw Total
- 180 detection
- Autodarts Status (connectivity)
- MQTT Discovery
- Auto reconnect
"""

import json
import time
import requests
import websocket
import paho.mqtt.client as mqtt

# ==================================================
# ================== CONFIG ========================
# ==================================================

AUTODARTS_WS_URL = "ws://192.168.178.XXX:3180/api/events"
AUTODARTS_HTTP_URL = "http://192.168.178.XXX:3180"

MQTT_HOST = "192.168.178.XXX"
MQTT_PORT = 1883
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"

MQTT_STATE_TOPIC = "autodarts/game/state"
MQTT_STATUS_TOPIC = "autodarts/status"

STATUS_CHECK_INTERVAL = 10  # seconds

# ==================================================
# ==================================================

GAME_STATE_ENDPOINTS = [
    "/api/game/state",
    "/api/game",
    "/api/game/current",
    "/api/match",
    "/api/state",
]

LAST_STATUS_CHECK = 0
LAST_STATUS = None

# ==================================================
# MQTT SETUP (with LWT)
# ==================================================
mqttc = mqtt.Client()
mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

mqttc.will_set(
    MQTT_STATUS_TOPIC,
    payload="offline",
    retain=True,
)

mqttc.connect(MQTT_HOST, MQTT_PORT)
mqttc.loop_start()

# ==================================================
# MQTT DISCOVERY
# ==================================================
def publish_discovery():
    device = {
        "identifiers": ["autodarts"],
        "name": "Autodarts",
        "manufacturer": "Autodarts",
        "model": "Camera Dartboard",
    }

    def dart_template(i):
        return (
            "{{ value_json.throws[%d].segment.multiplier == 0 and 'M' "
            "or value_json.throws[%d].segment.multiplier == 3 and 'T' ~ value_json.throws[%d].segment.number "
            "or value_json.throws[%d].segment.multiplier == 2 and 'D' ~ value_json.throws[%d].segment.number "
            "or value_json.throws[%d].segment.number }}"
        ) % (i, i, i, i, i, i)

    sensors = {
        "autodarts_dart_1": {"name": "Autodarts Dart 1", "value_template": dart_template(0)},
        "autodarts_dart_2": {"name": "Autodarts Dart 2", "value_template": dart_template(1)},
        "autodarts_dart_3": {"name": "Autodarts Dart 3", "value_template": dart_template(2)},
        "autodarts_throw_summary": {
            "name": "Autodarts Throw Summary",
            "value_template": f"{dart_template(0)} | {dart_template(1)} | {dart_template(2)}",
        },
        "autodarts_throw_total": {
            "name": "Autodarts Throw Total",
            "unit_of_measurement": "pts",
            "value_template": (
                "{{ (value_json.throws[0].segment.number * value_json.throws[0].segment.multiplier "
                "if value_json.throws | length > 0 else 0) + "
                "(value_json.throws[1].segment.number * value_json.throws[1].segment.multiplier "
                "if value_json.throws | length > 1 else 0) + "
                "(value_json.throws[2].segment.number * value_json.throws[2].segment.multiplier "
                "if value_json.throws | length > 2 else 0) }}"
            ),
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

    mqttc.publish(
        "homeassistant/binary_sensor/autodarts_180/config",
        json.dumps({
            "name": "Autodarts 180",
            "state_topic": MQTT_STATE_TOPIC,
            "value_template": (
                "{{ value_json.throws | length == 3 and "
                "value_json.throws[0].segment.multiplier == 3 and value_json.throws[0].segment.number == 20 and "
                "value_json.throws[1].segment.multiplier == 3 and value_json.throws[1].segment.number == 20 and "
                "value_json.throws[2].segment.multiplier == 3 and value_json.throws[2].segment.number == 20 }}"
            ),
            "payload_on": "True",
            "payload_off": "False",
            "unique_id": "autodarts_180",
            "device": device,
        }),
        retain=True,
    )

    mqttc.publish(
        "homeassistant/binary_sensor/autodarts_status/config",
        json.dumps({
            "name": "Autodarts Status",
            "state_topic": MQTT_STATUS_TOPIC,
            "payload_on": "online",
            "payload_off": "offline",
            "device_class": "connectivity",
            "unique_id": "autodarts_status",
            "device": device,
        }),
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
            if r.status_code == 200 and r.text.startswith("{"):
                return r.json()
        except Exception:
            pass
    return None


def autodarts_is_online():
    try:
        r = requests.get(AUTODARTS_HTTP_URL + "/api/state", timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def publish_status():
    global LAST_STATUS, LAST_STATUS_CHECK

    if time.time() - LAST_STATUS_CHECK < STATUS_CHECK_INTERVAL:
        return

    LAST_STATUS_CHECK = time.time()
    online = autodarts_is_online()
    new_status = "online" if online else "offline"

    if new_status != LAST_STATUS:
        mqttc.publish(MQTT_STATUS_TOPIC, new_status, retain=True)
        LAST_STATUS = new_status
        print(f"📡 Status: {new_status}")

# ==================================================
# WEBSOCKET CALLBACKS
# ==================================================
def on_message(ws, message):
    try:
        publish_status()

        if json.loads(message).get("type") == "motion_state":
            time.sleep(0.3)
            state = fetch_game_state()
            if state:
                mqttc.publish(MQTT_STATE_TOPIC, json.dumps(state))
                print("🎯 Throw published")

    except Exception as e:
        print("❌ Error:", e)

def on_open(ws):
    print("✅ Connected to Autodarts WebSocket")

def on_close(ws, *args):
    print("🔌 WebSocket closed")

# ==================================================
# MAIN LOOP
# ==================================================
while True:
    websocket.WebSocketApp(
        AUTODARTS_WS_URL,
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
    ).run_forever()
    time.sleep(2)
