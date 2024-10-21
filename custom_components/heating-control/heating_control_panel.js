import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class ExamplePanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
    };
  }

  requestUpdate() {
    (async () => await loadHaForm())();
  }

  render() {

    let config = this.panel.config["_panel_custom"].config.heating_control;

    return html`
     <ha-top-app-bar-fixed>
      <div slot="title">Heating Control</div>
      <ha-config-section full-width>
        <ha-gauge value="75" style="--gauge-color: red">
        </ha-gauge>
        <ha-card class="main">
         <h1 class="card-header">House</h1>
        <div class="card-content">
         <table>
            <tbody>
              <tr>
                <td>Outdoor Temperature</td><td>${this.hass.states[config.outdoor_temperature_sensor].state}°C</td>
              </tr>
            </tbody>
          </table>
        </div>
        </ha-card>
        ${config.rooms.map((room) => html`
        <ha-card class="main">
          <h1 class="card-header">${room.name}</h1>
          <div class="card-content">
            <table>
              <tbody>
                <tr>
                  <td>Current Temperature</td><td>${this.hass.states[room.current_temperature_sensor].state}°C</td>
                </tr>
                <tr>
                  <td>Target Temperature</td><td>${room.target_temperature}°C</td>
                </tr>
                <tr>
                  <td>Temperature Difference</td><td>${this.hass.states["sensor.sitting_room_temperature_difference"].state}°C</td>
                </tr>
                <tr>
                  <td>Current Heat Demand</td><td>${this.hass.states[room.current_heat_demand_sensor].state}W</td>
                </tr>
                <tr>
                  <td>Target Heat Demand</td><td>${this.hass.states["sensor.sitting_room_target_heat_demand"].state}W</td>
                </tr>
              </tbody>
            </table>
            <div>
            ${room.radiators.map((radiator) => html`
              <ha-card>
                <h1 class="card-header">${radiator.name}</h1>
              <div class="card-content">
            <table>
            <tbody>
            <tr>
            <td>Flow Temperature</td><td>${this.hass.states["sensor.radiator_sensor_8_flow_temperature"].state}°C</td>
            </tr>
            <tr>
            <td>Mean Temperature</td><td>${this.hass.states["sensor.radiator_sensor_8_mean_temperature"].state}°C</td>
            </tr>
            <tr>
            <td>Return Temperature</td><td>${this.hass.states["sensor.radiator_sensor_8_return_temperature"].state}°C</td>
            </tr>
            <tr>
            <td>Heat Output</td><td>${this.hass.states["sensor.radiator_8_heat_output"].state}W</td>
            </tr>
            </tbody>
            </table>
            </div>



              </ha-card>
            ` )}
            </div>
          </div>
        </ha-card>
        ` )}
        </ha-config-section>
      </ha-top-app-bar-fixed>
    `;
  }

  static get styles() {
    return css`
      ha-card.main {
        margin-top: 24px;
        margin-left: 24px;
        margin-right: 24px;
      }
    `;
  }


}

customElements.define("heating-control-panel", ExamplePanel);