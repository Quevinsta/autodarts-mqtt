![GitHub release](https://img.shields.io/github/v/release/Quevinsta/autodarts-mqtt)
![Downloads](https://img.shields.io/github/downloads/Quevinsta/autodarts-mqtt/total)
![Downloads latest](https://img.shields.io/github/downloads/Quevinsta/autodarts-mqtt/latest/total)
![Windows Build](https://github.com/Quevinsta/autodarts-mqtt/actions/workflows/build-windows.yml/badge.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-41BDF5?logo=home-assistant&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Required-orange)
![Autodarts Community](https://img.shields.io/badge/Autodarts-Community-purple)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![License](https://img.shields.io/github/license/Quevinsta/autodarts-mqtt)
![Stars](https://img.shields.io/github/stars/Quevinsta/autodarts-mqtt?style=social)

## 🚀 Autodarts MQTT – v1.4.0

This release updates the MQTT bridge and example script to be fully compatible with **Autodarts firmware 1.4.0** and introduces major stability and usability improvements.

### ✨ New & Improved
- ✅ Compatibility with **Autodarts firmware 1.4.0**
- 🎯 Board Status sensor  
  - `Throw`
  - `Takeout in Progress`
  - `Takeout`
  - `Offline`
- 🔢 Number of Throws sensor (0–3)
- 📊 3-Dart Average (per visit)
- 📈 Leg Average (running average, auto-reset on win)
- 🔄 Real-time updates via WebSocket
- 📴 Proper offline detection and MQTT state handling

### 🏠 Home Assistant
- MQTT Discovery support
- Clean sensor states when Autodarts is offline
- Retained MQTT states for reliable dashboards & automations

### 🔐 Security & Safety
- Example script (`autodarts_mqtt_example.py`) contains **no credentials**
- Clear placeholders for configuration
- Safe to publish and share

### 🛠 Technical
- Improved MQTT stability
- Reduced MQTT spam
- Better error handling
- Clean separation between example and production script

---

**Recommended for all users running Autodarts firmware 1.4.0 or newer.**
