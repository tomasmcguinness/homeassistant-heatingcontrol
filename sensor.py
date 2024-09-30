import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None):
    _LOGGER.info("Setting up sensoros for Heating Control")
    
    if discovery_info is None:
      return
    
    h = hass.data[DOMAIN]
    
    new_devices = []
    
    for room in h.rooms: 
        new_devices.append(TemperatureDifferenceSensor(room))
        new_devices.append(HeatDemandSensor(room))
        
        for radiator in room.radiators:
            new_devices.append(RadiatorOutputSensor(radiator))
    
    if new_devices:
        async_add_entities(new_devices)
    
class RoomSensorBase(Entity):
    
    should_poll = False

    def __init__(self, room):
        self._room = room

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._room.room_id)}}

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        return True

    async def async_added_to_hass(self):
        # Sensors should also register callbacks to HA when their state changes
        self._room.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._room.remove_callback(self.async_write_ha_state)


class TemperatureDifferenceSensor(RoomSensorBase):
    
    device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, room):
        super().__init__(room)

        self._attr_unique_id = f"{self._room.room_id}_temperature_difference"

        self._attr_name = f"{self._room.name} Temperature Difference"

        self._state = 0

    @property
    def state(self):
        return self._room.temperature_difference
    
class HeatDemandSensor(RoomSensorBase):
    
    device_class = SensorDeviceClass.POWER

    def __init__(self, room):
        super().__init__(room)

        self._attr_unique_id = f"{self._room.room_id}_heat_demand"

        self._attr_name = f"{self._room.name} Heat Demand"

        self._state = 0

    @property
    def state(self):
        return self._room.heat_demand
    
class RadiatorSensorBase(Entity):
    
    should_poll = False

    def __init__(self, radiator):
        self._radiator = radiator

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._radiator.radiator_id)}}

    @property
    def available(self) -> bool:
        return True

    async def async_added_to_hass(self):
        self._radiator.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._radiator.remove_callback(self.async_write_ha_state)


class RadiatorOutputSensor(RadiatorSensorBase):
    
    device_class = SensorDeviceClass.POWER

    def __init__(self, radiator):
        super().__init__(radiator)

        self._attr_unique_id = f"{self._radiator.radiator_id}_heat_output"

        self._attr_name = f"{self._radiator.name} Heat Output"

        self._state = 0

    @property
    def state(self):
        return self._radiator.heat_output