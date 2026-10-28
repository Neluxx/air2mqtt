# air2mqtt

Reads a **BME680** (temperature, humidity, pressure) and an **MH-Z19** (CO₂)
sensor on a Raspberry Pi and publishes the values to **Home Assistant via MQTT**.

- Entities appear automatically through **MQTT discovery** – no YAML needed.
- Runs as a long-lived **systemd service** with automatic MQTT reconnects.
- Availability via MQTT **Last Will**: the device shows as unavailable when the node goes offline.
- Stale values expire automatically if a sensor stops reporting.
- If one sensor is missing or fails, the other keeps working.

Requires Home Assistant **2024.11 or newer** (device-based MQTT discovery).

---

## Hardware wiring

### BME680 → Raspberry Pi (I²C)

| BME680 pin | Pi GPIO header         |
|------------|------------------------|
| VCC        | Pin 1  (3.3 V)         |
| GND        | Pin 6  (GND)           |
| SDA        | Pin 3  (GPIO 2 / SDA1) |
| SCL        | Pin 5  (GPIO 3 / SCL1) |

Verify: `sudo i2cdetect -y 1` → should show address `0x76` or `0x77`.

### MH-Z19 → Raspberry Pi (UART)

| MH-Z19 pin | Pi GPIO header          |
|------------|-------------------------|
| Vin (5 V)  | Pin 2  (5 V)            |
| GND        | Pin 14 (GND)            |
| TXD        | Pin 10 (GPIO 15 / RXD)  |
| RXD        | Pin 8  (GPIO 14 / TXD)  |

MH-Z19 TX → Pi RX and MH-Z19 RX → Pi TX (cross-over).

---

## Home Assistant preparation

1. Install the **Mosquitto broker** add-on (or use any other MQTT broker).
2. Add the **MQTT** integration (Settings → Devices & services).
3. Create a dedicated Home Assistant user for the node (Settings → People → Users)
   and use its credentials as `MQTT_USERNAME` / `MQTT_PASSWORD`.

---

## Installation on the Raspberry Pi

### 1. Enable I²C and UART

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → Serial Port → login shell: No, serial hardware: Yes
sudo usermod -aG i2c,dialout $USER   # log out and back in afterwards
sudo reboot
```

### 2. Clone and install

```bash
sudo apt install python3-venv git i2c-tools
sudo git clone https://github.com/Neluxx/air2mqtt.git /opt/air2mqtt
sudo chown -R $USER:$USER /opt/air2mqtt

cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install .
```

### 3. Configure

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

### 4. Test manually

```bash
.venv/bin/air2mqtt
```

The device should now appear in Home Assistant under
Settings → Devices & services → MQTT. Stop with `Ctrl+C`.

### 5. Run as a service

```bash
sudo cp deploy/air2mqtt.service /etc/systemd/system/
sudo nano /etc/systemd/system/air2mqtt.service   # adjust User= if needed
sudo systemctl daemon-reload
sudo systemctl enable --now air2mqtt
```

Logs: `journalctl -u air2mqtt -f`

### Updating

```bash
cd /opt/air2mqtt
git pull
.venv/bin/pip install .
sudo systemctl restart air2mqtt
```

---

## Configuration

All settings are environment variables, read from `/opt/air2mqtt/.env`.

| Variable              | Default          | Description                                        |
|-----------------------|------------------|----------------------------------------------------|
| `MQTT_HOST`           | *(required)*     | Hostname or IP of the MQTT broker                  |
| `MQTT_PORT`           | `1883`           | Broker port (usually `8883` with TLS)              |
| `MQTT_USERNAME`       | *(empty)*        | MQTT user                                          |
| `MQTT_PASSWORD`       | *(empty)*        | MQTT password                                      |
| `MQTT_TLS`            | `false`          | Connect via TLS using the system CA certificates   |
| `MQTT_KEEPALIVE`      | `60`             | MQTT keepalive in seconds                          |
| `MQTT_BASE_TOPIC`     | `air2mqtt`       | Prefix for state and availability topics           |
| `HA_DISCOVERY_PREFIX` | `homeassistant`  | Home Assistant discovery prefix                    |
| `DEVICE_ID`           | hostname         | Stable, unique ID of this node                     |
| `DEVICE_NAME`         | `Air2MQTT`       | Device name shown in Home Assistant                |
| `READ_INTERVAL`       | `60`             | Seconds between measurements (min. 5)              |
| `MHZ19_PORT`          | `/dev/serial0`   | UART port of the MH-Z19                            |
| `LOG_LEVEL`           | `INFO`           | `DEBUG`, `INFO`, `WARNING` or `ERROR`              |

---

## MQTT topics

With `DEVICE_ID=livingroom`:

| Topic                                         | Payload                        | Retained |
|-----------------------------------------------|--------------------------------|----------|
| `homeassistant/device/livingroom/config`      | Discovery JSON                 | yes      |
| `air2mqtt/livingroom/availability`            | `online` / `offline`           | yes      |
| `air2mqtt/livingroom/temperature`             | `21.4` (°C)                    | yes      |
| `air2mqtt/livingroom/humidity`                | `48.1` (%)                     | yes      |
| `air2mqtt/livingroom/pressure`                | `1013.2` (hPa)                 | yes      |
| `air2mqtt/livingroom/carbon_dioxide`          | `812` (ppm)                    | yes      |

The node listens on `homeassistant/status` and re-publishes its discovery
config whenever Home Assistant restarts.

---

## Project layout

```
air2mqtt/
├── pyproject.toml
├── .env.example
├── deploy/
│   └── air2mqtt.service      # systemd unit
├── air2mqtt/
│   ├── __main__.py           # entry point, wiring, signal handling
│   ├── app.py                # measurement loop
│   ├── config.py             # settings from environment
│   ├── metrics.py            # measured quantities (unit, device class, precision)
│   ├── homeassistant.py      # topics and discovery payload
│   ├── mqtt_client.py        # paho-mqtt wrapper (LWT, reconnects)
│   └── sensors/
│       ├── base.py           # Sensor protocol and SensorError
│       ├── bme680.py         # BME680 driver wrapper
│       └── mhz19.py          # MH-Z19 UART protocol
└── tests/
```

---

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `Skipping BME680` | `sudo i2cdetect -y 1` – is the sensor detected? Is I²C enabled? |
| `Cannot open MH-Z19 serial port` | `ls -l /dev/serial0` – does the port exist? Reboot after enabling UART. |
| `Permission denied` on I²C / UART | `groups` – the service user needs `i2c` and `dialout`. |
| `MQTT connection refused` | Check `MQTT_HOST`, `MQTT_USERNAME` and `MQTT_PASSWORD`. |
| Device not visible in HA | Is the MQTT integration set up and the discovery prefix correct? |
| CO₂ values look wrong after power-up | The MH-Z19 needs about 3 minutes to warm up. |
