"""The main loop: read all sensors periodically and publish the values to MQTT."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Sequence

from air2mqtt.config import Settings
from air2mqtt.homeassistant import Topics, build_discovery_payload
from air2mqtt.mqtt_client import ONLINE, MqttClient
from air2mqtt.sensors import Sensor, SensorError

log = logging.getLogger(__name__)

# A value is marked unavailable in HA if no update arrives within this many intervals.
_EXPIRE_AFTER_INTERVALS = 3


class Air2Mqtt:
    def __init__(
        self,
        settings: Settings,
        sensors: Sequence[Sensor],
        mqtt: MqttClient,
        topics: Topics,
    ) -> None:
        self._settings = settings
        self._sensors = sensors
        self._mqtt = mqtt
        self._topics = topics

        self._mqtt.add_connect_handler(self._publish_discovery)
        self._mqtt.subscribe(topics.homeassistant_status, self._on_homeassistant_status)

    def run(self, stop_event: threading.Event) -> None:
        """Measure and publish until ``stop_event`` is set."""
        self._mqtt.start()
        try:
            while not stop_event.is_set():
                started = time.monotonic()
                self._measure_and_publish()
                elapsed = time.monotonic() - started
                stop_event.wait(max(0.0, self._settings.read_interval - elapsed))
        finally:
            self._mqtt.stop()
            for sensor in self._sensors:
                sensor.close()

    def _measure_and_publish(self) -> None:
        for sensor in self._sensors:
            try:
                reading = sensor.read()
            except SensorError as exc:
                log.error("%s: %s", sensor.name, exc)
                continue

            for metric, value in reading.items():
                self._mqtt.publish(self._topics.state(metric), metric.format(value), retain=True)

            log.info(
                "%s: %s",
                sensor.name,
                ", ".join(f"{m.key}={m.format(v)} {m.unit}" for m, v in reading.items()),
            )

    def _publish_discovery(self) -> None:
        payload = build_discovery_payload(
            topics=self._topics,
            device_name=self._settings.device_name,
            metrics=[metric for sensor in self._sensors for metric in sensor.metrics],
            expire_after=self._settings.read_interval * _EXPIRE_AFTER_INTERVALS,
        )
        self._mqtt.publish(self._topics.discovery, json.dumps(payload), retain=True)
        log.info("Published Home Assistant discovery to %s.", self._topics.discovery)

    def _on_homeassistant_status(self, payload: str) -> None:
        # Home Assistant announces "online" after a restart; re-announce ourselves.
        if payload == ONLINE:
            self._publish_discovery()
