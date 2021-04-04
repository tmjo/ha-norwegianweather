"""Constants for NorwegianWeather."""
from homeassistant.const import (
    DEVICE_CLASS_TIMESTAMP,
    LENGTH_CENTIMETERS,
    TIME_HOURS,
    SPEED_METERS_PER_SECOND,
    PERCENTAGE,
    PRECIPITATION_MILLIMETERS_PER_HOUR,
    DEGREE,
    UV_INDEX,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
    PRESSURE_HPA,
)

# Base component constants
NAME = "Norwegian Weather"
DOMAIN = "norwegianweather"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "2021.3.3"
ATTRIBUTION = "Data from MET Norway (www.met.no)"
MANUFACTURER = f"{NAME}"
ISSUE_URL = "https://github.com/tmjo/ha-norwegianweather/issues"

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
    "weather_main": {
        "type": "sensor",
        "key": "symbol_code",
        "attrs": [
            "timeseries",
            "latitude",
            "longitude",
        ],
        "units": None,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:weather-windy-variant",
        "state_func": None,
    },
    "weather_wind_speed": {
        "type": "sensor",
        "key": "wind_speed",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        "units": None,
        "convert_units_func": None,
        "device_class": SPEED_METERS_PER_SECOND,
        "icon": "mdi:windsock",
        "state_func": None,
    },
    "wind_direction": {
        "type": "sensor",
        "key": "wind_from_direction",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        "units": None,
        "convert_units_func": None,
        "device_class": DEGREE,
        "icon": "mdi:windsock",
        "state_func": None,
    },
    "wind_direction_cardinal": {
        "type": "sensor",
        "key": "wind_from_direction_cardinal",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        "units": None,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:windsock",
        "state_func": None,
    },
    "temperature": {
        "type": "sensor",
        "key": "air_temperature",
        "attrs": ["dew_point_temperature", "relative_humidity"],
        "units": None,
        "convert_units_func": None,
        "device_class": TEMP_CELSIUS,
        "icon": None,
        "state_func": None,
    },
    "air_pressure": {
        "type": "sensor",
        "key": "air_pressure_at_sea_level",
        "attrs": [],
        "units": None,
        "convert_units_func": None,
        "device_class": PRESSURE_HPA,
        "icon": None,
        "state_func": None,
    },
    "cloud_area_fraction": {
        "type": "sensor",
        "key": "cloud_area_fraction",
        "attrs": [
            "cloud_area_fraction_high",
            "cloud_area_fraction_low",
            "cloud_area_fraction_medium",
            "fog_area_fraction",
        ],
        "units": None,
        "convert_units_func": None,
        "device_class": PERCENTAGE,
        "icon": None,
        "state_func": None,
    },
    "dew_point": {
        "type": "sensor",
        "key": "dew_point_temperature",
        "attrs": ["air_temperature", "relative_humidity"],
        "units": None,
        "convert_units_func": None,
        "device_class": TEMP_CELSIUS,
        "icon": None,
        "state_func": None,
    },
    "fog": {
        "type": "sensor",
        "key": "fog_area_fraction",
        "attrs": ["fog_area_fraction", "cloud_area_fraction"],
        "units": None,
        "convert_units_func": None,
        "device_class": PERCENTAGE,
        "icon": None,
        "state_func": None,
    },
    "relative_humidity": {
        "type": "sensor",
        "key": "relative_humidity",
        "attrs": ["air_temperature", "dew_point_temperature"],
        "units": None,
        "convert_units_func": None,
        "device_class": DEVICE_CLASS_HUMIDITY,
        "icon": None,
        "state_func": None,
    },
    "uv_index": {
        "type": "sensor",
        "key": "ultraviolet_index_clear_sky",
        "attrs": [],
        "units": None,
        "convert_units_func": None,
        "device_class": UV_INDEX,
        "icon": None,
        "state_func": None,
    },
    "wind_direction": {
        "type": "sensor",
        "key": "wind_from_direction",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        "units": DEGREE,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:windsock",
        "state_func": None,
    },
    "precipitation": {
        "type": "sensor",
        "key": "precipitation_amount",
        "attrs": [
            "precipitation_amount",
            "precipitation_amount_max",
            "precipitation_amount_min",
            "probability_of_precipitation",
        ],
        "units": PRECIPITATION_MILLIMETERS_PER_HOUR,
        "convert_units_func": None,
        "device_class": None,
        "icon": None,
        "state_func": None,
    },
    "thunder": {
        "type": "sensor",
        "key": "probability_of_thunder",
        "attrs": ["probability_of_thunder"],
        "units": None,
        "convert_units_func": None,
        "device_class": PERCENTAGE,
        "icon": "mdi:weather-lightning",
        "state_func": None,
    },
    "weather_cam": {
        "type": "camera",
        "key": "place",
        "attrs": [],
        "units": None,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:chart-timeline-variant-shimmer",
        "state_func": None,
    },
}
