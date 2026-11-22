from collections.abc import Mapping

import pytest

from air2mqtt.config import ConfigError, Settings

_REQUIRED = {"MQTT_HOST": "broker.local"}


def _load(**overrides: str) -> Settings:
    env: Mapping[str, str] = {**_REQUIRED, **overrides}
    return Settings.from_env(env)


def test_defaults() -> None:
    settings = _load()

    assert settings.mqtt.host == "broker.local"
    assert settings.mqtt.port == 1883
    assert settings.mqtt.use_tls is False
    assert settings.base_topic == "air2mqtt"
    assert settings.discovery_prefix == "homeassistant"
    assert settings.read_interval == 60
    assert settings.temperature_offset == 0.0
    assert settings.log_level == "INFO"


def test_blank_values_fall_back_to_defaults() -> None:
    assert _load(MQTT_PORT="  ", LOG_LEVEL="").mqtt.port == 1883


def test_device_id_is_slugified() -> None:
    assert _load(DEVICE_ID="Living Room #1").device_id == "living_room_1"


def test_temperature_offset() -> None:
    assert _load(TEMPERATURE_OFFSET="-1.5").temperature_offset == -1.5


def test_missing_host() -> None:
    with pytest.raises(ConfigError, match="MQTT_HOST"):
        Settings.from_env({})


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("READ_INTERVAL", "abc"),
        ("READ_INTERVAL", "2"),
        ("MQTT_TLS", "ture"),
        ("TEMPERATURE_OFFSET", "warm"),
        ("TEMPERATURE_OFFSET", "-12"),
        ("TEMPERATURE_OFFSET", "nan"),
        ("LOG_LEVEL", "VERBOSE"),
    ],
)
def test_invalid_values(name: str, value: str) -> None:
    with pytest.raises(ConfigError, match=name):
        _load(**{name: value})
