# 🎯 Autodarts MQTT Bridge

A lightweight Python bridge that connects **Autodarts** to **Home Assistant** using **MQTT Discovery**.

This project exposes live dart throws, summaries, totals, and Autodarts availability as Home Assistant sensors — without any manual YAML configuration.

---

## ✨ Features

- 🎯 Dart 1 / 2 / 3 sensors (`T20`, `D16`, `5`, `M`)
- 📋 Throw Summary sensor (`T20 | M | 5`)
- ➕ Throw Total sensor (numeric score)
- 🎯 180 detection (binary sensor)
- 📡 **Autodarts Status sensor** (real online/offline detection)
- 🏠 Home Assistant **MQTT Discovery**
- 🔁 Auto reconnect
- 💥 Offline detection when Autodarts stops or the host shuts down
- 🖥️ Works on **macOS**, **Linux**, and **Windows**

---

## 📦 Requirements

- Python **3.9+**
- An existing **MQTT broker**
- Autodarts running and reachable on the network
- Home Assistant with MQTT integration enabled

---

## 📥 Installation

Follow the steps below to install and run the Autodarts MQTT Bridge.


1️⃣ Clone the repository

``
git clone https://github.com/Quevinsta/autodarts-mqtt.git
cd autodarts-mqtt 
``

2️⃣ Install Python dependencies

Make sure Python 3.9 or newer is installed.
Then install the required packages:

``
pip install paho-mqtt websocket-client requests
``

3️⃣ Configure the script

Create your running configuration from the example file:

``
cp autodarts_mqtt_example.py autodarts_mqtt.py
``

Open autodarts_mqtt.py and update the CONFIG section with your own details:
```python
AUTODARTS_WS_URL = "ws://AUTODARTS_IP:3180/api/events"
AUTODARTS_HTTP_URL = "http://AUTODARTS_IP:3180"

MQTT_HOST = "MQTT_BROKER_IP"
MQTT_PORT = 1883
MQTT_USERNAME = "MQTT_USERNAME"
MQTT_PASSWORD = "MQTT_PASSWORD"
```

4️⃣ Run the script

Start the bridge using:

``
python3 autodarts_mqtt.py
``

If everything is working correctly, you should see output similar to:
```python
Connected to Autodarts WebSocket
🎯 Throw published
📡 Status: online
```


The script will now automatically create all required entities in Home Assistant using MQTT Discovery.
