"""Camera platform for NorwegianWeather."""

import logging
from datetime import timedelta
import io
from typing import Callable, List

import voluptuous as vol

from homeassistant.components.camera import Camera
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv

from .entity import NorwegianWeatherEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)

from .const import (
    CONF_STRINGTIME,
    DOMAIN,
    DOMAIN,
    MANUFACTURER,
    NAME,
    VERSION,
    ATTRIBUTION,
)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = coordinator.get_camera_entities()
    _LOGGER.debug(
        f"Setting up camera platform for {coordinator.place}, {len(entities)} entities"
    )
    async_add_devices(entities)


class NorwegianWeatherCam(Camera, NorwegianWeatherEntity):
    """NorwegianWeather Camera class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        place,
        name: str,
        state_key: str,
        units: str,
        convert_units_func: Callable,
        attrs_keys: List[str],
        device_class: str,
        icon: str,
        state_func=None,
        switch_func=None,
    ):
        NorwegianWeatherEntity.__init__(
            self,
            coordinator,
            config_entry,
            place,
            name,
            state_key,
            units,
            convert_units_func,
            attrs_keys,
            device_class,
            icon,
            state_func,
            switch_func,
        )
        Camera.__init__(self)

    # def __init__(self):
    #     Camera.__init__(self)

    @property
    def brand(self):
        """Return the camera brand."""
        return self.device_info.get("manufacturer", None)

    @property
    def model(self):
        """Return the camera model."""
        return self.device_info.get("model", None)

    @property
    def frame_interval(self):
        # this is how often the image will update in the background.
        # When the GUI panel is up, it is always updated every
        # 10 seconds, which is too much. Must figure out how to
        # reduce...
        return 60

    def camera_image(self):
        """Load image bytes in memory"""
        _LOGGER.debug("Updating camera image")
        buf = io.BytesIO()
        self.coordinator.api.process_weather_image(
            weatherdata=self.coordinator.api.data.get("timeseries", None), filename=buf
        )
        buf.seek(0)
        return buf.getvalue()
