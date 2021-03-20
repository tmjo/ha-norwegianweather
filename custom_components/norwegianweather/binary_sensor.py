"""Binary sensor platform for NorwegianWeather."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    BINARY_SENSOR,
    DOMAIN,
)
from .entity import NorwegianWeatherEntity
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = coordinator.get_binary_sensor_entities()
    _LOGGER.debug(
        f"Setting up binary sensor platform for {coordinator.place}, {len(entities)} entities"
    )
    async_add_devices(entities)


class NorwegianWeatherBinarySensor(NorwegianWeatherEntity, BinarySensorEntity):
    """NorwegianWeather binary_sensor class."""

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state
