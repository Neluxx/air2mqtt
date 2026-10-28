import pytest

from air2mqtt.sensors.base import SensorError
from air2mqtt.sensors.mhz19 import checksum, parse_co2_response


def _frame(co2_ppm: int) -> bytes:
    body = bytes([0xFF, 0x86, co2_ppm >> 8, co2_ppm & 0xFF, 0x47, 0, 0, 0])
    return body + bytes([checksum(body + b"\x00")])


def test_request_checksum_matches_datasheet() -> None:
    assert checksum(bytes([0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0])) == 0x79


def test_parse_valid_frame() -> None:
    assert parse_co2_response(_frame(812)) == 812


def test_rejects_short_frame() -> None:
    with pytest.raises(SensorError, match="bytes"):
        parse_co2_response(b"\xff\x86\x03")


def test_rejects_bad_checksum() -> None:
    frame = bytearray(_frame(812))
    frame[8] ^= 0xFF
    with pytest.raises(SensorError, match="checksum"):
        parse_co2_response(bytes(frame))


def test_rejects_unexpected_command() -> None:
    frame = bytearray(_frame(812))
    frame[1] = 0x99
    frame[8] = checksum(frame)
    with pytest.raises(SensorError, match="unexpected"):
        parse_co2_response(bytes(frame))
