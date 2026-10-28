"""Entry point: ``air2mqtt`` or ``python -m air2mqtt``."""

from __future__ import annotations

import logging
import signal
import sys
import threading

from air2mqtt import __version__
from air2mqtt.app import Air2Mqtt
from air2mqtt.config import ConfigError, Settings
from air2mqtt.homeassistant import Topics
from air2mqtt.mqtt_client import MqttClient
from air2mqtt.sensors import create_sensors

log = logging.getLogger("air2mqtt")


def main() -> int:
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=settings.log_level,
        format="%(levelname)-8s %(name)s: %(message)s",
    )
    log.info("Starting air2mqtt %s as device '%s'.", __version__, settings.device_id)

    sensors = create_sensors(settings)
    if not sensors:
        log.critical("No sensor could be initialised - exiting.")
        return 1

    topics = Topics(
        base_topic=settings.base_topic,
        discovery_prefix=settings.discovery_prefix,
        device_id=settings.device_id,
    )
    mqtt = MqttClient(
        settings.mqtt,
        client_id=f"air2mqtt-{settings.device_id}",
        availability_topic=topics.availability,
    )
    node = Air2Mqtt(settings, sensors, mqtt, topics)

    stop_event = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop_event.set())

    node.run(stop_event)
    log.info("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
