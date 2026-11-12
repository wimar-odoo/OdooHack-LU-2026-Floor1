/**
 * TODO 1 - The fill gauge of the festival
 *
 * A widget for an integer field (the seats taken), which displays a progress bar and the text
 * "taken / max (percentage %)": green below 70 %, orange below 90 %, red from 90 %.
 * The maximum is the field seats_max of the same record: this.props.record.data.seats_max
 *
 * Then add the widget to the registry of the fields, under the name festival_fill_gauge, and use
 * it on the form of the events (views/event_event_views.xml).
 *
 * ---------------------------------------------------------------------------------------------
 * OWL 3 (Odoo 20) in a nutshell. Careful, the documentation and the AI often show OWL 2:
 *   - in the templates, everything goes through "this":
 *         t-out="this.percentage"                   OWL 2: t-out="percentage"
 *         t-on-click="() => this.checkIn(record)"   (the variables of a t-foreach have no "this")
 *   - the props are declared with useProps():
 *         props = useProps(standardFieldProps);     OWL 2: static props = {...}
 *   - a reactive state (the template is rendered again when it changes) is created with proxy():
 *         this.state = proxy({ count: 0 });         OWL 2: useState({...})
 *   - an input bound with t-model needs a signal (not a property of a proxy):
 *         this.search = signal("");  then  t-model="this.search", and read it with this.search()
 *   - the services: this.orm = useService("orm"), then await this.orm.call(model, method, args)
 *   - the value of the field of a widget: this.props.record.data[this.props.name]
 * Example in Odoo: odoo/addons/web/static/src/views/fields/progress_bar/progress_bar_field.js
 * Debug: open Odoo with ?debug=assets to read the JavaScript errors in the console of the browser.
 * ---------------------------------------------------------------------------------------------
 */
import { Component, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const WARNING_RATE = 70;
const DANGER_RATE = 90;

export class FillGauge extends Component {
    static template = "trivia_festival.FillGauge";
    props = useProps(standardFieldProps);

    get value() {
        return this.props.record.data[this.props.name] || 0;
    }

    get max() {
        return this.props.record.data.seats_max || 0;
    }

    get percentage() {
        return this.max ? Math.round((100 * this.value) / this.max) : 0;
    }

    get barWidth() {
        return Math.min(this.percentage, 100);
    }

    get colorClass() {
        if (this.percentage >= DANGER_RATE) {
            return "bg-danger";
        }
        if (this.percentage >= WARNING_RATE) {
            return "bg-warning";
        }
        return "bg-success";
    }
}

export const fillGauge = {
    component: FillGauge,
    displayName: "Fill Gauge",
    supportedTypes: ["integer"],
    fieldDependencies: [{ name: "seats_max", type: "integer" }],
};

registry.category("fields").add("festival_fill_gauge", fillGauge);
