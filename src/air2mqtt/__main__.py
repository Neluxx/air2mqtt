"""Entry point: ``air2mqtt`` or ``python -m air2mqtt``."""

from __future__ import annotations

import logging
import os
import signal
import sys
import threading
from collections.abc import Sequence
from importlib.metadata import version

from dotenv import find_dotenv, load_dotenv

from air2mqtt.app import Air2Mqtt
from air2mqtt.config import ConfigError, Settings
from air2mqtt.homeassistant import Topics
from air2mqtt.mqtt_client import MqttClient
from air2mqtt.sensors import Sensor, create_sensors

log = logging.getLogger("air2mqtt")

EXIT_OK = 0
EXIT_NO_SENSORS = 1
EXIT_CONFIG_ERROR = 2


def main() -> int:
    load_dotenv(find_dotenv(usecwd=True))
    try:
        settings = Settings.from_env(os.environ)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return EXIT_CONFIG_ERROR

    _configure_logging(settings.log_level)
    sw_version = version("air2mqtt")
    log.info("Starting air2mqtt %s as device '%s'.", sw_version, settings.device_id)

    sensors = create_sensors(
        temperature_offset=settings.temperature_offset,
        mhz19_port=settings.mhz19_port,
    )
    if not sensors:
        log.critical("No sensor could be initialised - exiting.")
        return EXIT_NO_SENSORS

    node = _create_node(settings, sensors, sw_version)
    node.run(_stop_event_on_signals())
    log.info("Stopped.")
    return EXIT_OK


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(levelname)-8s %(name)s: %(message)s")


def _create_node(settings: Settings, sensors: Sequence[Sensor], sw_version: str) -> Air2Mqtt:
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
    return Air2Mqtt(settings, sensors, mqtt, topics, sw_version)


def _stop_event_on_signals() -> threading.Event:
    """Return an event that is set on Ctrl+C or when systemd stops the service."""
    stop_event = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop_event.set())
    return stop_event


if __name__ == "__main__":
    sys.exit(main())
