/**
 * TODO 2 - The welcome desk
 *
 * A client action (a screen of Odoo made of an OWL component) for the volunteers of the welcome
 * desk: 
 * 
 * the registrations of the festival, with a "Check in" button for the people who did not
 * arrive yet. Read the OWL 3 cheat sheet at the top of fill_gauge.js.
 *
 * The server side is ready (models/event_registration.py), call it with the service "orm":
 *   - await this.orm.call("event.registration", "get_kiosk_data", [])
 *         returns { event: {...}, registrations: [{ id, name, ticket, attended }, ...] }
 *   - await this.orm.call("event.registration", "action_kiosk_checkin", [[registrationId]])
 *
 * Then add the component to the registry of the actions, under the name festival_kiosk, and
 * create its client action and its menu in views/menus.xml.
 */
import { Component, onWillStart, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";  // eslint-disable-line no-unused-vars
import { useService } from "@web/core/utils/hooks";

export class FestivalKiosk extends Component {
    static template = "trivia_festival.Kiosk";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = proxy({ event: {}, registrations: [] });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        const data = await this.orm.call("event.registration", "get_kiosk_data", []);
        this.state.event = data.event;
        this.state.registrations = data.registrations;
    }

    async checkIn(registration) {
        await this.orm.call("event.registration", "action_kiosk_checkin", [[registration.id]]);
        this.notification.add(`Welcome, ${registration.name}!`, { type: "success" });
        await this.loadData();
    }
}

registry.category("actions").add("festival_kiosk", FestivalKiosk);
