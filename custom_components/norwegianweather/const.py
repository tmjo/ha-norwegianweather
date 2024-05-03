"""Constants for NorwegianWeather."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.const import (
    UnitOfTime,
    UnitOfVolumetricFlux,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfLength,
    UnitOfTime,
    UnitOfSpeed,
    UnitOfVolumetricFlux,
)

from homeassistant.const import (
    PERCENTAGE,
    DEGREE,
    UV_INDEX,
)


from .api import CONST_DIR_DEFAULT

# Base component constants
NAME = "Norwegian Weather"
DOMAIN = "norwegianweather"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.6"
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
        "units": UnitOfSpeed.METERS_PER_SECOND,
        "convert_units_func": None,
        # "device_class": None,
        "device_class": SensorDeviceClass.WIND_SPEED,
        "icon": "mdi:weather-windy",
        "state_func": None,
    },
    "weather_wind_gusts": {
        "type": "sensor",
        "key": "wind_speed_of_gust",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        "units": UnitOfSpeed.METERS_PER_SECOND,
        "convert_units_func": None,
        # "device_class": None,
        "device_class": SensorDeviceClass.WIND_SPEED,
        "icon": "mdi:weather-windy",
        "state_func": None,
    },
    "weather_wind_beaufort": {
        "type": "sensor",
        "key": "wind_speed_bf",
        "attrs": [
            "wind_from_direction",
            "wind_from_direction_cardinal",
            "wind_speed",
            "wind_speed_of_gust",
            "wind_speed_bf",
            "wind_speed_bf_desc",
            "wind_speed_knot",
        ],
        # "units": None,
        "units": UnitOfSpeed.BEAUFORT,
        "convert_units_func": None,
        # "device_class": None,
        "device_class": SensorDeviceClass.WIND_SPEED,
        "icon": "mdi:weather-windy",
        "state_func": None,
    },
    "weather_wind_direction": {
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
        "device_class": None,
        "units": DEGREE,
        "convert_units_func": None,
        "icon": "mdi:windsock",
        "state_func": None,
    },
    "weather_wind_direction_cardinal": {
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
    "weather_temperature": {
        "type": "sensor",
        "key": "air_temperature",
        "attrs": ["dew_point_temperature", "relative_humidity"],
        # "units": TEMP_CELSIUS,
        "units": UnitOfTemperature.CELSIUS,
        "convert_units_func": None,
        # "device_class": DEVICE_CLASS_TEMPERATURE,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "icon": None,
        "state_func": None,
    },
    "weather_air_pressure": {
        "type": "sensor",
        "key": "air_pressure_at_sea_level",
        "attrs": [],
        # "units": PRESSURE_HPA,
        "units": UnitOfPressure.HPA,
        "convert_units_func": None,
        # "device_class": DEVICE_CLASS_PRESSURE,
        "device_class": SensorDeviceClass.PRESSURE,
        "icon": None,
        "state_func": None,
    },
    "weather_cloud_area_fraction": {
        "type": "sensor",
        "key": "cloud_area_fraction",
        "attrs": [
            "cloud_area_fraction_high",
            "cloud_area_fraction_low",
            "cloud_area_fraction_medium",
            "fog_area_fraction",
        ],
        "units": PERCENTAGE,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:cloud",
        "state_func": None,
    },
    "weather_dew_point": {
        "type": "sensor",
        "key": "dew_point_temperature",
        "attrs": ["air_temperature", "relative_humidity"],
        # "units": TEMP_CELSIUS,
        "units": UnitOfTemperature.CELSIUS,
        "convert_units_func": None,
        # "device_class": DEVICE_CLASS_TEMPERATURE,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "icon": None,
        "state_func": None,
    },
    "weather_fog": {
        "type": "sensor",
        "key": "fog_area_fraction",
        "attrs": ["fog_area_fraction", "cloud_area_fraction"],
        "units": PERCENTAGE,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:weather-fog",
        "state_func": None,
    },
    "weather_relative_humidity": {
        "type": "sensor",
        "key": "relative_humidity",
        "attrs": ["air_temperature", "dew_point_temperature"],
        "units": PERCENTAGE,
        "convert_units_func": None,
        # "device_class": DEVICE_CLASS_HUMIDITY,
        "device_class": SensorDeviceClass.HUMIDITY,
        "icon": None,
        "state_func": None,
    },
    "weather_uv_index": {
        "type": "sensor",
        "key": "ultraviolet_index_clear_sky",
        "attrs": [],
        "units": UV_INDEX,
        "convert_units_func": None,
        "device_class": None,
        "icon": "mdi:weather-sunny-alert",
        "state_func": None,
    },
    "weather_precipitation": {
        "type": "sensor",
        "key": "precipitation_amount",
        "attrs": [
            "precipitation_amount",
            "precipitation_amount_max",
            "precipitation_amount_min",
            "probability_of_precipitation",
        ],
        "units": UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        "convert_units_func": None,
        # "device_class": None,
        "device_class": SensorDeviceClass.PRECIPITATION_INTENSITY,
        "icon": "mdi:weather-rainy",
        "state_func": None,
    },
    "weather_thunder": {
        "type": "sensor",
        "key": "probability_of_thunder",
        "attrs": ["probability_of_thunder"],
        "units": PERCENTAGE,
        "convert_units_func": None,
        "device_class": None,
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
        "icon": "mdi:camera-enhance",
        "state_func": None,
    },
}
