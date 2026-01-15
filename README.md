![GitHub release](https://img.shields.io/github/v/release/Quevinsta/autodarts-mqtt?include_prereleases=false)
![Windows Build](https://github.com/Quevinsta/autodarts-mqtt/actions/workflows/build-windows.yml/badge.svg)
![Last commit](https://img.shields.io/github/last-commit/Quevinsta/autodarts-mqtt)
![License](https://img.shields.io/github/license/Quevinsta/autodarts-mqtt)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![Stars](https://img.shields.io/github/stars/Quevinsta/autodarts-mqtt?style=social)

# Autodarts MQTT Bridge

Autodarts MQTT Bridge connects **Autodarts** to **Home Assistant** using **MQTT**.  
It publishes dart throws, scores, and game state automatically via MQTT Discovery.

This project provides **standalone installers** for macOS and Windows — no Python knowledge required.

---

## ✨ Features

- 🎯 Dart throw detection (Single / Double / Triple / Miss)
- 🔢 Per-dart sensors (Dart 1 / Dart 2 / Dart 3)
- 📊 Throw summary and total score
- 💯 180 detection
- 🔌 Autodarts status sensor (online / offline)
- 🏠 Home Assistant MQTT Discovery (automatic entities)
- 📦 Standalone installers (macOS & Windows)

---

## 📥 Installation

### macOS (recommended)
1. Download `autodarts-mqtt.pkg` from **GitHub Releases**
2. Double-click the `.pkg` installer
3. The application is installed to:

# Autodarts MQTT Bridge

Autodarts MQTT Bridge connects **Autodarts** to **Home Assistant** using **MQTT**.  
It publishes dart throws, scores, and game state automatically via MQTT Discovery.

This project provides **standalone installers** for macOS and Windows — no Python knowledge required.

---

## ✨ Features

- 🎯 Dart throw detection (Single / Double / Triple / Miss)
- 🔢 Per-dart sensors (Dart 1 / Dart 2 / Dart 3)
- 📊 Throw summary and total score
- 💯 180 detection
- 🔌 Autodarts status sensor (online / offline)
- 🏠 Home Assistant MQTT Discovery (automatic entities)
- 📦 Standalone installers (macOS & Windows)

---

## 📥 Installation

### macOS (recommended)
1. Download `autodarts-mqtt.pkg` from **GitHub Releases**
2. Double-click the `.pkg` installer
3. The application is installed to:

- ```/Applications/Autodarts```


---

### Windows
1. Download `autodarts-mqtt.exe` from **GitHub Releases**
2. Place the `.exe` in a folder of your choice
3. Double-click to run

> ⚠️ Windows SmartScreen may warn on first run  
> Click **More info → Run anyway**

---

## ⚙️ Configuration

After installation, a file named `config.json` is required **next to the executable**.

### Location
- **macOS**: `/Applications/Autodarts/config.json`
- **Windows**: same folder as `autodarts-mqtt.exe`

### Example `config.json`
```json
{
  "autodarts_ws_url": "ws://AUTODARTS_IP:3180/api/events",
  "autodarts_http_url": "http://AUTODARTS_IP:3180",
  "mqtt_host": "MQTT_BROKER_IP",
  "mqtt_port": 1883,
  "mqtt_username": "MQTT_USERNAME",
  "mqtt_password": "MQTT_PASSWORD"
}
```

➡️ Replace all placeholder values with your own configuration.

➡️ The application will not start until placeholders are replaced.

▶️ Running the application
macOS
```
/Applications/Autodarts/autodarts-mqtt
```

Windows
Double-click ```autodarts-mqtt.exe```

---

🏠 Home Assistant

- Uses MQTT Discovery
- Entities appear automatically
- No YAML required in Home Assistant
- Example entities
- Dart 1 / Dart 2 / Dart 3
- Throw Summary
- Throw Total
- 180 Detection
- Autodarts Status

---

🛠 Requirements

- MQTT broker (e.g. Mosquitto)
- Autodarts running and reachable on your network
- Home Assistant with MQTT integration enabled

---

⚠️ Notes

- macOS Gatekeeper may warn about unsigned software
- Windows SmartScreen warnings are normal for open-source executables
- config.json contains sensitive data — do not share it

---

🚀 Roadmap

- Automatic startup (launchd / Windows service)
- Docker support
- Advanced game state sensors
- Multi-board support

---

📄 License

- MIT License

---

❤️ Credits

Developed by Quevinsta
Built for the Autodarts & Home Assistant community.
