# Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
git clone https://github.com/Neluxx/air2mqtt.git
cd air2mqtt
uv sync
```

## Tests and linting

```bash
uv run pytest
uv run ruff check && uv run ruff format --check
```

CI runs the same checks on Python 3.11 – 3.14.

## Running locally

```bash
cp .env.example .env   # set MQTT_HOST etc.
uv run air2mqtt
```

Without the sensors attached, both are skipped and air2mqtt exits with
`No sensor could be initialised`. To work on the MQTT and Home Assistant parts
without hardware, use the unit tests.

## Project layout

```
air2mqtt/
├── pyproject.toml
├── .env.example
├── deploy/
│   └── air2mqtt.service      # systemd unit
├── docs/                     # documentation
├── src/
│   └── air2mqtt/
│       ├── __main__.py       # entry point, wiring, signal handling
│       ├── app.py            # measurement loop
│       ├── config.py         # settings from environment
│       ├── metrics.py        # measured quantities (unit, device class, precision)
│       ├── homeassistant.py  # topics and discovery payload
│       ├── mqtt_client.py    # paho-mqtt wrapper (LWT, reconnects)
│       └── sensors/
│           ├── base.py       # Sensor protocol and SensorError
│           ├── bme680.py     # BME680 driver wrapper
│           └── mhz19.py      # MH-Z19 UART protocol
└── tests/
```

`docs/INSTALLATION.md` contains a copy of the systemd unit and a short `.env` example.
When you change `deploy/air2mqtt.service` or add a setting, update it as well.

## Changelog

Notable changes are recorded in [CHANGELOG.md](../CHANGELOG.md) following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
