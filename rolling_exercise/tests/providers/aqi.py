class AqiLevel:
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_FOR_SENSITIVE_GROUPS = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class Pm25:
    GOOD = 5
    TOP_OF_GOOD = 12
    MODERATE = 20
    UNHEALTHY_FOR_SENSITIVE_GROUPS = 40
    UNHEALTHY = 100
    VERY_UNHEALTHY = 200
    HAZARDOUS = 300


class No2:
    GOOD = 10
    VERY_UNHEALTHY = 700


class Co2:
    GOOD = 1
    # Above the highest CO2 breakpoint of the given AQI function
    ABOVE_HIGHEST_BREAKPOINT = 450


class Aqi:
    TOP_OF_GOOD = 50
    MAX = 500
