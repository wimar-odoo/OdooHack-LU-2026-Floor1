import { Component, onWillStart, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// shared state: the welcome desk updates it, so the counter changes right after a check-in
export const festivalState = proxy({ attendees: 0, seatsMax: 0 });

export class AttendeesCounter extends Component {
    static template = "trivia_festival.AttendeesCounter";

    setup() {
        this.orm = useService("orm");
        this.state = festivalState;
        onWillStart(() => this.load());
    }

    async load() {
        try {
            const data = await this.orm.call("event.registration", "get_kiosk_data", []);
            this.state.attendees = data.event.attendees;
            this.state.seatsMax = data.event.seats_max;
        } catch {
            // users without access to the events just see 0
        }
    }
}

registry.category("systray").add(
    "trivia_festival.AttendeesCounter",
    { Component: AttendeesCounter },
    { sequence: 20 },
);