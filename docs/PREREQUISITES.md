# Prerequisites

Complete these steps before you [install](INSTALLATION.md) air2mqtt.

## Raspberry Pi

- Raspberry Pi OS Bookworm or newer, or another Linux distribution
- Python 3.11 or newer (check with `python3 --version`)

## Sensors

| Sensor | Measures | Interface |
| --- | --- | --- |
| BME680 | Temperature, humidity, pressure | I²C |
| MH-Z19 | CO₂ | UART |

You can use one or both sensors. A sensor that isn't found at startup is skipped, and Home Assistant only gets entities for the sensors that were found. The BME680's gas sensor (VOC/IAQ) isn't used, because its heater would distort the temperature reading.

### Wiring the BME680 (I²C)

| BME680 | Raspberry Pi |
| --- | --- |
| VCC | Pin 1 (3.3 V) |
| GND | Pin 6 (GND) |
| SDA | Pin 3 (GPIO 2) |
| SCL | Pin 5 (GPIO 3) |

Both I²C addresses (`0x76` and `0x77`) are detected automatically. Mount the sensor a few centimetres away from the Pi, because the Pi's heat makes it read too high. You can also correct this with [`TEMPERATURE_OFFSET`](CONFIGURATION.md#calibrating-the-temperature).

### Wiring the MH-Z19 (UART)

| MH-Z19 | Raspberry Pi |
| --- | --- |
| Vin | Pin 2 (5 V) |
| GND | Pin 14 (GND) |
| TXD | Pin 10 (GPIO 15 / RXD) |
| RXD | Pin 8 (GPIO 14 / TXD) |

TX and RX are crossed. The sensor needs about 3 minutes to warm up after power-on, and readings taken during that time aren't reliable.

### Enabling I²C and UART

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → Serial Port → login shell: No, serial hardware: Yes
sudo usermod -aG i2c,dialout $USER
sudo reboot
```

The user that runs air2mqtt must be in the `i2c` and `dialout` groups, otherwise reading the sensors fails with `Permission denied`.

To check that the sensors are detected:

```bash
sudo apt install i2c-tools
i2cdetect -y 1        # BME680: shows 0x76 or 0x77
ls -l /dev/serial0    # MH-Z19: links to ttyS0 or ttyAMA0
```

## Home Assistant and MQTT

1. **Home Assistant 2024.11 or newer.** Older versions don't support the device-based MQTT discovery that air2mqtt uses.
2. **An MQTT broker with the [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) set up.** The easiest option is the Mosquitto broker add-on, but any MQTT broker works.
3. **Broker credentials.** With the Mosquitto add-on, any Home Assistant user can log in. Creating a dedicated user (e.g. `air2mqtt`) under **Settings → People → Users** is recommended.

No YAML configuration is needed in Home Assistant.
