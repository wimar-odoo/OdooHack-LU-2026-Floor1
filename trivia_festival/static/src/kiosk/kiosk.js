import { Component, onWillStart, proxy, signal } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


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
        this.notification.add(_t("Welcome %s!", registration.name), { type: "success" });
        await this.loadData();
    }
}

registry.category("actions").add("festival_kiosk", FestivalKiosk);