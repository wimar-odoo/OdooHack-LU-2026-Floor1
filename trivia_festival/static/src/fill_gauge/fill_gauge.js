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
import { registry } from "@web/core/registry";  // eslint-disable-line no-unused-vars
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class FillGauge extends Component {
    static template = "trivia_festival.FillGauge";
    props = useProps(standardFieldProps);

    get value() {
        const value = this.props.record.data[this.props.name];
        if (value) {
            return value;
        } else {
            return 0;
        }
    }
    // TODO 1: the maximum, the percentage and the color (a Bootstrap class: bg-success, bg-warning or bg-danger)
    get max() {
        const max = this.props.record.data.seats_max;
        if (max) {
            return max;
        } else {
            return 0;
        }
    }

    get percentage() {
        if (this.max > 0) {
            return (this.value / this.max) * 100;
        } else {
            return 0;
        }
    }

    get width() {
        const percentage = this.percentage;
        if (percentage < 0) {
            return 0;
        } else if (percentage > 100) {
            return 100;
        } else {
            return percentage;
        }
    }

    get color() {
        const percentage = this.percentage;
        if (percentage >= 90) {
            return "bg-danger";
        } else if (percentage >= 70) {
            return "bg-warning";
        } else {
            return "bg-success";
        }
    }
}

// TODO 1: add the widget to the registry of the fields
registry.category("fields").add("festival_fill_gauge", {
    component: FillGauge,
    supportedTypes: ["integer"],
});
