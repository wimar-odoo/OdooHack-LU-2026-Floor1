/**
 * The fill gauge of the festival: a widget for an integer field (the seats taken), which displays
 * a progress bar and the text "taken / max (percentage %)": green below 70 %, orange below 90 %,
 * red from 90 %. The maximum is the field seats_max of the same record.
 */
import { Component, useProps } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class FillGauge extends Component {
    static template = "trivia_festival.FillGauge";
    props = useProps(standardFieldProps);

    get value() {
        return this.props.record.data[this.props.name] || 0;
    }

    get maxValue() {
        return this.props.record.data.seats_max || 0;
    }

    get percentage() {
        if (!this.maxValue) {
            return 0;
        }
        return Math.min(100, Math.round((100 * this.value) / this.maxValue));
    }

    get colorClass() {
        if (this.percentage >= 90) {
            return "bg-danger";
        }
        if (this.percentage >= 70) {
            return "bg-warning";
        }
        return "bg-success";
    }

    get label() {
        return `${this.value} / ${this.maxValue} (${this.percentage} %)`;
    }
}

export const fillGaugeField = {
    component: FillGauge,
    displayName: _t("Fill Gauge"),
    supportedTypes: ["integer", "float"],
    fieldDependencies: [{ name: "seats_max", type: "integer" }],
};

registry.category("fields").add("festival_fill_gauge", fillGaugeField);
