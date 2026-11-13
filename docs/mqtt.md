# MQTT topics and behaviour

This page describes what air2mqtt sends to the broker. You only need it if you want
to use the data outside of Home Assistant's automatic discovery, or if you are debugging.

## Topics

With `DEVICE_ID=livingroom` and the default prefixes:

| Topic                                         | Payload                        | QoS | Retained |
|-----------------------------------------------|--------------------------------|-----|----------|
| `homeassistant/device/livingroom/config`      | Discovery JSON                 | 1   | yes      |
| `air2mqtt/livingroom/availability`            | `online` / `offline`           | 1   | yes      |
| `air2mqtt/livingroom/temperature`             | `21.4` (°C)                    | 0   | no       |
| `air2mqtt/livingroom/humidity`                | `48.1` (%)                     | 0   | no       |
| `air2mqtt/livingroom/pressure`                | `1013.2` (hPa)                 | 0   | no       |
| `air2mqtt/livingroom/carbon_dioxide`          | `812` (ppm)                    | 0   | no       |

The prefixes can be changed with `HA_DISCOVERY_PREFIX` and `MQTT_BASE_TOPIC` (see
[Configuration](CONFIGURATION.md)).

To watch the live traffic:

```bash
mosquitto_sub -h <broker> -u <user> -P <password> -v -t 'air2mqtt/#'
```

## Discovery

air2mqtt uses Home Assistant's device-based MQTT discovery (Home Assistant 2024.11+).
A single retained config message describes the device and one sensor entity per
measured value. Entities are only created for sensors that were found at startup.

The discovery config is published after every (re)connect to the broker. air2mqtt also
listens on `homeassistant/status` and publishes it again whenever Home Assistant
comes back online after a restart.

## Availability

- After connecting, the node publishes `online` to its availability topic.
- On a clean shutdown (`Ctrl+C`, `systemctl stop`), it publishes `offline`.
- If the node disappears unexpectedly (power loss, network failure), the broker
  publishes `offline` on its behalf. This is configured as the MQTT **Last Will**.

While the node is `offline`, all of its entities show as unavailable in Home Assistant.

Individual values also expire: if a sensor stops delivering values, its entities
turn `unavailable` after three missed read intervals, even while the node itself is online.

## When the broker is unreachable

The client reconnects automatically, waiting up to 2 minutes between attempts.
Measurements taken while the broker is unreachable are logged and dropped, not
buffered. Home Assistant timestamps every state on arrival, so values delivered late
would appear at the wrong time. Instead, the history shows a gap.

Measurement values are not retained either. Home Assistant restores the last state
itself, and a replayed retained value could bring back a sensor that has already expired.
