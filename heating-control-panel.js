import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

//import { loadHaForm } from './load-ha-form';

class ExamplePanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
    };
  }

  // requestUpdate() {
  //   (async () => await loadHaForm())();
  // }
  
  render() {

    let config = this.panel.config["_panel_custom"].config.heating_control;

    //console.log(this.hass.states["sensor.sitting_room_temperature"]);

    return html`
     <ha-top-app-bar-fixed>
      <div slot="title">Heating Control</div>
      <ha-config-section .narrow=${this.narrow} full-width>
        <ha-gauge value="75" style="--gauge-color: red">
        </ha-gauge>
        <ha-card>
         <h1 class="card-header">Boiler</h1>
        <div class="card-content">
        <ha-switch />
        </div>
        </ha-card>
        <ha-card>
          <h1 class="card-header">${config.rooms.map((room) => html`${room.name}` )}</h1>
          <div class="card-content">
            <table>
            <tbody>
            <tr>
            <td>Current Temperature</td><td>${this.hass.states["sensor.sitting_room_temperature"].state}°C</td>
            </tr>
            <tr>
            <td>Target Temperature</td><td>21°C</td>
            </tr>
            <tr>
            <td>Temperature Difference</td><td>${this.hass.states["sensor.sitting_room_temperature_difference"].state}°C</td>
            </tr>
            </tbody>
            </table>
          </div>
        </ha-card>
         </ha-config-section>
      </ha-top-app-bar-fixed>
    `;
  }

  static get styles() {
    return css`
      
    `;
  }

  
}

customElements.define("heating-control-panel", ExamplePanel);