"""Common interface for all sensors."""

from __future__ import annotations

from typing import Protocol

from air2mqtt.metrics import Metric, Reading


class SensorError(RuntimeError):
    """Raised whenever a sensor cannot be initialised or read."""


class Sensor(Protocol):
    name: str
    metrics: tuple[Metric, ...]

    def read(self) -> Reading:
        """Return the current values. Raises SensorError on failure."""
        ...

    def close(self) -> None:
        """Release any hardware resources."""
        ...
