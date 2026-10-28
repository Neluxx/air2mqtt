"""Thin wrapper around paho-mqtt with availability (LWT) and automatic reconnects."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.reasoncodes import ReasonCode

from air2mqtt.config import MqttSettings

log = logging.getLogger(__name__)

ONLINE = "online"
OFFLINE = "offline"

_QOS = 1
_RECONNECT_MIN_DELAY = 1
_RECONNECT_MAX_DELAY = 120
_SHUTDOWN_TIMEOUT_SECONDS = 5

MessageHandler = Callable[[str], None]
ConnectHandler = Callable[[], None]


class MqttClient:
    def __init__(self, settings: MqttSettings, client_id: str, availability_topic: str) -> None:
        self._settings = settings
        self._availability_topic = availability_topic
        self._connect_handlers: list[ConnectHandler] = []
        self._subscriptions: dict[str, MessageHandler] = {}
        self._connected = threading.Event()

        self._client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
        if settings.username:
            self._client.username_pw_set(settings.username, settings.password)
        if settings.use_tls:
            self._client.tls_set()

        # The broker publishes "offline" on our behalf if we disappear unexpectedly.
        self._client.will_set(availability_topic, OFFLINE, qos=_QOS, retain=True)
        self._client.reconnect_delay_set(_RECONNECT_MIN_DELAY, _RECONNECT_MAX_DELAY)

        self._client.on_connect = self._handle_connect
        self._client.on_disconnect = self._handle_disconnect

    # -- Public API -----------------------------------------------------------

    def add_connect_handler(self, handler: ConnectHandler) -> None:
        """Run ``handler`` after every (re)connect, before the client announces itself online."""
        self._connect_handlers.append(handler)

    def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Subscribe to ``topic``; the subscription is restored on every reconnect."""
        self._subscriptions[topic] = handler
        self._client.message_callback_add(topic, self._wrap(handler))

    def publish(self, topic: str, payload: str, *, retain: bool = False) -> None:
        """Publish reliably (QoS 1). Intended for config and availability messages."""
        result = self._client.publish(topic, payload, qos=_QOS, retain=retain)
        if result.rc not in (mqtt.MQTT_ERR_SUCCESS, mqtt.MQTT_ERR_NO_CONN):
            log.warning("Publishing to %s failed: %s", topic, mqtt.error_string(result.rc))

    def publish_state(self, topic: str, payload: str) -> bool:
        """Publish a live measurement, or drop it if the broker is unreachable.

        Measurements are deliberately not buffered: Home Assistant timestamps a
        state on arrival, so values delivered late would show up at the wrong time.
        Returns whether the value was handed to the broker connection.
        """
        if not self._client.is_connected():
            return False
        result = self._client.publish(topic, payload, qos=0, retain=False)
        return result.rc == mqtt.MQTT_ERR_SUCCESS

    def start(self) -> None:
        log.info("Connecting to MQTT broker %s:%d …", self._settings.host, self._settings.port)
        self._client.connect_async(
            self._settings.host,
            self._settings.port,
            keepalive=self._settings.keepalive,
        )
        self._client.loop_start()

    def wait_until_connected(self, timeout: float) -> bool:
        """Block until the client is connected or ``timeout`` expires."""
        return self._connected.wait(timeout)

    def stop(self) -> None:
        if self._client.is_connected():
            info = self._client.publish(self._availability_topic, OFFLINE, qos=_QOS, retain=True)
            info.wait_for_publish(timeout=_SHUTDOWN_TIMEOUT_SECONDS)
        self._client.disconnect()
        self._client.loop_stop()
        log.info("Disconnected from MQTT broker.")

    # -- Callbacks ------------------------------------------------------------

    def _handle_connect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: mqtt.ConnectFlags,
        reason_code: ReasonCode,
        _properties: Any,
    ) -> None:
        if reason_code.is_failure:
            log.error("MQTT connection refused: %s", reason_code)
            return

        log.info("Connected to MQTT broker.")
        for topic in self._subscriptions:
            self._client.subscribe(topic, qos=_QOS)

        for handler in self._connect_handlers:
            handler()
        self.publish(self._availability_topic, ONLINE, retain=True)
        self._connected.set()

    def _handle_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: mqtt.DisconnectFlags,
        reason_code: ReasonCode,
        _properties: Any,
    ) -> None:
        self._connected.clear()
        if reason_code.is_failure:
            log.warning("Lost connection to MQTT broker (%s), reconnecting …", reason_code)

    @staticmethod
    def _wrap(handler: MessageHandler) -> Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]:
        def on_message(_client: mqtt.Client, _userdata: Any, message: mqtt.MQTTMessage) -> None:
            handler(message.payload.decode("utf-8", errors="replace"))

        return on_message
