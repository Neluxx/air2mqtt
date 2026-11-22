from air2mqtt.metrics import CARBON_DIOXIDE, TEMPERATURE


def test_metric_formatting() -> None:
    assert TEMPERATURE.format(21.456) == "21.5"
    assert CARBON_DIOXIDE.format(812) == "812"
