import asyncio
import logging
import math

from typing import Callable

from homeassistant.core import HomeAssistant
from homeassistant.core import HomeAssistant, callback, Event, EventStateChangedData
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)

class House:
    """House for Hello World example."""

    manufacturer = "Tom Inc"

    def __init__(self, hass: HomeAssistant, name: str, outdoor_temperature_sensor: str) -> None:
        """Init dummy hub."""
        self._hass = hass
        self._id = name.lower()
        self.name = name
        self.outdoor_temperature = 10 # get from another sensor
        
        self.rooms = []
        
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()

        self.unsub = async_track_state_change_event(hass, [outdoor_temperature_sensor], self._async_on_change)
    
    @callback
    def _async_on_change(self, event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is not None:
            self.set_current_temperature(float(new_state.state))

    def set_current_temperature(self, temperature: float) -> None:
        self.outdoor_temperature = temperature
        self.publish_updates()
        
    @property
    def hub_id(self) -> str:
        return self._id

    async def test_connection(self) -> bool:
        await asyncio.sleep(1)
        return True
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.discard(callback)

    def publish_updates(self) -> None:
        for callback in self._callbacks:
            callback()
            
        for room in self.rooms:
            room.recalculate()

    @property
    def online(self) -> float:
        return True

class Room:
    
    def __init__(self, hass, room_id: str, name: str, current_temperature_sensor:str, target_temperature: float, heat_loss: int, house: House) -> None:
        self._hass = hass
        self._id = room_id
    
        self.name = name
        self.house = house
        self.radiators = []
    
        self._target_temperature = target_temperature
        self._heat_loss = heat_loss    
        self._temperature_difference = 0
        self._current_temperature = 0
        self._curent_heat_demand = 0
        self._target_heat_demand = 0
        
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        
        self.unsub = async_track_state_change_event(hass, [current_temperature_sensor], self._async_on_change)
    
    @callback
    def _async_on_change(self, event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is not None:
            self.set_current_temperature(float(new_state.state))
        
    @property
    def room_id(self) -> str:
        return self._id

    def set_current_temperature(self, temperature: float) -> None:
        
        self._current_temperature = temperature
        
        self.recalculate()
        
    def recalculate(self) -> None:
        self._temperature_difference = self._target_temperature - self._current_temperature
        
        current_internal_v_external_dT = self._current_temperature - self.house.outdoor_temperature
        
        self._current_heat_demand = current_internal_v_external_dT * self._heat_loss
        
        target_internal_v_external_dT = self._target_temperature - self.house.outdoor_temperature
        
        self._target_heat_demand = target_internal_v_external_dT * self._heat_loss
        
        self.publish_updates()
        
        for radiator in self.radiators:
            radiator.publish_updates()
        
    @property
    def current_temperature(self):
        return self._current_temperature
    
    @property
    def temperature_difference(self):
        return self._temperature_difference
    
    @property
    def current_heat_demand(self):
        return self._current_heat_demand
    
    @property
    def target_heat_demand(self):
        return self._target_heat_demand
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.discard(callback)

    def publish_updates(self) -> None:
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        return True
    
class Radiator:
    
    def __init__(self, hass, radiator_id: str, name: str, nominal_output: int, room: Room, house: House) -> None:
        self._hass = hass
        self._id = radiator_id
        self.name = name
        self.nominal_output = nominal_output
        self._heat_output = 0
        self._room = room
        self._house = house
        
        
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        
        self.unsub = async_track_state_change_event(hass, ["sensor.radiator_sensor_8_mean_temperature"], self._async_on_change)
    
    @callback
    def _async_on_change(self, event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is not None:
            self.set_current_mean_temperature(float(new_state.state))
        
    @property
    def radiator_id(self) -> str:
        return self._id

    def set_current_mean_temperature(self, temperature: float) -> None:
        
        mwt_to_room_dt = temperature - self._room.current_temperature
        
        conversion_factor = math.pow(mwt_to_room_dt / 50, 1.3)
        
        self._heat_output = self.nominal_output * conversion_factor
        
        self.publish_updates()
        
    @property
    def heat_output(self):
        return self._heat_output
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    def publish_updates(self) -> None:
        for callback in self._callbacks:
            callback()

    @property
    def online(self) -> float:
        return True