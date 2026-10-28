import pytest

from air2mqtt.config import ConfigError, Settings

_VARIABLES = (
    "MQTT_HOST",
    "MQTT_PORT",
    "MQTT_USERNAME",
    "MQTT_PASSWORD",
    "MQTT_TLS",
    "MQTT_KEEPALIVE",
    "MQTT_BASE_TOPIC",
    "HA_DISCOVERY_PREFIX",
    "DEVICE_ID",
    "DEVICE_NAME",
    "READ_INTERVAL",
    "MHZ19_PORT",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)  # no stray .env file
    for name in _VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("MQTT_HOST", "broker.local")


def test_defaults() -> None:
    settings = Settings.from_env()

    assert settings.mqtt.host == "broker.local"
    assert settings.mqtt.port == 1883
    assert settings.mqtt.use_tls is False
    assert settings.base_topic == "air2mqtt"
    assert settings.discovery_prefix == "homeassistant"
    assert settings.read_interval == 60
    assert settings.log_level == "INFO"


def test_device_id_is_slugified(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEVICE_ID", "Living Room #1")
    assert Settings.from_env().device_id == "living_room_1"


def test_missing_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MQTT_HOST")
    with pytest.raises(ConfigError, match="MQTT_HOST"):
        Settings.from_env()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("READ_INTERVAL", "abc"),
        ("READ_INTERVAL", "2"),
        ("MQTT_TLS", "ture"),
        ("LOG_LEVEL", "VERBOSE"),
    ],
)
def test_invalid_values(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError, match=name):
        Settings.from_env()
