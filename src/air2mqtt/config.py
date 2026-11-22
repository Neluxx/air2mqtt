"""Application settings, parsed from environment variables."""

from __future__ import annotations

import re
import socket
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_KEEPALIVE_SECONDS = 60
DEFAULT_READ_INTERVAL_SECONDS = 60
MIN_READ_INTERVAL_SECONDS = 5
MAX_TEMPERATURE_OFFSET = 10.0

_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}

Environment = Mapping[str, str]


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
    temperature_offset: float
    mhz19_port: str
    log_level: str

    @classmethod
    def from_env(cls, env: Environment) -> Settings:
        """Parse all settings from ``env``, e.g. ``os.environ``."""
        return cls(
            mqtt=MqttSettings(
                host=_require(env, "MQTT_HOST"),
                port=_int(env, "MQTT_PORT", DEFAULT_MQTT_PORT),
                username=_get(env, "MQTT_USERNAME"),
                password=env.get("MQTT_PASSWORD") or None,
                use_tls=_bool(env, "MQTT_TLS", False),
                keepalive=_int(env, "MQTT_KEEPALIVE", DEFAULT_MQTT_KEEPALIVE_SECONDS),
            ),
            base_topic=(_get(env, "MQTT_BASE_TOPIC") or "air2mqtt").strip("/"),
            discovery_prefix=(_get(env, "HA_DISCOVERY_PREFIX") or "homeassistant").strip("/"),
            device_id=_slugify(_get(env, "DEVICE_ID") or socket.gethostname()),
            device_name=_get(env, "DEVICE_NAME") or "Air2MQTT",
            read_interval=_int(
                env,
                "READ_INTERVAL",
                DEFAULT_READ_INTERVAL_SECONDS,
                minimum=MIN_READ_INTERVAL_SECONDS,
            ),
            temperature_offset=_float(env, "TEMPERATURE_OFFSET", 0.0, limit=MAX_TEMPERATURE_OFFSET),
            mhz19_port=_get(env, "MHZ19_PORT") or "/dev/serial0",
            log_level=_choice(env, "LOG_LEVEL", "INFO", _LOG_LEVELS),
        )


def _get(env: Environment, name: str) -> str | None:
    """Return the trimmed value of ``name``, or None if it is unset or blank."""
    return env.get(name, "").strip() or None


def _require(env: Environment, name: str) -> str:
    value = _get(env, name)
    if value is None:
        raise ConfigError(f"Environment variable {name} is required.")
    return value


def _int(env: Environment, name: str, default: int, *, minimum: int = 1) -> int:
    raw = _get(env, name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}.") from exc
    if value < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {value}.")
    return value


def _float(env: Environment, name: str, default: float, *, limit: float) -> float:
    """Parse a float whose absolute value must not exceed ``limit``."""
    raw = _get(env, name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got {raw!r}.") from exc
    if not -limit <= value <= limit:
        raise ConfigError(f"{name} must be between -{limit:g} and {limit:g}, got {value:g}.")
    return value


def _bool(env: Environment, name: str, default: bool) -> bool:
    raw = _get(env, name)
    if raw is None:
        return default
    value = raw.lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true or false, got {raw!r}.")


def _choice(env: Environment, name: str, default: str, choices: tuple[str, ...]) -> str:
    value = (_get(env, name) or default).upper()
    if value not in choices:
        raise ConfigError(f"{name} must be one of {', '.join(choices)}, got {value!r}.")
    return value


def _slugify(value: str) -> str:
    """Make a value safe for use in MQTT topics and Home Assistant unique IDs."""
    slug = re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower()).strip("_")
    if not slug:
        raise ConfigError(f"Cannot derive a valid device id from {value!r}.")
    return slug
