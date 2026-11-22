import json
import threading

from air2mqtt.app import Air2Mqtt
from air2mqtt.config import Settings
from air2mqtt.homeassistant import Topics
from air2mqtt.metrics import CARBON_DIOXIDE, HUMIDITY, TEMPERATURE, Metric, Reading
from air2mqtt.sensors import SensorError

TOPICS = Topics(base_topic="air2mqtt", discovery_prefix="homeassistant", device_id="livingroom")
SETTINGS = Settings.from_env({"MQTT_HOST": "broker.local", "DEVICE_ID": "livingroom"})


class FakeMqtt:
    def __init__(self) -> None:
        self.connect_handlers: list = []
        self.subscriptions: dict = {}
        self.messages: dict[str, str] = {}
        self.states: dict[str, str] = {}
        self.stopped = False

    def add_connect_handler(self, handler) -> None:
        self.connect_handlers.append(handler)

    def subscribe(self, topic: str, handler) -> None:
        self.subscriptions[topic] = handler

    def start(self) -> None:
        for handler in self.connect_handlers:
            handler()

    def wait_until_connected(self, _timeout: float) -> bool:
        return True

    def publish(self, topic: str, payload: str, *, retain: bool = False) -> None:
        self.messages[topic] = payload

    def publish_state(self, topic: str, payload: str) -> bool:
        self.states[topic] = payload
        return True

    def stop(self) -> None:
        self.stopped = True


class FakeSensor:
    def __init__(self, name: str, metrics: tuple[Metric, ...], reading: Reading | None) -> None:
        self.name = name
        self.metrics = metrics
        self._reading = reading
        self.closed = False

    def read(self) -> Reading:
        if self._reading is None:
            raise SensorError("not responding")
        return self._reading

    def close(self) -> None:
        self.closed = True


class StopAfterFirstRound(threading.Event):
    """Ends the measurement loop after one round instead of waiting."""

    def wait(self, timeout: float | None = None) -> bool:
        self.set()
        return True


def _run(*sensors: FakeSensor) -> FakeMqtt:
    mqtt = FakeMqtt()
    Air2Mqtt(SETTINGS, sensors, mqtt, TOPICS, sw_version="1.2.3").run(StopAfterFirstRound())
    return mqtt


def test_publishes_every_value_to_its_state_topic() -> None:
    sensor = FakeSensor("BME680", (TEMPERATURE, HUMIDITY), {TEMPERATURE: 21.46, HUMIDITY: 48.0})

    mqtt = _run(sensor)

    assert mqtt.states == {
        "air2mqtt/livingroom/temperature": "21.5",
        "air2mqtt/livingroom/humidity": "48.0",
    }


def test_a_failing_sensor_does_not_stop_the_others() -> None:
    broken = FakeSensor("BME680", (TEMPERATURE,), reading=None)
    working = FakeSensor("MH-Z19", (CARBON_DIOXIDE,), {CARBON_DIOXIDE: 812})

    mqtt = _run(broken, working)

    assert mqtt.states == {"air2mqtt/livingroom/carbon_dioxide": "812"}


def test_shuts_down_mqtt_and_sensors() -> None:
    sensor = FakeSensor("MH-Z19", (CARBON_DIOXIDE,), {CARBON_DIOXIDE: 812})

    mqtt = _run(sensor)

    assert mqtt.stopped
    assert sensor.closed


def test_publishes_discovery_on_connect_and_after_a_home_assistant_restart() -> None:
    sensor = FakeSensor("MH-Z19", (CARBON_DIOXIDE,), {CARBON_DIOXIDE: 812})
    mqtt = _run(sensor)

    discovery = json.loads(mqtt.messages.pop(TOPICS.discovery))
    assert discovery["device"]["sw_version"] == "1.2.3"

    mqtt.subscriptions[TOPICS.homeassistant_status]("online")
    assert TOPICS.discovery in mqtt.messages
