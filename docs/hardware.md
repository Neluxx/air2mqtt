# Hardware

air2mqtt reads two sensors connected to a Raspberry Pi:

| Sensor  | Measures                           | Interface |
|---------|------------------------------------|-----------|
| BME680  | Temperature, humidity, pressure    | I²C       |
| MH-Z19  | CO₂ concentration                  | UART      |

You can use both sensors or just one of them. Sensors that can't be found at startup
are skipped, and the device in Home Assistant only gets entities for the sensors that were found.

> The BME680's gas sensor (VOC / IAQ) is not used. Its heater would distort the
> temperature reading.

## Wiring

### BME680 → Raspberry Pi (I²C)

| BME680 pin | Pi GPIO header         |
|------------|------------------------|
| VCC        | Pin 1  (3.3 V)         |
| GND        | Pin 6  (GND)           |
| SDA        | Pin 3  (GPIO 2 / SDA1) |
| SCL        | Pin 5  (GPIO 3 / SCL1) |

Both I²C addresses of the BME680 (`0x76` and `0x77`) are detected automatically.

Heat from the Pi can warm up the BME680. Mount it a few centimetres away from the
board, or compensate with [`TEMPERATURE_OFFSET`](CONFIGURATION.md#calibrating-the-temperature).

### MH-Z19 → Raspberry Pi (UART)

| MH-Z19 pin | Pi GPIO header          |
|------------|-------------------------|
| Vin (5 V)  | Pin 2  (5 V)            |
| GND        | Pin 14 (GND)            |
| TXD        | Pin 10 (GPIO 15 / RXD)  |
| RXD        | Pin 8  (GPIO 14 / TXD)  |

The data lines are crossed over: MH-Z19 TX → Pi RX and MH-Z19 RX → Pi TX.

The MH-Z19 needs about 3 minutes to warm up after power-on. CO₂ readings taken
during that time are not reliable.

## Enable I²C and UART

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → Serial Port → login shell: No, serial hardware: Yes
sudo usermod -aG i2c,dialout $USER
sudo reboot
```

The user that runs air2mqtt needs to be in the `i2c` and `dialout` groups. Without them,
reading the sensors fails with `Permission denied`.

## Verify

```bash
sudo apt install i2c-tools
i2cdetect -y 1        # BME680: should show 0x76 or 0x77
ls -l /dev/serial0    # MH-Z19: should link to ttyS0 or ttyAMA0
```

---

Next: [Installation](INSTALLATION.md)
