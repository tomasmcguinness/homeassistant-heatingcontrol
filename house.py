import asyncio
import logging
from typing import Callable

from homeassistant.core import HomeAssistant
from homeassistant.core import HomeAssistant, callback, Event, EventStateChangedData
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)

class House:
    """House for Hello World example."""

    manufacturer = "Tom Inc"

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Init dummy hub."""
        self._hass = hass
        self._id = name.lower()
        self.name = name
        
        self.rooms = []
        self.online = True

    @property
    def hub_id(self) -> str:
        """ID for dummy hub."""
        return self._id

    async def test_connection(self) -> bool:
        """Test connectivity to the Dummy hub is OK."""
        await asyncio.sleep(1)
        return True


class Room:
    
    def __init__(self, hass, room_id: str, name: str, house: House) -> None:
        self._hass = hass
        self._id = room_id
        self.name = name
        self.house = house
        
        self._temperature_difference = 0
        self._current_temperature = 0
        
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        
        self.unsub = async_track_state_change_event(hass, ["sensor.sitting_room_temperature"], self._async_on_change)
    
    @callback
    def _async_on_change(self, event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        _LOGGER.info(new_state.state)
        self.set_current_temperature(new_state.state)
        
    @property
    def room_id(self) -> str:
        return self._id

    @property
    def current_temperature(self):
        return self._current_temperature
    
    def set_current_temperature(self, temperature: int) -> None:
        _LOGGER.info("Setting current temperature to " + temperature)
        
        self._current_temperature = temperature
        self._temperature_difference = 21 - int(self._current_temperature)
        
        self.publish_updates()
        
    @property
    def temperature_difference(self):
        return self._temperature_difference
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    def publish_updates(self) -> None:
        for callback in self._callbacks:
            _LOGGER.info("Invoking callback!")
            callback()

    @property
    def online(self) -> float:
        """Room is online."""
        return True