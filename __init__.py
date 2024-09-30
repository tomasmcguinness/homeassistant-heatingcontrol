"""Heating Control"""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta

from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.core import HomeAssistant, callback, Event, EventStateChangedData
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.frontend import  async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import Platform

from .const import SETTINGS_PANEL_URL

from .const import DOMAIN

from .house import House
from . import sensor

_LOGGER = logging.getLogger(__name__)

from homeassistant.const import (
    CONF_NAME
)

RADIATOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("mwt_sensor"): cv.string,
    }
)

ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("current_temperature_sensor"): cv.string,
        vol.Required("target_temperature"): cv.positive_int,
        vol.Required("radiators", default=[]): vol.All(
            cv.ensure_list, [RADIATOR_SCHEMA]
        )
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("rooms", default=[]): vol.All(
                    cv.ensure_list, [ROOM_SCHEMA]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Setup our Heating Control component"""

    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.async_set('heating_control.status', 'Staring')

    # Serve the panel and register it as a panel
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                SETTINGS_PANEL_URL,
                hass.config.path("custom_components/heating_control/heating-control-panel.js"),
                True,
            )
        ]
    )
    
    async_register_built_in_panel(
        hass=hass,
        component_name="custom",
        sidebar_title="Heating",
        sidebar_icon="mdi:fire",
        frontend_url_path="heating-control",
        require_admin=False,
        config={
            "_panel_custom": {
                "name": "heating-control-panel",
                "module_url": SETTINGS_PANEL_URL,
                "config": config
            }
        },
    )
    
    rooms_config = config.get(DOMAIN).get("rooms")
    
    h = House(hass, "NasebyRoad")
    
    for room in rooms_config:
        room_name = room.get("name")
        room_id = room_name.replace(" ", "_").lower()
        
        r = house.Room(hass, room_id, room_name, h)
        h.rooms.append(r)
        
    hass.data[DOMAIN] = h
    
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    
    # Listen for changes in all the sensors related to heating.
    # Loop through teh configuration and setup the various rooms.
    
    #entity_ids = ['sensor.radiator_8_flow_temperature']
    
    #unsub = async_track_state_change_event(hass, entity_ids, _async_on_change)
    
    #hass.async_create_task(async_manage_radiators(hass))
    
    
    #new_entities = []


        
        # Add the sensors for this room!
    
    #async_add_entities(new_entities)
    
    async def async_update_data():
        _LOGGER.info("Running heating control loop...")
        
        # The control loop has a simple job. Check the temperature of each room vs it's desired temperature.
        # If there is a shortfall:
        #
        # Adjust the radiator's output by changing the TRV.
        # If the TRV is full open, it may be necessary to increase the boiler's flow temperature.
        
        for room in h.rooms:
            _LOGGER.info("Processing " + room.name)
            
            #try:
                # First, work out the difference between the target temp and the actual temp!
                
            #current_temperature_sensor_name = room.get("current_temperature_sensor")
            #target_temperature = room.get("target_temperature")
            
            _LOGGER.info("Fetching current temperature sensor")
            
            current_temperature_entity = hass.states.get("sensor.sitting_room_temperature")
            
            if current_temperature_entity != None:
            
            #_LOGGER.info(current_temperature_entity)
            
            #_LOGGER.info(current_temperature_entity.state)
            #_LOGGER.info(current_temperature_entity.domain)
            
            #temperature_difference = target_temperature - int(current_temperature_entity.state)
            
                room.set_current_temperature(int(current_temperature_entity.state))
            
            #hass.states.async_set('heating_control.Hello_World', temperature_difference)

                
            # except:
            #     _LOGGER.error("Something went wrong")
        
        #h.publish_updates()
        
    #coordinator = DataUpdateCoordinator(hass, _LOGGER, name="HeatingControl", update_method = async_update_data, update_interval = timedelta(seconds=10))
    
    async def on_hass_started(event):
        _LOGGER.info("Home Assistant has started!")
        
       
        #unsub()
        #await coordinator.async_config_entry_first_refresh()

    hass.bus.async_listen_once('homeassistant_start', on_hass_started)
    
    #
    #await coordinator.async_config_entry_first_refresh()
    
    hass.states.async_set('heating_control.status', 'Running')
    
    return True

# @callback
# def _async_on_change(event: Event[EventStateChangedData]) -> None:
#     entity_id = event.data["entity_id"]
#     old_state = event.data["old_state"]
#     new_state = event.data["new_state"]
    
#     _LOGGER.info("State change for " + entity_id)
#     _LOGGER.info("State: " + new_state)
    
#     # Find the room connected to this entity and do something with the updated information!
#     #
#     for room in self.hass.data[DOMAIN].rooms:
#         room.set_current_temperature
        
    
async def async_manage_radiators(hass):
    while True:
        _LOGGER.warning("Checking radiators")
    