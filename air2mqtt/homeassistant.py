"""Home Assistant MQTT discovery (device-based, HA 2024.11+)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from air2mqtt import __version__
from air2mqtt.metrics import Metric

REPOSITORY_URL = "https://github.com/Neluxx/air2mqtt"


@dataclass(frozen=True, slots=True)
class Topics:
    """All MQTT topics used by one node."""

    base_topic: str
    discovery_prefix: str
    device_id: str

    @property
    def root(self) -> str:
        return f"{self.base_topic}/{self.device_id}"

    @property
    def availability(self) -> str:
        return f"{self.root}/availability"

    @property
    def discovery(self) -> str:
        return f"{self.discovery_prefix}/device/{self.device_id}/config"

    @property
    def homeassistant_status(self) -> str:
        return f"{self.discovery_prefix}/status"

    def state(self, metric: Metric) -> str:
        return f"{self.root}/{metric.key}"


def build_discovery_payload(
    topics: Topics,
    device_name: str,
    metrics: Iterable[Metric],
    expire_after: int,
) -> dict[str, Any]:
    """Describe the device and one sensor entity per metric for Home Assistant."""
    return {
        "device": {
            "identifiers": [topics.device_id],
            "name": device_name,
            "model": "Air2MQTT",
            "sw_version": __version__,
        },
        "origin": {
            "name": "air2mqtt",
            "sw_version": __version__,
            "support_url": REPOSITORY_URL,
        },
        "availability_topic": topics.availability,
        "qos": 1,
        "components": {
            _unique_id(topics, metric): _sensor_component(topics, metric, expire_after)
            for metric in metrics
        },
    }


def _sensor_component(topics: Topics, metric: Metric, expire_after: int) -> dict[str, Any]:
    return {
        "platform": "sensor",
        "unique_id": _unique_id(topics, metric),
        "name": metric.name,
        "device_class": metric.device_class,
        "state_class": "measurement",
        "unit_of_measurement": metric.unit,
        "suggested_display_precision": metric.precision,
        "state_topic": topics.state(metric),
        "expire_after": expire_after,
    }


def _unique_id(topics: Topics, metric: Metric) -> str:
    return f"{topics.device_id}_{metric.key}"
