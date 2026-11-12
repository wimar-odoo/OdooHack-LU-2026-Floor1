/**
 * The welcome desk: a client action for the volunteers of the entrance, which lists the
 * registrations of the festival with a "Check in" button for the people who did not arrive yet.
 */
import { Component, onWillStart, proxy, signal } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class FestivalKiosk extends Component {
    static template = "trivia_festival.Kiosk";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = proxy({ event: {}, registrations: [], loading: false });
        // ⭐ BONUS: the search box
        this.search = signal("");
        onWillStart(() => this.loadData());
    }

    async loadData() {
        const data = await this.orm.call("event.registration", "get_kiosk_data", []);
        this.state.event = data.event;
        this.state.registrations = data.registrations;
    }

    get filteredRegistrations() {
        const term = (this.search() || "").trim().toLowerCase();
        if (!term) {
            return this.state.registrations;
        }
        return this.state.registrations.filter((registration) =>
            (registration.name || "").toLowerCase().includes(term)
        );
    }

    async checkIn(registration) {
        if (this.state.loading) {
            return;
        }
        this.state.loading = true;
        try {
            await this.orm.call("event.registration", "action_kiosk_checkin", [[registration.id]]);
            this.notification.add(_t("Welcome %s!", registration.name), { type: "success" });
            await this.loadData();
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("festival_kiosk", FestivalKiosk);
