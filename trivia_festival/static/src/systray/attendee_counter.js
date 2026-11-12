/**
 * ⭐ BONUS - The counter of the attendees in the systray (the icons at the top right).
 */
import { Component, onWillStart, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AttendeeCounter extends Component {
    static template = "trivia_festival.AttendeeCounter";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = proxy({ attendees: 0, seatsMax: 0, loaded: false });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        try {
            const data = await this.orm.call("event.registration", "get_kiosk_data", []);
            this.state.attendees = data.event.attendees;
            this.state.seatsMax = data.event.seats_max;
            this.state.loaded = true;
        } catch {
            this.state.loaded = false;
        }
    }

    openKiosk() {
        this.action.doAction({ type: "ir.actions.client", tag: "festival_kiosk", name: "Welcome Desk" });
    }
}

registry.category("systray").add("trivia_festival.attendee_counter", { Component: AttendeeCounter }, { sequence: 50 });
