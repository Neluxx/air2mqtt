"""Sensor drivers and a factory that skips sensors which fail to initialise."""

from __future__ import annotations

import logging
from collections.abc import Callable

from air2mqtt.sensors.base import Sensor, SensorError
from air2mqtt.sensors.bme680 import BME680Sensor
from air2mqtt.sensors.mhz19 import MHZ19Sensor

__all__ = ["Sensor", "SensorError", "create_sensors"]

log = logging.getLogger(__name__)


def create_sensors(*, temperature_offset: float, mhz19_port: str) -> list[Sensor]:
    """Initialise every known sensor; a missing sensor is logged, not fatal."""
    factories: dict[str, Callable[[], Sensor]] = {
        "BME680": lambda: BME680Sensor(temperature_offset),
        "MH-Z19": lambda: MHZ19Sensor(mhz19_port),
    }

    sensors: list[Sensor] = []
    for name, factory in factories.items():
        try:
            sensors.append(factory())
        except SensorError as exc:
            log.error("Skipping %s: %s", name, exc)
    return sensors
