from air2mqtt.homeassistant import Topics, build_discovery_payload
from air2mqtt.metrics import CARBON_DIOXIDE, TEMPERATURE

TOPICS = Topics(base_topic="air2mqtt", discovery_prefix="homeassistant", device_id="livingroom")


def test_topics() -> None:
    assert TOPICS.availability == "air2mqtt/livingroom/availability"
    assert TOPICS.discovery == "homeassistant/device/livingroom/config"
    assert TOPICS.homeassistant_status == "homeassistant/status"
    assert TOPICS.state(TEMPERATURE) == "air2mqtt/livingroom/temperature"


def test_discovery_payload_contains_one_component_per_metric() -> None:
    payload = build_discovery_payload(
        TOPICS, "Living Room", [TEMPERATURE, CARBON_DIOXIDE], expire_after=180
    )

    assert payload["device"]["identifiers"] == ["livingroom"]
    assert payload["availability_topic"] == TOPICS.availability
    assert set(payload["components"]) == {"livingroom_temperature", "livingroom_carbon_dioxide"}

    co2 = payload["components"]["livingroom_carbon_dioxide"]
    assert co2["platform"] == "sensor"
    assert co2["device_class"] == "carbon_dioxide"
    assert co2["unit_of_measurement"] == "ppm"
    assert co2["state_topic"] == "air2mqtt/livingroom/carbon_dioxide"
    assert co2["expire_after"] == 180


def test_metric_formatting() -> None:
    assert TEMPERATURE.format(21.456) == "21.5"
    assert CARBON_DIOXIDE.format(812) == "812"
