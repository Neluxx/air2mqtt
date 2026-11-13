# Configuration

air2mqtt is configured entirely through environment variables. It has no
command-line options.

On startup, air2mqtt looks for a `.env` file in the current working directory, or in
the nearest parent directory that has one. For the systemd service that is
`/opt/air2mqtt/.env`. Variables that are already set in the environment take
precedence over the `.env` file.

A commented template is available as [`.env.example`](../.env.example).

## Options

| Variable              | Default          | Description                                                |
|-----------------------|------------------|------------------------------------------------------------|
| `MQTT_HOST`           | *(required)*     | Hostname or IP of the MQTT broker                          |
| `MQTT_PORT`           | `1883`           | Broker port (usually `8883` with TLS)                      |
| `MQTT_USERNAME`       | *(empty)*        | MQTT user; leave empty for anonymous access                |
| `MQTT_PASSWORD`       | *(empty)*        | MQTT password                                              |
| `MQTT_TLS`            | `false`          | Connect via TLS, verified against the system CA certificates |
| `MQTT_KEEPALIVE`      | `60`             | MQTT keepalive in seconds                                  |
| `MQTT_BASE_TOPIC`     | `air2mqtt`       | Prefix for state and availability topics                   |
| `HA_DISCOVERY_PREFIX` | `homeassistant`  | Home Assistant discovery prefix                            |
| `DEVICE_ID`           | hostname         | Stable, unique ID of this node                             |
| `DEVICE_NAME`         | `Air2MQTT`       | Device name shown in Home Assistant                        |
| `READ_INTERVAL`       | `60`             | Seconds between measurements (min. 5)                      |
| `TEMPERATURE_OFFSET`  | `0`              | BME680 temperature correction in °C (−10 to 10)            |
| `MHZ19_PORT`          | `/dev/serial0`   | UART port of the MH-Z19                                    |
| `LOG_LEVEL`           | `INFO`           | `DEBUG`, `INFO`, `WARNING` or `ERROR`                      |

Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off` and `1`/`0`.
If a value is invalid, air2mqtt exits at startup with a `Configuration error: …` message.

## Notes

### Device ID

`DEVICE_ID` appears in the MQTT topics and in the unique IDs of the Home Assistant
entities (see [MQTT](MQTT.md)). It is normalised to lowercase. Any character other than
`a-z`, `0-9`, `_` and `-` is replaced by `_`, so `Living Room` becomes `living_room`.

Keep the ID stable: changing it creates a new device in Home Assistant. When running
several nodes, give each one a unique ID such as `livingroom` or `bedroom`.

### Discovery prefix

`HA_DISCOVERY_PREFIX` must match the discovery prefix configured in the Home Assistant
MQTT integration. The default `homeassistant` is correct unless you changed it there.

### Read interval and expiry

Each sensor entity expires (shows as `unavailable`) when no new value arrives within
three read intervals, so after 3 minutes with the default `READ_INTERVAL=60`.

### Calibrating the temperature

Heat from the Pi can make the BME680 read too high. Compare it with a reference
thermometer and set `TEMPERATURE_OFFSET` to the difference, e.g. `-1.5`.
The offset is applied before the humidity is calculated, so the relative humidity is
corrected as well.
