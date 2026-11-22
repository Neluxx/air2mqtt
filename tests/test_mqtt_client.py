from unittest.mock import Mock

import paho.mqtt.client as mqtt
from paho.mqtt.reasoncodes import ReasonCode

from air2mqtt.config import MqttSettings
from air2mqtt.mqtt_client import OFFLINE, ONLINE, MqttClient

AVAILABILITY = "air2mqtt/livingroom/availability"
SETTINGS = MqttSettings(
    host="broker.local",
    port=1883,
    username=None,
    password=None,
    use_tls=False,
    keepalive=60,
)


def _client(*, publish_rc: int = mqtt.MQTT_ERR_SUCCESS) -> tuple[MqttClient, Mock]:
    client = MqttClient(SETTINGS, client_id="air2mqtt-test", availability_topic=AVAILABILITY)
    paho = Mock()
    paho.publish.return_value.rc = publish_rc
    client._client = paho
    return client, paho


def _connect(client: MqttClient) -> None:
    success = ReasonCode(mqtt.PacketTypes.CONNACK, identifier=0)
    client._handle_connect(Mock(), None, Mock(), success, None)


def test_subscribes_and_announces_online_after_connect_handlers() -> None:
    client, paho = _client()
    client.subscribe("homeassistant/status", lambda _payload: None)
    client.add_connect_handler(lambda: paho.publish("homeassistant/device/x/config", "{}"))

    _connect(client)

    paho.subscribe.assert_called_once_with("homeassistant/status", qos=1)
    published_topics = [c.args[0] for c in paho.publish.call_args_list]
    assert published_topics == ["homeassistant/device/x/config", AVAILABILITY]
    assert paho.publish.call_args.args[1] == ONLINE
    assert client.wait_until_connected(0)


def test_publish_state_is_dropped_while_disconnected() -> None:
    client, paho = _client()
    paho.is_connected.return_value = False

    assert client.publish_state("air2mqtt/livingroom/temperature", "21.5") is False
    paho.publish.assert_not_called()


def test_stop_announces_offline_and_waits_for_delivery() -> None:
    client, paho = _client()

    client.stop()

    paho.publish.assert_called_once_with(AVAILABILITY, OFFLINE, qos=1, retain=True)
    paho.publish.return_value.wait_for_publish.assert_called_once()
    paho.disconnect.assert_called_once()
    paho.loop_stop.assert_called_once()
