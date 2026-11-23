# air2mqtt

[![CI](https://github.com/Neluxx/air2mqtt/actions/workflows/ci.yml/badge.svg)](https://github.com/Neluxx/air2mqtt/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/air2mqtt)](https://pypi.org/project/air2mqtt/)
[![Python](https://img.shields.io/pypi/pyversions/air2mqtt)](https://pypi.org/project/air2mqtt/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Neluxx/air2mqtt/blob/main/LICENSE)

**Indoor air quality for Home Assistant, from a Raspberry Pi.**

air2mqtt reads a **BME680** (temperature, humidity, pressure) and an **MH-Z19** (CO₂) sensor on a Raspberry Pi and publishes the values to **Home Assistant via MQTT**.

```
BME680 ──I²C──┐
              ├── Raspberry Pi (air2mqtt) ──MQTT──> Broker ──> Home Assistant
MH-Z19 ──UART─┘
```

## Features

- **No setup in Home Assistant:** the device and its entities appear automatically through MQTT discovery.
- **Runs unattended** as a systemd service and reconnects to the broker on its own.
- **Reliable availability:** the device shows as unavailable when the Pi goes offline, and values expire if a sensor stops reporting.
- **Fault tolerant:** if one sensor is missing or fails, the other keeps working.

## Requirements

- Raspberry Pi (or another Linux board) with Python 3.11 or newer
- A BME680 and/or an MH-Z19 sensor, wired up with I²C/UART enabled
- Home Assistant 2024.11 or newer with an MQTT broker

See [Prerequisites](https://github.com/Neluxx/air2mqtt/blob/main/docs/PREREQUISITES.md) for wiring and broker setup.

## Quick start

**1. Install** into a virtual environment:

```bash
sudo mkdir /opt/air2mqtt && sudo chown $USER:$USER /opt/air2mqtt
cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install air2mqtt
```

**2. Configure.** Create `/opt/air2mqtt/.env` with your broker details:

```ini
MQTT_HOST=homeassistant.local
MQTT_USERNAME=air2mqtt
MQTT_PASSWORD=change-me
```

**3. Run:**

```bash
.venv/bin/air2mqtt
```

The device appears in Home Assistant under **Settings → Devices & services → MQTT**. To start air2mqtt automatically at boot, set it up as a [systemd service](https://github.com/Neluxx/air2mqtt/blob/main/docs/INSTALLATION.md#4-run-as-a-service).

## Documentation

| Guide | Contents |
| --- | --- |
| [Prerequisites](https://github.com/Neluxx/air2mqtt/blob/main/docs/PREREQUISITES.md) | Sensors and wiring, enabling I²C/UART, Home Assistant and MQTT broker |
| [Installation](https://github.com/Neluxx/air2mqtt/blob/main/docs/INSTALLATION.md) | Installing, running as a service, updating and uninstalling |
| [Configuration](https://github.com/Neluxx/air2mqtt/blob/main/docs/CONFIGURATION.md) | All settings and their defaults |
| [Usage](https://github.com/Neluxx/air2mqtt/blob/main/docs/USAGE.md) | Operating the service, MQTT topics and troubleshooting |
| [Development](https://github.com/Neluxx/air2mqtt/blob/main/docs/DEVELOPMENT.md) | Setup, tests, conventions and releasing |
| [Changelog](https://github.com/Neluxx/air2mqtt/blob/main/CHANGELOG.md) | Changes in each release |
