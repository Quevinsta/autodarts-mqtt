# 🎯 Autodarts MQTT Bridge

A lightweight Python bridge that connects **Autodarts** to **MQTT** and **Home Assistant**  
using **MQTT Discovery**.

This project exposes dart throws and scores as Home Assistant entities, making it easy
to build dashboards, automations and statistics around your dart games.

---

## ✨ Features

- 🎯 Dart 1 / Dart 2 / Dart 3 sensors
- 🧾 Throw Summary (e.g. `T20 | 20 | 5`)
- ➕ Throw Total (e.g. `85`, `140`, `180`)
- 🔔 180 detection (binary sensor)
- 🏠 Automatic Home Assistant MQTT Discovery
- 🔄 Auto reconnect on WebSocket drop
- 💻 Works on **macOS & Linux**
- 🧩 Single-file, easy to extend

---

## 🧠 How it works

- Listens to Autodarts events via WebSocket
- Fetches the current game state via HTTP
- Publishes game state to MQTT as JSON
- Home Assistant discovers sensors automatically via MQTT Discovery

No Home Assistant YAML configuration required.

---

## 📦 Requirements

- Python **3.9+**
- Autodarts running
- MQTT broker (e.g. Mosquitto)
- Home Assistant (optional, but recommended)

Python dependencies:

```bash
pip install paho-mqtt websocket-client requests



## 🚀 Installation & Usage

### 1️⃣ Get the script

This repository contains an **example configuration**.

Copy the example file:

```bash
cp autodarts_mqtt_example.py autodarts_mqtt.py

### 2️⃣ Configure

Edit the CONFIG section at the top of autodarts_mqtt.py:

AUTODARTS_WS_URL = "ws://AUTODARTS_IP:3180/api/events"
AUTODARTS_HTTP_URL = "http://AUTODARTS_IP:3180"

MQTT_HOST = "MQTT_BROKER_IP"
MQTT_PORT = 1883
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"

### 3️⃣ Run
python3 autodarts_mqtt.py

The script will keep running and automatically reconnect if needed.
