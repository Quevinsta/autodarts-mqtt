#!/usr/bin/env python3
"""
Autodarts MQTT Example

This is an example configuration for the Autodarts MQTT bridge.
Copy this file to `autodarts_mqtt.py` and fill in your own settings.
"""

import json
import time
import threading
import requests
import websocket
import paho.mqtt.client as mqtt

# ==================================================
# CONFIG (FILL IN YOUR OWN VALUES)
# ==================================================

# Autodarts
AUTODARTS_WS_URL = "ws://AUTODARTS_IP:3180/api/events"
AUTODARTS_HTTP_URL = "http://AUTODARTS_IP:3180"

# MQTT
MQTT_HOST = "MQTT_BROKER_IP"
MQTT_PORT = 1883
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"

# MQTT Topics
MQTT_BASE = "autodarts"
MQTT_STATE_TOPIC = f"{MQTT_BASE}/state"
MQTT_STATUS_TOPIC = f"{MQTT_BASE}/status"

# Home Assistant Discovery
DISCOVERY_PREFIX = "homeassistant"
DEVICE_ID = "autodarts_board"

STATUS_CHECK_INTERVAL = 10  # seconds

IMPOSSIBLE_CHECKOUTS = {169, 168, 166, 165, 163, 162, 159}

# ==================================================
# GLOBALS
# ==================================================

total_scored_points = 0
total_throws = 0

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
    "manufacturer": "Autodarts",
    "model": "Autodarts MQTT Bridge"
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
        "total": "Throw Total",
        "remaining": "Points Remaining",
        "leg_result": "Leg Result",
        "board_status": "Board Status",
        "number_of_throws": "Number of Throws",
        "three_dart_average": "3 Dart Average",
        "leg_average": "Leg Average"
    }

    for key, name in sensors.items():
        mqttc.publish(
            f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/{key}/config",
            json.dumps({
                "name": name,
                "state_topic": MQTT_STATE_TOPIC,
                "value_template": f"{{{{ value_json.{key} }}}}",
                "unique_id": f"{DEVICE_ID}_{key}",
                "device": DEVICE_INFO
            }),
            retain=True
        )

# ==================================================
# HELPERS
# ==================================================

def dart_to_value(dart):
    if dart.startswith("T"):
        return int(dart[1:]) * 3
    if dart.startswith("D"):
        return int(dart[1:]) * 2
    if dart.startswith("M"):
        return 0
    return int(dart) if dart.isdigit() else 0


def is_checkout_possible(remaining):
    if remaining <= 1 or remaining > 170:
        return False
    return remaining not in IMPOSSIBLE_CHECKOUTS


def autodarts_is_online():
    try:
        return requests.get(f"{AUTODARTS_HTTP_URL}/api/state", timeout=1).status_code == 200
    except Exception:
        return False


def fetch_game_state():
    try:
        r = requests.get(f"{AUTODARTS_HTTP_URL}/api/state", timeout=2)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

# ==================================================
# STATE PUBLISHING
# ==================================================

def publish_initial_state():
    mqttc.publish(
        MQTT_STATE_TOPIC,
        json.dumps({
            "dart1": "0",
            "dart2": "0",
            "dart3": "0",
            "dart1_value": 0,
            "dart2_value": 0,
            "dart3_value": 0,
            "summary": "Waiting",
            "total": 0,
            "remaining": 0,
            "checkout_possible": False,
            "leg_result": "offline",
            "is_180": False,
            "board_status": "Offline",
            "number_of_throws": 0,
            "three_dart_average": 0,
            "leg_average": 0
        }),
        retain=True
    )


def publish_offline_state():
    mqttc.publish(
        MQTT_STATE_TOPIC,
        json.dumps({
            "dart1": "0",
            "dart2": "0",
            "dart3": "0",
            "dart1_value": 0,
            "dart2_value": 0,
            "dart3_value": 0,
            "summary": "Offline",
            "total": 0,
            "remaining": 0,
            "checkout_possible": False,
            "leg_result": "offline",
            "is_180": False,
            "board_status": "Offline",
            "number_of_throws": 0,
            "three_dart_average": 0,
            "leg_average": 0
        }),
        qos=1,
        retain=True
    )


def publish_state(state):
    global total_scored_points, total_throws

    throws = state.get("throws", [])
    game = state.get("game", {})
    players = game.get("players", [])
    current_player = state.get("currentPlayer", 0)

    darts = ["0", "0", "0"]
    values = [0, 0, 0]

    for i in range(min(3, len(throws))):
        seg = throws[i].get("segment", {})
        mult = seg.get("multiplier", 0)
        num = seg.get("number", 0)

        dart = (
            f"T{num}" if mult == 3 else
            f"D{num}" if mult == 2 else
            f"M{num}" if mult == 0 else
            str(num)
        )

        darts[i] = dart
        values[i] = dart_to_value(dart)

    number_of_throws = min(len(throws), 3)
    throw_total = sum(values)

    if number_of_throws > 0:
        total_scored_points += throw_total
        total_throws += number_of_throws

    three_dart_average = round(throw_total / 3, 2) if number_of_throws else 0
    leg_average = round((total_scored_points / total_throws) * 3, 2) if total_throws else 0

    remaining = 0
    checkout_possible = False
    leg_result = "playing"

    if players and current_player < len(players):
        remaining = players[current_player].get("score", 0)
        checkout_possible = is_checkout_possible(remaining)

        if players[current_player].get("hasWon"):
            leg_result = "win"
            total_scored_points = 0
            total_throws = 0

    board_status = "Throw"
    if leg_result == "win":
        board_status = "Takeout"
    elif checkout_possible and number_of_throws > 0:
        board_status = "Takeout in Progress"

    payload = {
        "dart1": darts[0],
        "dart2": darts[1],
        "dart3": darts[2],
        "dart1_value": values[0],
        "dart2_value": values[1],
        "dart3_value": values[2],
        "summary": " | ".join(darts),
        "total": throw_total,
        "remaining": remaining,
        "checkout_possible": checkout_possible,
        "leg_result": leg_result,
        "is_180": throw_total == 180,
        "board_status": board_status,
        "number_of_throws": number_of_throws,
        "three_dart_average": three_dart_average,
        "leg_average": leg_average
    }

    mqttc.publish(MQTT_STATE_TOPIC, json.dumps(payload), qos=1, retain=True)

# ==================================================
# STATUS LOOP
# ==================================================

def status_loop():
    last_online = None

    while True:
        online = autodarts_is_online()

        mqttc.publish(
            MQTT_STATUS_TOPIC,
            "online" if online else "offline",
            retain=True
        )

        if online is False and last_online is not False:
            publish_offline_state()

        last_online = online
        time.sleep(STATUS_CHECK_INTERVAL)

# ==================================================
# WEBSOCKET
# ==================================================

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "motion_state":
            time.sleep(0.3)
            state = fetch_game_state()
            if state:
                publish_state(state)
    except Exception:
        pass


def on_open(ws):
    print("Connected to Autodarts WebSocket")


def on_error(ws, error):
    print("WebSocket error:", error)


def on_close(ws):
    print("WebSocket closed")

# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    publish_discovery()
    publish_initial_state()

    threading.Thread(target=status_loop, daemon=True).start()

    ws = websocket.WebSocketApp(
        AUTODARTS_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    while True:
        ws.run_forever()
        time.sleep(5)
