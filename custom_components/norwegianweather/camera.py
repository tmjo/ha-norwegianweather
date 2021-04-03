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


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = coordinator.get_camera_entities()
    _LOGGER.debug(
        f"Setting up camera platform for {coordinator.place}, {len(entities)} entities"
    )
    async_add_devices(entities)


# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up the skyfield platform."""
#     latitude = config.get(CONF_LATITUDE, hass.config.latitude)
#     longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
#     tzname = str(hass.config.time_zone)
#     show_constellations = config.get(CONF_SHOW_CONSTELLATIONS)
#     show_time = config.get(CONF_SHOW_TIME)
#     show_legend = config.get(CONF_SHOW_LEGEND)
#     constellation_list = config.get(CONF_CONSTELLATION_LIST)
#     planet_list = config.get(CONF_PLANET_LIST)
#     north_up = config.get(CONF_NORTH_UP)
#     configdir = hass.config.config_dir
#     tmpdir = "/tmp/skyfield"
#     _LOGGER.debug("Setting up skyfield.")
#     panel = SkyFieldCam(
#         latitude,
#         longitude,
#         tzname,
#         configdir,
#         tmpdir,
#         show_constellations,
#         show_time,
#         show_legend,
#         constellation_list,
#         planet_list,
#         north_up,
#     )

#     _LOGGER.debug("Adding skyfield cam")
#     add_entities([panel], True)


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
    def frame_interval(self):
        # this is how often the image will update in the background.
        # When the GUI panel is up, it is always updated every
        # 10 seconds, which is too much. Must figure out how to
        # reduce...
        return 60

    def camera_image(self):
        """Load image bytes in memory"""
        # # don't use throttle because extra calls return Nones
        # if not self._loaded:
        #     _LOGGER.debug("Loading image data")
        #     self.sky.load(self._tmpdir)
        #     self._loaded = True
        _LOGGER.debug("Updating camera image")
        buf = io.BytesIO()
        # self.sky.plot_sky(buf)
        self.coordinator.api.process_weather_image(
            weatherdata=self.coordinator.api.data.get("timeseries", None), filename=buf
        )
        buf.seek(0)
        return buf.getvalue()

    # def __init__(
    #     self,
    #     latitude,
    #     longitude,
    #     tzname,
    #     configdir,
    #     tmpdir,
    #     show_constellations,
    #     show_time,
    #     show_legend,
    #     constellations,
    #     planets,
    #     north_up,
    # ):
    #     Camera.__init__(self)
    #     from . import bodies

    #     self.sky = bodies.Sky(
    #         (latitude, longitude),
    #         tzname,
    #         show_constellations,
    #         show_time,
    #         show_legend,
    #         constellations,
    #         planets,
    #         north_up,
    #     )
    #     self._loaded = False
    #     self._configdir = configdir
    #     self._tmpdir = tmpdir

    # @property
    # def frame_interval(self):
    #     # this is how often the image will update in the background.
    #     # When the GUI panel is up, it is always updated every
    #     # 10 seconds, which is too much. Must figure out how to
    #     # reduce...
    #     return 60

    # @property
    # def name(self):
    #     return "SkyField"

    # @property
    # def brand(self):
    #     return "SkyField"

    # @property
    # def model(self):
    #     return "Sky"

    # @property
    # def icon(self):
    #     return ICON

    # def camera_image(self):
    #     """Load image bytes in memory"""
    #     # don't use throttle because extra calls return Nones
    #     if not self._loaded:
    #         _LOGGER.debug("Loading skyfield data")
    #         self.sky.load(self._tmpdir)
    #         self._loaded = True
    #     _LOGGER.debug("Updating skyfield plot")
    #     buf = io.BytesIO()
    #     self.sky.plot_sky(buf)
    #     buf.seek(0)
    #     return buf.getvalue()