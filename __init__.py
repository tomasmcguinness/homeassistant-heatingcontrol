"""Heating Control"""
import asyncio
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from http import HTTPStatus
from aiohttp import web

from homeassistant.components import mqtt

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType

from homeassistant.components.frontend import add_extra_js_url, async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig

from .const import SETTINGS_PANEL_URL

#from . import websocket_api

DOMAIN = "heating_control"
_LOGGER = logging.getLogger(__name__)

from homeassistant.const import (
    CONF_NAME
)

ROOM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("rooms", default=[]): vol.All(
                    cv.ensure_list, [ROOM_SCHEMA]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

# async def async_setup_entry(hass: HomeAssistant, config: ConfigType) -> bool:
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup our skeleton component."""

    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.async_set('heating_control.Hello_World', 'Works!')

    # Serve the Browser Mod controller and add it as extra_module_url
    # await hass.http.async_register_static_paths(
    #     [
    #         StaticPathConfig(
    #             FRONTEND_SCRIPT_URL,
    #             hass.config.path("custom_components/browser_mod/browser_mod.js"),
    #             True,
    #         )
    #     ]
    # )
    # add_extra_js_url(hass, FRONTEND_SCRIPT_URL)
    
    # hass.http.register_view(HeatingControlView())

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
    
    # Return boolean to indicate that initialization was successfully.
    return True

# class HeatingControlView(HomeAssistantView):
   
#     url = "/api/heating-control/period"
#     name = "api:history:view-period"
#     extra_urls = ["/api/history/period/{datetime}"]

#     async def get(
#         self, request: web.Request, datetime: str | None = None
#     ) -> web.Response:
#         """Return history over a period of time."""
#         datetime_ = None
#         query = request.query

#         if datetime and (datetime_ := dt_util.parse_datetime(datetime)) is None:
#             return self.json_message("Invalid datetime", HTTPStatus.BAD_REQUEST)

#         if not (entity_ids_str := query.get("filter_entity_id")) or not (
#             entity_ids := entity_ids_str.strip().lower().split(",")
#         ):
#             return self.json_message(
#                 "filter_entity_id is missing", HTTPStatus.BAD_REQUEST
#             )

#         hass = request.app[KEY_HASS]

#         for entity_id in entity_ids:
#             if not hass.states.get(entity_id) and not valid_entity_id(entity_id):
#                 return self.json_message(
#                     "Invalid filter_entity_id", HTTPStatus.BAD_REQUEST
#                 )

#         now = dt_util.utcnow()
#         if datetime_:
#             start_time = dt_util.as_utc(datetime_)
#         else:
#             start_time = now - _ONE_DAY

#         if start_time > now:
#             return self.json([])

#         if end_time_str := query.get("end_time"):
#             if end_time := dt_util.parse_datetime(end_time_str):
#                 end_time = dt_util.as_utc(end_time)
#             else:
#                 return self.json_message("Invalid end_time", HTTPStatus.BAD_REQUEST)
#         else:
#             end_time = start_time + _ONE_DAY

#         include_start_time_state = "skip_initial_state" not in query
#         significant_changes_only = query.get("significant_changes_only", "1") != "0"

#         minimal_response = "minimal_response" in request.query
#         no_attributes = "no_attributes" in request.query

#         if (
#             (end_time and not has_recorder_run_after(hass, end_time))
#             or not include_start_time_state
#             and entity_ids
#             and not entities_may_have_state_changes_after(
#                 hass, entity_ids, start_time, no_attributes
#             )
#         ):
#             return self.json([])

#         return cast(
#             web.Response,
#             await get_instance(hass).async_add_executor_job(
#                 self._sorted_significant_states_json,
#                 hass,
#                 start_time,
#                 end_time,
#                 entity_ids,
#                 include_start_time_state,
#                 significant_changes_only,
#                 minimal_response,
#                 no_attributes,
#             ),
#         )