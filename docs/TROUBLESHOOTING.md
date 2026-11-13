# Troubleshooting

Start with the logs:

```bash
journalctl -u air2mqtt -f
```

For more detail, set `LOG_LEVEL=DEBUG` in `.env` and restart the service.

## Startup

| Message | Cause / fix |
|---------|-------------|
| `Configuration error: …` | A setting is missing or invalid; the message names it. See [Configuration](CONFIGURATION.md). |
| `Skipping BME680: BME680 not found on I²C …` | `i2cdetect -y 1`: is the sensor detected at `0x76`/`0x77`? Is I²C enabled? Check the wiring. |
| `Skipping MH-Z19: Cannot open MH-Z19 serial port …` | `ls -l /dev/serial0`: does the port exist? Reboot after enabling UART. Check `MHZ19_PORT`. |
| `Permission denied` on I²C / UART | Run `groups`. The service user needs to be in `i2c` and `dialout`. Log in again after adding them. |
| `No sensor could be initialised - exiting.` | Neither sensor was found. Fix at least one of the issues above. |

## MQTT and Home Assistant

| Symptom | Cause / fix |
|---------|-------------|
| `MQTT connection refused: …` | The broker rejected the login. Check `MQTT_USERNAME` and `MQTT_PASSWORD`. |
| `MQTT broker not reachable yet, measuring anyway.` / `(not sent, MQTT broker unreachable)` | Check `MQTT_HOST`, `MQTT_PORT` and `MQTT_TLS`, and whether the broker is running and reachable from the Pi. |
| Device not visible in Home Assistant | Is the MQTT integration set up? Does `HA_DISCOVERY_PREFIX` match its discovery prefix? Is Home Assistant 2024.11 or newer? |
| Two devices after changing `DEVICE_ID` or hostname | Every ID creates its own device. Delete the old one in Home Assistant (see [Uninstalling](INSTALLATION.md#uninstalling)). |
| Entities show `unavailable` | The node is offline, or no value arrived for three read intervals. Check the logs for sensor read errors. |

## Readings

| Symptom | Cause / fix |
|---------|-------------|
| Temperature reads too high | Heat from the Pi warms the BME680. Compare with a reference thermometer and set `TEMPERATURE_OFFSET` (e.g. `-1.5`). |
| CO₂ values look wrong after power-up | The MH-Z19 needs about 3 minutes to warm up. |
| `MH-Z19 reported an implausible value` | The value is outside 300–10,000 ppm. It is still published. This is usually normal during warm-up. |
| `MH-Z19 sent 0 bytes, expected 9.` | No response from the sensor. Make sure TX/RX are crossed and the sensor has 5 V. |

Still stuck? [Open an issue](https://github.com/Neluxx/air2mqtt/issues) and include the log output.
