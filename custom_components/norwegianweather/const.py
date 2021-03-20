"""Constants for NorwegianWeather."""
from homeassistant.const import (
    DEVICE_CLASS_TIMESTAMP,
    LENGTH_CENTIMETERS,
    TIME_HOURS,
)

# Base component constants
NAME = "Norwegian Weather"
DOMAIN = "norwegianweather"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "2021.3.1"
ATTRIBUTION = "Data from ©Yr (www.yr.no)"
MANUFACTURER = "yr.no"
ISSUE_URL = "https://github.com/custom-components/NorwegianWeather/issues"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
CAMERA = "camera"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH, CAMERA]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_PLACE = "place"
CONF_LAT = "latitude"
CONF_LONG = "longitude"
CONF_STRINGTIME = "%d.%m %H:%M"

# Defaults
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""


ENTITIES = {
    "norwegian_weather": {
        "type": "sensor",
        "key": "type",
        "attrs": [],
        "units": None,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:home",
        "state_func": None,
    },
    "weather_cam": {
        "type": "camera",
        "key": "type",
        "attrs": [],
        "units": None,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:home",
        "state_func": None,
    },
}
