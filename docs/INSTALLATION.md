# Installation

This guide installs air2mqtt on a Raspberry Pi into `/opt/air2mqtt` and runs it as a
systemd service.

## Prerequisites

### Raspberry Pi

- Raspberry Pi OS **Bookworm or newer**, or any other Linux distribution with
  **Python 3.11 or newer**. Check with `python3 --version`.
- The sensors are wired up and I²C/UART are enabled, as described in [Hardware](HARDWARE.md).

### Home Assistant and MQTT broker

air2mqtt publishes its readings to Home Assistant over MQTT. You need:

1. **Home Assistant 2024.11 or newer.** Older versions don't support the device-based
   MQTT discovery that air2mqtt uses. See the official
   [installation guide](https://www.home-assistant.io/installation/).
2. **An MQTT broker with the MQTT integration set up.** The easiest option is the
   Mosquitto broker add-on. See the
   [MQTT integration documentation](https://www.home-assistant.io/integrations/mqtt/).
   Any other MQTT broker works as well.
3. **Broker credentials.** With the Mosquitto add-on, any Home Assistant user can log in.
   Creating a dedicated user (e.g. `air2mqtt`) under **Settings → People → Users** is
   recommended.

You don't need any YAML configuration in Home Assistant. The device and its
entities are created automatically.

## 1. Install the package

Create a virtual environment and install air2mqtt from [PyPI](https://pypi.org/project/air2mqtt/):

```bash
sudo apt install python3-venv
sudo mkdir /opt/air2mqtt
sudo chown $USER:$USER /opt/air2mqtt

cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install air2mqtt
```

> Use a virtual environment, as shown above. Raspberry Pi OS refuses `pip install`
> into the system Python (`externally-managed-environment`).

## 2. Configure

air2mqtt is configured through a `.env` file in its working directory. Create it:

```bash
cd /opt/air2mqtt
nano .env
```

Paste the following and fill in your broker details:

```ini
# Required
MQTT_HOST=homeassistant.local
MQTT_USERNAME=air2mqtt
MQTT_PASSWORD=change-me

# Optional – uncomment to change the defaults
#DEVICE_ID=livingroom
#DEVICE_NAME=Living Room
#READ_INTERVAL=60
#TEMPERATURE_OFFSET=0
```

Save with `Ctrl+O`, `Enter` and exit with `Ctrl+X`. Then make the file readable only by you,
because it contains your password:

```bash
chmod 600 .env
```

All options are described in [Configuration](CONFIGURATION.md).

## 3. Test manually

```bash
cd /opt/air2mqtt
.venv/bin/air2mqtt
```

Expected output:

```
INFO     air2mqtt: Starting air2mqtt 0.1.0 as device 'raspberrypi'.
INFO     air2mqtt.sensors.bme680: BME680 initialised.
INFO     air2mqtt.sensors.mhz19: MH-Z19 initialised on /dev/serial0.
INFO     air2mqtt.mqtt_client: Connecting to MQTT broker homeassistant.local:1883 …
INFO     air2mqtt.mqtt_client: Connected to MQTT broker.
INFO     air2mqtt.app: Published Home Assistant discovery to homeassistant/device/raspberrypi/config.
INFO     air2mqtt.app: BME680: temperature=21.4 °C, humidity=48.1 %, pressure=1013.2 hPa
INFO     air2mqtt.app: MH-Z19: carbon_dioxide=812 ppm
```

The device should now appear in Home Assistant under
**Settings → Devices & services → MQTT**. Stop with `Ctrl+C`.

If something doesn't work, see [Troubleshooting](TROUBLESHOOTING.md).

## 4. Run as a service

Create the systemd unit:

```bash
sudo nano /etc/systemd/system/air2mqtt.service
```

Paste the following and replace `pi` in `User=` with the user that owns `/opt/air2mqtt`
(`whoami` shows your user name). That user needs to be in the `i2c` and `dialout` groups.

```ini
[Unit]
Description=air2mqtt – indoor air sensors to Home Assistant via MQTT
Documentation=https://github.com/Neluxx/air2mqtt
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/air2mqtt
ExecStart=/opt/air2mqtt/.venv/bin/air2mqtt
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=10

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
```

If you installed somewhere other than `/opt/air2mqtt`, adjust `WorkingDirectory=` and
`ExecStart=` as well. Under `/home`, also change `ProtectHome=true` to
`ProtectHome=read-only`, otherwise the service can't read `.env`.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now air2mqtt
```

Check the status and follow the logs:

```bash
systemctl status air2mqtt
journalctl -u air2mqtt -f
```

The service restarts automatically after a crash. On a clean shutdown it marks the
device as offline in Home Assistant.

## Updating

```bash
/opt/air2mqtt/.venv/bin/pip install --upgrade air2mqtt
sudo systemctl restart air2mqtt
```

See the [changelog](../CHANGELOG.md) for what changed between releases.

## Uninstalling

```bash
sudo systemctl disable --now air2mqtt
sudo rm /etc/systemd/system/air2mqtt.service
sudo systemctl daemon-reload
sudo rm -rf /opt/air2mqtt
```

Then delete the device in Home Assistant under **Settings → Devices & services → MQTT**.
Its discovery config is retained on the broker. If the device comes back after
deleting it, clear the config by publishing an empty retained message:

```bash
mosquitto_pub -h <broker> -u <user> -P <password> -r -n \
  -t homeassistant/device/<DEVICE_ID>/config
```

## Installing from source

To run the latest unreleased version, install from a Git clone instead of PyPI:

```bash
sudo apt install git
sudo git clone https://github.com/Neluxx/air2mqtt.git /opt/air2mqtt
sudo chown -R $USER:$USER /opt/air2mqtt
cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install .
```

The clone already contains `.env.example` and `deploy/air2mqtt.service`, so you can copy
them instead of downloading them. To update, run `git pull` and `.venv/bin/pip install .`.
