# Configuration

air2mqtt is configured entirely through environment variables. It has no command-line options.

At startup, air2mqtt loads a `.env` file from the current working directory, or from the nearest parent directory that has one. For the systemd service, this is `/opt/air2mqtt/.env`. Variables already set in the environment take precedence over `.env`. A commented template is available in [`.env.example`](../.env.example).

## Settings

| Variable | Default | Description |
| --- | --- | --- |
| `MQTT_HOST` | *(required)* | Hostname or IP of the MQTT broker |
| `MQTT_PORT` | `1883` | Broker port (usually `8883` with TLS) |
| `MQTT_USERNAME` | *(empty)* | MQTT user. Leave empty for anonymous access. |
| `MQTT_PASSWORD` | *(empty)* | MQTT password |
| `MQTT_TLS` | `false` | Connect via TLS, verified against the system CA certificates |
| `MQTT_KEEPALIVE` | `60` | MQTT keepalive in seconds |
| `MQTT_BASE_TOPIC` | `air2mqtt` | Prefix for state and availability topics |
| `HA_DISCOVERY_PREFIX` | `homeassistant` | Home Assistant discovery prefix |
| `DEVICE_ID` | hostname | Stable, unique ID of this device |
| `DEVICE_NAME` | `Air2MQTT` | Device name shown in Home Assistant |
| `READ_INTERVAL` | `60` | Seconds between measurements (minimum 5) |
| `TEMPERATURE_OFFSET` | `0` | BME680 temperature correction in °C (−10 to 10). Humidity is corrected too. |
| `MHZ19_PORT` | `/dev/serial0` | UART port of the MH-Z19 |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR` |

Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off` and `1`/`0`. If a value is missing or invalid, air2mqtt exits at startup with a `Configuration error: …` message that names the setting.

## Notes

### Device ID

`DEVICE_ID` is used in the MQTT topics and in the entity IDs in Home Assistant. It is converted to lowercase, and every character other than `a-z`, `0-9`, `_` and `-` becomes `_`. For example, `Living Room` becomes `living_room`.

Keep the ID stable: changing it creates a new device in Home Assistant. If you run air2mqtt on several devices, give each one a unique ID, such as `livingroom` or `bedroom`.

### Discovery prefix

`HA_DISCOVERY_PREFIX` must match the discovery prefix of the MQTT integration in Home Assistant. Keep the default unless you changed it there.

### Read interval

A sensor entity shows as unavailable if no new value arrives within three read intervals. With the default `READ_INTERVAL=60`, that is 3 minutes.

### Calibrating the temperature

The Pi's heat can make the BME680 read too high. Compare the reading with a reference thermometer and set `TEMPERATURE_OFFSET` to the difference, e.g. `-1.5`. The offset is applied before humidity is calculated, so relative humidity is corrected as well.
