/**
 * TODO 2 - The welcome desk
 *
 * A client action (a screen of Odoo made of an OWL component) for the volunteers of the welcome
 * desk: the registrations of the festival, with a "Check in" button for the people who did not
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
import { Component, onWillStart, proxy, signal } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";  // eslint-disable-line no-unused-vars
import { useService } from "@web/core/utils/hooks";

export const FESTIVAL_ATTENDEES_UPDATED = "TRIVIA_FESTIVAL:ATTENDEES_UPDATED";

export class FestivalKiosk extends Component {
    static template = "trivia_festival.Kiosk";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = proxy({
            event: {},
            registrations: [],
            checkingIn: false,
        });
        this.search = signal("");
        onWillStart(() => this.loadData());
    }

    get filteredRegistrations() {
        const query = this.search().trim().toLocaleLowerCase();
        if (query === "") {
            return this.state.registrations;
        } else {
            const matchingRegistrations = [];
            for (const registration of this.state.registrations) {
                if (!registration.name) {
                    continue;
                }
                const name = registration.name.toLocaleLowerCase();
                if (name.includes(query)) {
                    matchingRegistrations.push(registration);
                }
            }
            return matchingRegistrations;
        }
    }

    async loadData() {
        // TODO 2: get the data of the welcome desk from the server, and put it in this.state
        const data = await this.orm.call("event.registration", "get_kiosk_data", []);
        this.state.event = data.event;
        this.state.registrations = data.registrations;
        this.env.bus.trigger(FESTIVAL_ATTENDEES_UPDATED, data.event.attendees);
    }

    async checkIn(registration) {
        // TODO 2: check the registration in on the server, welcome the attendee
        // (this.notification.add(message, { type: "success" })), then load the data again
        if (registration.attended) {
            return;
        }
        if (this.state.checkingIn) {
            return;
        }

        this.state.checkingIn = true;
        try {
            await this.orm.call("event.registration", "action_kiosk_checkin", [[registration.id]]);
            const message = _t("Welcome, %s!", registration.name);
            this.notification.add(message, { type: "success" });
            await this.loadData();
        } finally {
            this.state.checkingIn = false;
        }
    }
}

// TODO 2: add the component to the registry of the actions
registry.category("actions").add("festival_kiosk", FestivalKiosk);
