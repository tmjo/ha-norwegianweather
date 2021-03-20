"""Sensor platform for NorwegianWeather."""
import logging
from .const import DOMAIN
from .entity import NorwegianWeatherEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = coordinator.get_sensor_entities()
    _LOGGER.debug(
        f"Setting up sensor platform for {coordinator.place}, {len(entities)} entities"
    )
    async_add_devices(entities)


class NorwegianWeatherSensor(NorwegianWeatherEntity):
    """NorwegianWeather Sensor class."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
