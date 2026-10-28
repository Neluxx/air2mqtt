"""Application settings, loaded from environment variables (and an optional ``.env`` file)."""

from __future__ import annotations

import os
import re
import socket
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv

_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


class ConfigError(ValueError):
    """Raised when a required setting is missing or a value is invalid."""


@dataclass(frozen=True, slots=True)
class MqttSettings:
    host: str
    port: int
    username: str | None
    password: str | None
    use_tls: bool
    keepalive: int


@dataclass(frozen=True, slots=True)
class Settings:
    mqtt: MqttSettings
    base_topic: str
    discovery_prefix: str
    device_id: str
    device_name: str
    read_interval: int
    mhz19_port: str
    log_level: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(find_dotenv(usecwd=True))

        return cls(
            mqtt=MqttSettings(
                host=_require("MQTT_HOST"),
                port=_int("MQTT_PORT", 1883),
                username=os.getenv("MQTT_USERNAME") or None,
                password=os.getenv("MQTT_PASSWORD") or None,
                use_tls=_bool("MQTT_TLS", False),
                keepalive=_int("MQTT_KEEPALIVE", 60),
            ),
            base_topic=os.getenv("MQTT_BASE_TOPIC", "air2mqtt").strip("/"),
            discovery_prefix=os.getenv("HA_DISCOVERY_PREFIX", "homeassistant").strip("/"),
            device_id=_slugify(os.getenv("DEVICE_ID") or socket.gethostname()),
            device_name=os.getenv("DEVICE_NAME", "Air2MQTT"),
            read_interval=_int("READ_INTERVAL", 60, minimum=5),
            mhz19_port=os.getenv("MHZ19_PORT", "/dev/serial0"),
            log_level=_choice("LOG_LEVEL", "INFO", _LOG_LEVELS),
        )


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Environment variable {name} is required.")
    return value


def _int(name: str, default: int, *, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}.") from exc
    if value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {value}.")
    return value


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true or false, got {raw!r}.")


def _choice(name: str, default: str, choices: tuple[str, ...]) -> str:
    value = (os.getenv(name) or default).strip().upper()
    if value not in choices:
        raise ConfigError(f"{name} must be one of {', '.join(choices)}, got {value!r}.")
    return value


def _slugify(value: str) -> str:
    """Make a value safe for use in MQTT topics and Home Assistant unique IDs."""
    slug = re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower()).strip("_")
    if not slug:
        raise ConfigError(f"Cannot derive a valid device id from {value!r}.")
    return slug
