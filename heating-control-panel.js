import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
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
  
  render() {

    let config = this.panel.config["_panel_custom"].config.heating_control;

    //<pre>${JSON.stringify(config, undefined, 2)}</pre>
        
    return html`
      <div class="page" style="background: transparent;">
        <h1>Heating Control</h1>
        <ha-card>
          <h2>${config.rooms.map((room) => html`${room.name}` )}<h2>
        </ha-card>
      </wired-card>
    `;
  }

  static get styles() {
    return css`
      :host {
        
      }
      wired-card {
        
      }
    `;
  }
}

customElements.define("heating-control-panel", ExamplePanel);