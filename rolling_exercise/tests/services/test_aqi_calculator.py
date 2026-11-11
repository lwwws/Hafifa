import pytest

from src.services.aqi_calculator import AqiCalculator
from tests.providers.aqi import Aqi, AqiLevel, Co2, No2, Pm25


@pytest.mark.parametrize(
    ("pm25", "expected_level"),
    [
        (Pm25.GOOD, AqiLevel.GOOD),
        (Pm25.MODERATE, AqiLevel.MODERATE),
        (Pm25.UNHEALTHY_FOR_SENSITIVE_GROUPS, AqiLevel.UNHEALTHY_FOR_SENSITIVE_GROUPS),
        (Pm25.UNHEALTHY, AqiLevel.UNHEALTHY),
        (Pm25.VERY_UNHEALTHY, AqiLevel.VERY_UNHEALTHY),
        (Pm25.HAZARDOUS, AqiLevel.HAZARDOUS),
    ],
)
def test_pm25_range_decides_the_level(pm25, expected_level):
    result = AqiCalculator().calculate(pm25=pm25, no2=No2.GOOD, co2=Co2.GOOD)

    assert result.aqi_level == expected_level


def test_pm25_at_top_of_good_range_gives_top_good_aqi():
    result = AqiCalculator().calculate(pm25=Pm25.TOP_OF_GOOD, no2=No2.GOOD, co2=Co2.GOOD)

    assert result.aqi == Aqi.TOP_OF_GOOD
    assert result.aqi_level == AqiLevel.GOOD


def test_highest_pollutant_decides_the_aqi():
    result = AqiCalculator().calculate(pm25=Pm25.GOOD, no2=No2.VERY_UNHEALTHY, co2=Co2.GOOD)

    assert result.aqi_level == AqiLevel.VERY_UNHEALTHY


def test_co2_above_highest_breakpoint_gives_max_aqi():
    result = AqiCalculator().calculate(pm25=Pm25.GOOD, no2=No2.GOOD, co2=Co2.ABOVE_HIGHEST_BREAKPOINT)

    assert result.aqi == Aqi.MAX
    assert result.aqi_level == AqiLevel.HAZARDOUS
