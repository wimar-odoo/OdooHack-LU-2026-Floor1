
import { Component, onWillStart, proxy } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class FestivalSystrayCounter extends Component {
    static template = "trivia_festival.SystrayCounter";

    setup() {
        this.orm = useService("orm");
        this.state = proxy({ attendees: 0 });

        onWillStart(async () => {
            const data = await this.orm.call(
                "event.registration",
                "get_kiosk_data",
                []
            );

            this.state.attendees = data.event.attendees;
        });
    }
}

registry.category("systray").add(
    "trivia_festival.systray_counter",
    {
        Component: FestivalSystrayCounter,
    }
);