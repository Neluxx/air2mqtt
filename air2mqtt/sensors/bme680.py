"""Bosch BME680 - temperature, humidity and pressure via I²C (Pimoroni driver)."""

from __future__ import annotations

import logging
import time
from types import ModuleType
from typing import Any

from air2mqtt.metrics import HUMIDITY, PRESSURE, TEMPERATURE, Reading
from air2mqtt.sensors.base import SensorError

log = logging.getLogger(__name__)

_READ_TIMEOUT_SECONDS = 5.0
_POLL_INTERVAL_SECONDS = 0.1


class BME680Sensor:
    name = "BME680"
    metrics = (TEMPERATURE, HUMIDITY, PRESSURE)

    def __init__(self) -> None:
        try:
            import bme680
        except ImportError as exc:
            raise SensorError("The 'bme680' package is not installed.") from exc

        self._sensor = self._connect(bme680)

        # Oversampling and filter settings as recommended by Bosch.
        self._sensor.set_humidity_oversample(bme680.OS_2X)
        self._sensor.set_pressure_oversample(bme680.OS_4X)
        self._sensor.set_temperature_oversample(bme680.OS_8X)
        self._sensor.set_filter(bme680.FILTER_SIZE_3)

        # The gas heater is not used and would skew the temperature reading.
        self._sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)

        log.info("BME680 initialised.")

    @staticmethod
    def _connect(bme680: ModuleType) -> Any:
        errors = []
        for address in (bme680.I2C_ADDR_PRIMARY, bme680.I2C_ADDR_SECONDARY):
            try:
                return bme680.BME680(address)
            except (OSError, RuntimeError) as exc:
                errors.append(f"0x{address:02x}: {exc}")
        raise SensorError(f"BME680 not found on I²C ({'; '.join(errors)}).")

    def read(self) -> Reading:
        deadline = time.monotonic() + _READ_TIMEOUT_SECONDS
        try:
            while not self._sensor.get_sensor_data():
                if time.monotonic() >= deadline:
                    raise SensorError("BME680 returned no data in time.")
                time.sleep(_POLL_INTERVAL_SECONDS)
        except OSError as exc:
            raise SensorError(f"BME680 read failed: {exc}") from exc

        data = self._sensor.data
        return {
            TEMPERATURE: data.temperature,
            HUMIDITY: data.humidity,
            PRESSURE: data.pressure,
        }

    def close(self) -> None:
        """The I²C bus is shared and needs no explicit cleanup."""
