![GitHub release](https://img.shields.io/github/v/release/Quevinsta/autodarts-mqtt)
![Downloads](https://img.shields.io/github/downloads/Quevinsta/autodarts-mqtt/total)
![Downloads latest](https://img.shields.io/github/downloads/Quevinsta/autodarts-mqtt/latest/total)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-41BDF5?logo=home-assistant&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Required-orange)
![Autodarts Community](https://img.shields.io/badge/Autodarts-Community-purple)
![License](https://img.shields.io/github/license/Quevinsta/autodarts-mqtt)
![Stars](https://img.shields.io/github/stars/Quevinsta/autodarts-mqtt?style=social)

# Autodarts MQTT

Realtime MQTT bridge for Autodarts with Home Assistant support.

This project publishes live Autodarts game data to MQTT and supports automatic discovery in Home Assistant.

---

## ✨ Features
- Realtime WebSocket updates
- Board Status (Throw / Takeout / Offline)
- Number of Throws (0–3)
- 3-Dart Average
- Leg Average
- Offline detection
- Home Assistant MQTT Discovery

<img width="300" height="803" alt="Scherm­afbeelding 2026-01-22 om 01 30 16" src="https://github.com/user-attachments/assets/85ac6e71-fbd1-4bf3-b383-f5db7a34ae4d" />

---

## 📋 Requirements
- MQTT broker (e.g. Mosquitto, Home Assistant)
- Python 3.9+ (if not using binaries)

---

## 🔐 Security
- Never commit credentials
- Use `autodarts_mqtt_example.py` as a template
- The example file contains no secrets

---

## 📬 Support
- Issues & feature requests via GitHub

---

## Installation
- Please use Google for how to fire a Python script on your OS.
- Adjust the credentials to your server details (Autodarts & MQTT) in the autodarts_mqtt.py.




