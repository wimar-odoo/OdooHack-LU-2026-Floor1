/**
 * Systray counter of the attendees of the festival.
 *
 * A small OWL component added to the systray (the icons at the top right of Odoo). It shows how
 * many attendees have already arrived, from the plugin shared with the welcome desk, so that a
 * check-in at the desk updates it at once.
 */
import { Component, usePlugin } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { FestivalAttendeesPlugin } from "@trivia_festival/festival_attendees_plugin";

export class FestivalAttendeeCounter extends Component {
    static template = "trivia_festival.AttendeeCounter";

    setup() {
        this.attendees = usePlugin(FestivalAttendeesPlugin);
        // not awaited: the navbar must not wait for the server to be drawn
        this.attendees.load();
    }
}

registry.category("systray").add(
    "trivia_festival.AttendeeCounter",
    { Component: FestivalAttendeeCounter },
    { sequence: 100 },
);
