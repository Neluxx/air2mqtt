"""Winsen MH-Z19 - CO₂ concentration via UART.

Speaks the sensor's serial protocol directly, so no root privileges or
service restarts are needed (unlike the ``mh-z19`` PyPI package).
"""

from __future__ import annotations

import logging

import serial

from air2mqtt.metrics import CARBON_DIOXIDE, Reading
from air2mqtt.sensors.base import SensorError

log = logging.getLogger(__name__)

_BAUD_RATE = 9600
_TIMEOUT_SECONDS = 2.0
_FRAME_LENGTH = 9
_START_BYTE = 0xFF
_CMD_READ_CO2 = 0x86
_READ_CO2_REQUEST = bytes([_START_BYTE, 0x01, _CMD_READ_CO2, 0, 0, 0, 0, 0, 0x79])

_PLAUSIBLE_RANGE_PPM = range(300, 10_001)


def checksum(frame: bytes) -> int:
    """Checksum as defined in the MH-Z19 datasheet: two's complement of bytes 1-7."""
    return (0xFF - (sum(frame[1:8]) & 0xFF) + 1) & 0xFF


def parse_co2_response(frame: bytes) -> int:
    """Extract the CO₂ value (ppm) from a response frame. Raises SensorError if invalid."""
    if len(frame) != _FRAME_LENGTH:
        raise SensorError(f"MH-Z19 sent {len(frame)} bytes, expected {_FRAME_LENGTH}.")
    if frame[0] != _START_BYTE or frame[1] != _CMD_READ_CO2:
        raise SensorError(f"MH-Z19 sent an unexpected frame: {frame.hex(' ')}.")
    if frame[8] != checksum(frame):
        raise SensorError("MH-Z19 response checksum mismatch.")
    return (frame[2] << 8) | frame[3]


class MHZ19Sensor:
    name = "MH-Z19"
    metrics = (CARBON_DIOXIDE,)

    def __init__(self, port: str) -> None:
        try:
            self._serial = serial.Serial(port, baudrate=_BAUD_RATE, timeout=_TIMEOUT_SECONDS)
        except serial.SerialException as exc:
            raise SensorError(f"Cannot open MH-Z19 serial port {port}: {exc}") from exc
        log.info("MH-Z19 initialised on %s.", port)

    def read(self) -> Reading:
        try:
            self._serial.reset_input_buffer()
            self._serial.write(_READ_CO2_REQUEST)
            frame = self._serial.read(_FRAME_LENGTH)
        except serial.SerialException as exc:
            raise SensorError(f"MH-Z19 read failed: {exc}") from exc

        co2_ppm = parse_co2_response(frame)
        if co2_ppm not in _PLAUSIBLE_RANGE_PPM:
            log.warning("MH-Z19 reported an implausible value of %d ppm.", co2_ppm)

        return {CARBON_DIOXIDE: co2_ppm}

    def close(self) -> None:
        self._serial.close()
