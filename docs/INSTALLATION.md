# Installation

This guide installs air2mqtt into `/opt/air2mqtt` and runs it as a systemd service. Make sure you have completed the [prerequisites](PREREQUISITES.md) first.

## 1. Install the package

```bash
sudo apt install python3-venv
sudo mkdir /opt/air2mqtt
sudo chown $USER:$USER /opt/air2mqtt

cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install air2mqtt
```

Always use a virtual environment. Raspberry Pi OS refuses `pip install` into the system Python (`externally-managed-environment`).

## 2. Configure

Create `/opt/air2mqtt/.env`:

```ini
# Required
MQTT_HOST=homeassistant.local
MQTT_USERNAME=air2mqtt
MQTT_PASSWORD=change-me

# Optional
#DEVICE_ID=livingroom
#DEVICE_NAME=Living Room
#READ_INTERVAL=60
#TEMPERATURE_OFFSET=0
```

The file contains your password, so make it readable only by you:

```bash
chmod 600 /opt/air2mqtt/.env
```

All settings are described in [Configuration](CONFIGURATION.md).

## 3. Test manually

```bash
cd /opt/air2mqtt
.venv/bin/air2mqtt
```

You should see output like this:

```
INFO     air2mqtt: Starting air2mqtt 0.1.0 as device 'raspberrypi'.
INFO     air2mqtt.sensors.bme680: BME680 initialised.
INFO     air2mqtt.sensors.mhz19: MH-Z19 initialised on /dev/serial0.
INFO     air2mqtt.mqtt_client: Connected to MQTT broker.
INFO     air2mqtt.app: Published Home Assistant discovery to homeassistant/device/raspberrypi/config.
INFO     air2mqtt.app: BME680: temperature=21.4 °C, humidity=48.1 %, pressure=1013.2 hPa
INFO     air2mqtt.app: MH-Z19: carbon_dioxide=812 ppm
```

The device now appears in Home Assistant under **Settings → Devices & services → MQTT**. Stop air2mqtt with `Ctrl+C`. If something goes wrong, see [Troubleshooting](USAGE.md#troubleshooting).

## 4. Run as a service

Create `/etc/systemd/system/air2mqtt.service`:

```ini
[Unit]
Description=air2mqtt – indoor air sensors to Home Assistant via MQTT
Documentation=https://github.com/Neluxx/air2mqtt
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
# Adjust to the user that owns /opt/air2mqtt (must be in the i2c and dialout groups).
User=pi
WorkingDirectory=/opt/air2mqtt
ExecStart=/opt/air2mqtt/.venv/bin/air2mqtt
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=10
# Exit code 2 = configuration error; restarting will not fix it.
RestartPreventExitStatus=2

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

- Set `User=` to the user that owns `/opt/air2mqtt` (run `whoami` to see it).
- If you installed somewhere else, adjust `WorkingDirectory=` and `ExecStart=` to match. If that location is under `/home`, also set `ProtectHome=read-only`, otherwise the service can't read `.env`.
- On a configuration error the service stops instead of restarting. Fix `.env`, then run `sudo systemctl restart air2mqtt`.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now air2mqtt
```

## Updating

```bash
/opt/air2mqtt/.venv/bin/pip install --upgrade air2mqtt
sudo systemctl restart air2mqtt
```

See the [changelog](../CHANGELOG.md) for what changed.

## Uninstalling

```bash
sudo systemctl disable --now air2mqtt
sudo rm /etc/systemd/system/air2mqtt.service
sudo systemctl daemon-reload
sudo rm -rf /opt/air2mqtt
```

Then delete the device in Home Assistant under **Settings → Devices & services → MQTT**. If the device comes back afterwards, clear its retained discovery config on the broker:

```bash
mosquitto_pub -h <broker> -u <user> -P <password> -r -n \
  -t homeassistant/device/<DEVICE_ID>/config
```

## Installing from source

To run the latest unreleased version, install from a Git clone instead of PyPI:

```bash
sudo git clone https://github.com/Neluxx/air2mqtt.git /opt/air2mqtt
sudo chown -R $USER:$USER /opt/air2mqtt
cd /opt/air2mqtt
python3 -m venv .venv
.venv/bin/pip install .
```

To update, run `git pull` and then `.venv/bin/pip install .` again. The clone already contains `.env.example` and `deploy/air2mqtt.service` as templates.
