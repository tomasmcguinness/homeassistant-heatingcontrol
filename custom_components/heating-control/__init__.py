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
        vol.Required("mean_temperature_sensor"): cv.string,
        vol.Required("flow_temperature_sensor"): cv.string,
        vol.Required("return_temperature_sensor"): cv.string,
        vol.Required("nominal_output"): cv.positive_int,
    }
)

ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required("current_temperature_sensor"): cv.string,
        vol.Required("target_temperature"): cv.positive_int,
        vol.Required("radiators", default=[]): vol.All(
            cv.ensure_list, [RADIATOR_SCHEMA]
        ),
        vol.Required("heat_loss"): cv.positive_int
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("outdoor_temperature_sensor"): cv.string,
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
    
    root_config = config.get(DOMAIN)
    rooms_config = root_config.get("rooms")
    
    h = House(hass, "NasebyRoad", root_config.get("outdoor_temperature_sensor") )
    
    for room in rooms_config:
        room_name = room.get("name")
        room_id = room_name.replace(" ", "_").lower()
        current_temperature_sensor = room.get("current_temperature_sensor")
        target_temperature = room.get("target_temperature")
        heat_loss = room.get("heat_loss")
        
        r = house.Room(hass, room_id, room_name, current_temperature_sensor, target_temperature, heat_loss, h)
        h.rooms.append(r)
        
        radiators = room.get("radiators")
        
        for radiator in radiators:
            radiator_name = radiator.get("name")
            radiator_id = radiator_name.replace(" ", "_").lower()
            nominal_output = radiator.get("nominal_output")
            
            rad = house.Radiator(hass, radiator_id, radiator_name, nominal_output, r, h)
            
            r.radiators.append(rad)
        
        
    hass.data[DOMAIN] = h
    
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    
    async def on_hass_started(event):
        _LOGGER.info("Home Assistant has started!")
        
    hass.bus.async_listen_once('homeassistant_start', on_hass_started)
    
    hass.states.async_set('heating_control.status', 'Running')
    
    return True

async def async_manage_radiators(hass):
    while True:
        _LOGGER.warning("Checking radiators")
    