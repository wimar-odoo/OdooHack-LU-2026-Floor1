import { Component, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

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
        if (!this.max) {
            return 0;
        }
        return Math.round((this.value / this.max) * 100);
    }

    get barWidth() {
        return Math.min(this.percentage, 100);
    }

    get color() {
        if (this.percentage >= 90) {
            return "bg-danger";
        }
        if (this.percentage >= 70) {
            return "bg-warning";
        }
        return "bg-success";
    }
}

export const fillGauge = {
    component: FillGauge,
    supportedTypes: ["integer"],
    // makes sure seats_max is loaded with the record, even if it isn't in the view
    fieldDependencies: [{ name: "seats_max", type: "integer" }],
};

registry.category("fields").add("festival_fill_gauge", fillGauge);