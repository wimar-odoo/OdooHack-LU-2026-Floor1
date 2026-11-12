import { Component, onMounted, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useBus, useService } from "@web/core/utils/hooks";
import { FESTIVAL_ATTENDEES_UPDATED } from "../kiosk/kiosk";

export class AttendeeCounter extends Component {
    static template = "trivia_festival.AttendeeCounter";

    setup() {
        this.orm = useService("orm");
        this.state = proxy({ attendees: null });
        useBus(this.env.bus, FESTIVAL_ATTENDEES_UPDATED, (updateEvent) => {
            this.state.attendees = updateEvent.detail;
        });
        onMounted(() => this.loadCount());
    }

    async loadCount() {
        const canAccessWelcomeDesk = await user.hasGroup("event.group_event_registration_desk");
        if (!canAccessWelcomeDesk) {
            return;
        }
        try {
            const data = await this.orm.call("event.registration", "get_kiosk_data", []);
            if (this.state.attendees === null) {
                this.state.attendees = data.event.attendees;
            }
        } catch {
            // The festival may not be accessible in the current company.
        }
    }
}

registry.category("systray").add("trivia_festival.attendee_counter", {
    Component: AttendeeCounter,
});
