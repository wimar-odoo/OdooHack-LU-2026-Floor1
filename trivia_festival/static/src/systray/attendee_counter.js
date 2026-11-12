/**
 * Systray counter of the attendees of the festival.
 *
 * A small OWL component added to the systray (the icons at the top right of Odoo). It shows how
 * many attendees have already arrived, read from the same server method as the welcome desk.
 */
import { Component, onWillStart, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class FestivalAttendeeCounter extends Component {
    static template = "trivia_festival.AttendeeCounter";

    setup() {
        this.orm = useService("orm");
        this.state = proxy({ attendees: 0 });
        onWillStart(() => this.loadCount());
    }

    async loadCount() {
        const data = await this.orm.call("event.registration", "get_kiosk_data", []);
        this.state.attendees = data.event.attendees;
    }
}

registry.category("systray").add(
    "trivia_festival.AttendeeCounter",
    { Component: FestivalAttendeeCounter },
    { sequence: 100 },
);
