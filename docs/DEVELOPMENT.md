# Development

## Requirements

- [Python](https://www.python.org/) 3.11 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/Neluxx/air2mqtt.git
cd air2mqtt
uv sync
```

`uv sync` creates the virtual environment and installs the package together with its development dependencies.

## Tests and code style

```bash
uv run pytest          # tests
uv run ruff check      # linting
uv run ruff format     # formatting
```

CI runs `ruff check`, `ruff format --check` and `pytest` on Python 3.11–3.14 for every pull request and every push to `main`.

## Running locally

```bash
cp .env.example .env   # then set MQTT_HOST etc.
uv run air2mqtt
```

Without sensors attached, air2mqtt exits with `No sensor could be initialised`. To work on the MQTT and Home Assistant code without hardware, rely on the unit tests.

## Project structure

```
.
├── deploy/air2mqtt.service   # systemd unit
├── docs/                     # documentation
├── src/air2mqtt/
│   ├── __main__.py           # entry point and signal handling
│   ├── app.py                # measurement loop
│   ├── config.py             # settings from environment variables
│   ├── metrics.py            # measured values (unit, device class, precision)
│   ├── homeassistant.py      # topics and discovery payload
│   ├── mqtt_client.py        # paho-mqtt wrapper (last will, reconnects)
│   └── sensors/
│       ├── base.py           # Sensor protocol and SensorError
│       ├── bme680.py         # BME680 driver
│       └── mhz19.py          # MH-Z19 UART protocol
├── tests/
├── .env.example
├── CHANGELOG.md
└── pyproject.toml
```

## Keeping the docs in sync

- **New setting:** add it to `config.py`, `.env.example` and the table in [CONFIGURATION.md](CONFIGURATION.md).
- **Changed systemd unit:** update `deploy/air2mqtt.service` and the copy in [INSTALLATION.md](INSTALLATION.md#4-run-as-a-service).
- **New log message that users may see:** add it to [Troubleshooting](USAGE.md#troubleshooting) if users can act on it.

## Conventions

- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/): `<type>: <short description>`. Common types are `feat`, `fix`, `docs`, `refactor`, `chore` and `build`.
- **Changelog:** add every user-facing change to the `Unreleased` section of [CHANGELOG.md](../CHANGELOG.md), following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- **Versioning** follows [Semantic Versioning](https://semver.org/).

## Releasing

1. Update `version` in `pyproject.toml` and move the `Unreleased` entries in `CHANGELOG.md` to a new version section.
2. Commit, tag and push:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
3. The release workflow checks that the tag matches the package version, runs the tests, builds the package and publishes it to [TestPyPI](https://test.pypi.org/project/air2mqtt/).
4. Check the TestPyPI release, then approve the `pypi` deployment in the workflow run. The same files are then published to [PyPI](https://pypi.org/project/air2mqtt/) and attached to a new GitHub release.
