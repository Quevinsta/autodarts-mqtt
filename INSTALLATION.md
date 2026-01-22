Installation Guide – Autodarts MQTT

This guide explains how to install, configure, start, and automatically 
run
Autodarts MQTT on macOS, Linux, and Windows.

Requirements

Autodarts firmware 1.4.0 or newer

MQTT broker (Mosquitto, Home Assistant, etc.)

Network access to the Autodarts server

Python 3.9+ (only required for Python installation)

Installation Methods

You can run Autodarts MQTT in two ways:

Prebuilt binaries (recommended)

Python script (recommended for customization)

Option 1 – Prebuilt Binaries (Recommended)
macOS

Download autodarts-mqtt.pkg from GitHub Releases

Double-click the installer and follow the steps

The binary is installed to:

/usr/local/bin/autodarts-mqtt

Start manually:

autodarts-mqtt

Windows

Download autodarts-mqtt.exe from GitHub Releases

Place the file anywhere (for example C:\autodarts)

Start by double-clicking or via Command Prompt:

autodarts-mqtt.exe

Windows may show a security warning because the file is unsigned.
Choose More info → Run anyway.

Linux

At the moment, Linux uses the Python installation method below.

Option 2 – Python Installation (All Platforms)
Clone the repository
git clone https://github.com/Quevinsta/autodarts-mqtt.git
cd autodarts-mqtt

Create a virtual environment
python3 -m venv venv


Activate it:

macOS / Linux:

source venv/bin/activate


Windows:

venv\Scripts\activate

Install dependencies
pip install requests websocket-client paho-mqtt

Configure

Copy the example file:

cp autodarts_mqtt_example.py autodarts_mqtt.py


Edit autodarts_mqtt.py and configure:

Autodarts IP address

MQTT broker host and port

MQTT username and password (if required)

Start manually
python3 autodarts_mqtt.py

Home Assistant Integration

MQTT Discovery is enabled by default

Sensors appear automatically in Home Assistant

No manual YAML configuration required

Available sensors include:

Board Status (Throw / Takeout / Offline)

Number of Throws

3-Dart Average

Leg Average

Remaining score

Dart values and summaries

Automatic Start (Autostart)
macOS – launchd

Create a LaunchAgent file:

nano ~/Library/LaunchAgents/com.quevinsta.autodarts-mqtt.plist


Paste the following content (adjust paths if needed):

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.quevinsta.autodarts-mqtt</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/path/to/autodarts_mqtt.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/autodarts-mqtt.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/autodarts-mqtt.err</string>
  </dict>
</plist>


Load and start:

launchctl load ~/Library/LaunchAgents/com.quevinsta.autodarts-mqtt.plist
launchctl start com.quevinsta.autodarts-mqtt


To stop or unload:

launchctl unload ~/Library/LaunchAgents/com.quevinsta.autodarts-mqtt.plist

Linux – systemd

Create a service file:

sudo nano /etc/systemd/system/autodarts-mqtt.service


Paste the following content:

[Unit]
Description=Autodarts MQTT Bridge
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/autodarts_mqtt.py
WorkingDirectory=/path/to
Restart=always
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target


Enable and start:

sudo systemctl daemon-reload
sudo systemctl enable autodarts-mqtt
sudo systemctl start autodarts-mqtt


Check status:

sudo systemctl status autodarts-mqtt

Windows – Task Scheduler

Press Win + R, type taskschd.msc, press Enter

Click Create Task

General tab:

Name: Autodarts MQTT

Enable Run whether user is logged on or not

Triggers tab:

New → At startup

Actions tab:

Action: Start a program

Program/script:

python.exe


Add arguments:

C:\path\to\autodarts_mqtt.py


Start in:

C:\path\to\


Save the task.

The script will now start automatically on system boot.

Troubleshooting
Script exits immediately

Configuration placeholders are still present

Edit autodarts_mqtt.py and fill in all required values

No sensors in Home Assistant

Verify MQTT broker is running

Check MQTT credentials

Ensure Home Assistant MQTT integration is enabled

Security Notes

Never publish your personal autodarts_mqtt.py

Use autodarts_mqtt_example.py for sharing

Do not commit credentials to GitHub

Firmware Compatibility
Autodarts firmware	Supported
1.4.0+	Yes
< 1.4.0	No
