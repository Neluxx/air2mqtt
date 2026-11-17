# Usage

## Managing the service

| Command | Purpose |
| --- | --- |
| `systemctl status air2mqtt` | Show whether the service is running |
| `journalctl -u air2mqtt -f` | Follow the logs |
| `sudo systemctl restart air2mqtt` | Restart, e.g. after changing `.env` |
| `sudo systemctl stop air2mqtt` | Stop the service and mark the device offline |

The service restarts automatically after a crash. When it stops cleanly, the device shows as offline in Home Assistant.

## Home Assistant

air2mqtt creates one device with a sensor entity for each value it measures:

| Entity | Unit | Sensor |
| --- | --- | --- |
| Temperature | °C | BME680 |
| Humidity | % | BME680 |
| Pressure | hPa | BME680 |
| CO₂ | ppm | MH-Z19 |

Entities are created only for sensors that were found at startup. Entities show as unavailable if:

- the device is offline (clean shutdown, or detected by the broker after a power or network loss), or
- no new value has arrived for three read intervals.

## MQTT topics

These examples use `DEVICE_ID=livingroom` and the default prefixes:

| Topic | Payload | QoS | Retained |
| --- | --- | --- | --- |
| `homeassistant/device/livingroom/config` | Discovery JSON | 1 | yes |
| `air2mqtt/livingroom/availability` | `online` / `offline` | 1 | yes |
| `air2mqtt/livingroom/temperature` | `21.4` | 0 | no |
| `air2mqtt/livingroom/humidity` | `48.1` | 0 | no |
| `air2mqtt/livingroom/pressure` | `1013.2` | 0 | no |
| `air2mqtt/livingroom/carbon_dioxide` | `812` | 0 | no |

- **Discovery** is published after every connect to the broker, and again whenever Home Assistant reports `online` on `homeassistant/status` (for example after a restart).
- **If the broker is unreachable**, air2mqtt keeps retrying, waiting up to 2 minutes between attempts. Measurements taken in the meantime are dropped, not buffered, so the history shows a gap rather than values with the wrong timestamps.

To watch the messages live:

```bash
mosquitto_sub -h <broker> -u <user> -P <password> -v -t 'air2mqtt/#'
```

## Troubleshooting

For more detail, set `LOG_LEVEL=DEBUG` in `.env` and restart the service.

| Problem | Fix |
| --- | --- |
| `Configuration error: …` | A setting is missing or invalid. The message names it. See [Configuration](CONFIGURATION.md). |
| `Skipping BME680: BME680 not found on I²C …` | Check the wiring and that I²C is enabled. `i2cdetect -y 1` should show `0x76` or `0x77`. |
| `Skipping MH-Z19: Cannot open MH-Z19 serial port …` | Check that `/dev/serial0` exists (reboot after enabling UART) and that `MHZ19_PORT` is correct. |
| `Permission denied` on I²C or UART | Add the service user to the `i2c` and `dialout` groups, then log in again. |
| `No sensor could be initialised - exiting.` | Neither sensor was found. Fix at least one of the problems above. |
| `MQTT connection refused: …` | Check `MQTT_USERNAME` and `MQTT_PASSWORD`. |
| `MQTT broker not reachable yet …` or `(not sent, MQTT broker unreachable)` | Check `MQTT_HOST`, `MQTT_PORT` and `MQTT_TLS`, and make sure the Pi can reach the broker. |
| Device doesn't appear in Home Assistant | Check that the MQTT integration is set up, `HA_DISCOVERY_PREFIX` matches its discovery prefix, and Home Assistant is 2024.11 or newer. |
| Duplicate device after changing `DEVICE_ID` or the hostname | Delete the old device (see [Uninstalling](INSTALLATION.md#uninstalling)). |
| Temperature reads too high | Set `TEMPERATURE_OFFSET` (see [Configuration](CONFIGURATION.md#calibrating-the-temperature)). |
| CO₂ values are wrong after power-up, or `MH-Z19 reported an implausible value` | The MH-Z19 needs about 3 minutes to warm up. Readings outside 300–10,000 ppm are logged but still published. |
| `MH-Z19 sent 0 bytes, expected 9.` | The sensor isn't responding. Check that TX/RX are crossed and that it is powered with 5 V. |

Still stuck? [Open an issue](https://github.com/Neluxx/air2mqtt/issues) and include the log output.
