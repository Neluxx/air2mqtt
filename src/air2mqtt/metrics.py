"""The physical quantities this node measures, described once and reused everywhere."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Metric:
    key: str
    name: str
    unit: str
    device_class: str
    precision: int

    def format(self, value: float) -> str:
        return f"{value:.{self.precision}f}"


TEMPERATURE = Metric("temperature", "Temperature", "°C", "temperature", precision=1)
HUMIDITY = Metric("humidity", "Humidity", "%", "humidity", precision=1)
PRESSURE = Metric("pressure", "Pressure", "hPa", "atmospheric_pressure", precision=1)
CARBON_DIOXIDE = Metric("carbon_dioxide", "CO₂", "ppm", "carbon_dioxide", precision=0)

Reading = dict[Metric, float]
