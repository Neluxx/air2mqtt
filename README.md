# air2mqtt

[![CI](https://github.com/Neluxx/air2mqtt/actions/workflows/ci.yml/badge.svg)](https://github.com/Neluxx/air2mqtt/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/air2mqtt)](https://pypi.org/project/air2mqtt/)
[![Python](https://img.shields.io/pypi/pyversions/air2mqtt)](https://pypi.org/project/air2mqtt/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Neluxx/air2mqtt/blob/main/LICENSE)

**Indoor air quality for Home Assistant, from a Raspberry Pi.**

air2mqtt reads a **BME680** (temperature, humidity, pressure) and an **MH-Z19** (CO₂)
sensor on a Raspberry Pi and publishes the values to **Home Assistant via MQTT**.

```
BME680 ──I²C──┐
              ├── Raspberry Pi (air2mqtt) ──MQTT──> Broker ──> Home Assistant
MH-Z19 ──UART─┘
```

## Features

- **Zero configuration in Home Assistant** – entities appear automatically through MQTT discovery.
- **Runs unattended** as a systemd service with automatic MQTT reconnects.
- **Honest availability** – the device shows as unavailable when the node goes offline (MQTT Last Will),
  and stale values expire if a sensor stops reporting.
- **Fault tolerant** – if one sensor is missing or fails, the other keeps working.

## Requirements

- Raspberry Pi (or another Linux board) with Python 3.11 or newer
- BME680 and/or MH-Z19 sensor
- Home Assistant **2024.11 or newer** with an MQTT broker

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install air2mqtt
```

Create a `.env` file in the current directory with at least `MQTT_HOST`, `MQTT_USERNAME`
and `MQTT_PASSWORD`, then run `.venv/bin/air2mqtt`. The device appears in Home Assistant
automatically.

For a complete setup, follow the [installation guide][installation]. It covers
enabling I²C/UART and running air2mqtt as a service.

## Documentation

| Guide                                      | What you'll find                                                 |
|--------------------------------------------|------------------------------------------------------------------|
| [Hardware][hardware]                       | Wiring the sensors and enabling I²C/UART on the Pi               |
| [Installation][installation]               | Prerequisites, setup, systemd service, updating and uninstalling |
| [Configuration][configuration]             | All environment variables and their defaults                     |
| [MQTT][mqtt]                               | Topics, discovery, availability and offline behaviour            |
| [Troubleshooting][troubleshooting]         | Common error messages and how to fix them                        |
| [Development][development]                 | Running tests, linting and the project layout                    |

## Contributing

Bug reports and pull requests are welcome on [GitHub](https://github.com/Neluxx/air2mqtt/issues).
See the [development guide][development] to get started and the [changelog][changelog] for recent changes.

## License

[MIT](https://github.com/Neluxx/air2mqtt/blob/main/LICENSE)

<!-- Absolute links so they also work on PyPI. -->
[hardware]: https://github.com/Neluxx/air2mqtt/blob/main/docs/HARDWARE.md
[installation]: https://github.com/Neluxx/air2mqtt/blob/main/docs/INSTALLATION.md
[configuration]: https://github.com/Neluxx/air2mqtt/blob/main/docs/CONFIGURATION.md
[mqtt]: https://github.com/Neluxx/air2mqtt/blob/main/docs/MQTT.md
[troubleshooting]: https://github.com/Neluxx/air2mqtt/blob/main/docs/TROUBLESHOOTING.md
[development]: https://github.com/Neluxx/air2mqtt/blob/main/docs/DEVELOPMENT.md
[changelog]: https://github.com/Neluxx/air2mqtt/blob/main/CHANGELOG.md
