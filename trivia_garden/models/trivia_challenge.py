import psycopg2

from odoo import Command, fields, models
from odoo.exceptions import UserError
from odoo.tools import mute_logger
from odoo.tools.safe_eval import datetime, dateutil, safe_eval, time

from odoo.addons.trivia_hackathon.models.trivia_challenge import CheckFailed, eval_expression, get_arch, require

FEE_MODEL = "garden.membership.fee"
FEE_DATA_COUNT = 41  # fees of data/garden_membership_fee_data.xml
REFUSALS = (UserError, psycopg2.IntegrityError)  # ValidationError is a UserError


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "The Garden Fees": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_garden(self):
        _ = self._get_report_env()._
        env = self.env
        Partner = env["res.partner"]
        today = fields.Date.context_today(self)
        this_year = today.year

        def fee_model():
            require(FEE_MODEL in env, _("The model %(model)s does not exist yet (mission 1).", model=FEE_MODEL))
            return env[FEE_MODEL]

        def field_of(model, name, types, mission):
            field = model._fields.get(name)
            require(field, _(
                "The field %(field)s of %(model)s is missing (mission %(mission)s).",
                field=name, model=model._name, mission=mission,
            ))
            require(field.type in types, _(
                "The field %(field)s of %(model)s must be a %(types)s field, not a %(type)s field.",
                field=name, model=model._name, types=" / ".join(types), type=field.type,
            ))
            return field

        def create_member(paid_years=()):
            Fee = fee_model()
            vals = {"name": "Checker member"}
            if "membership_type" in Partner._fields:
                vals["membership_type"] = "individual"
            member = Partner.create(vals)
            Fee.create([{"partner_id": member.id, "year": year, "state": "paid"} for year in paid_years])
            return member

        def from_db(record, field_name):
            env.flush_all()
            env.invalidate_all()
            return record[field_name]

        def refused(function):
            """ Return whether ``function`` is refused by a constraint; when it is not, its changes are kept. """
            try:
                # a refusal by the database is expected here: don't log it as an error
                with mute_logger("odoo.sql_db"), env.cr.savepoint():
                    function()
                    env.flush_all()
            except REFUSALS:
                return True
            return False

        def check_fee_model():
            Fee = fee_model()
            partner = field_of(Fee, "partner_id", ["many2one"], 1)
            require(partner.comodel_name == "res.partner" and partner.required,
                    _("partner_id must be a required link to a contact (res.partner)."))
            require(field_of(Fee, "year", ["integer"], 1).required, _("The year of a fee must be required."))
            field_of(Fee, "amount", ["float", "monetary"], 1)
            state = field_of(Fee, "state", ["selection"], 1)
            require(set(state.get_values(env)) == {"draft", "paid"},
                    _("The state of a fee must have exactly two values: draft and paid."))
            require(Fee.default_get(["state"]).get("state") == "draft", _("A new fee must be in draft."))
            field_of(Fee, "payment_date", ["date"], 1)

        def check_unique_fee():
            Fee = fee_model()
            member = create_member()
            Fee.create({"partner_id": member.id, "year": this_year})
            require(not refused(lambda: Fee.create({"partner_id": member.id, "year": this_year - 1})),
                    _("A member must be able to pay the fees of different years."))
            require(refused(lambda: Fee.create({"partner_id": member.id, "year": this_year})),
                    _("A member can pay two fees for the same year: add a constraint (mission 1)."))
            # a constraint on (partner_id, year, state) would accept a paid fee next to the draft one
            require(refused(lambda: Fee.create({"partner_id": member.id, "year": this_year, "state": "paid"})), _(
                "A member can have a draft fee and a paid fee for the same year: "
                "the constraint must be on the member and the year only (mission 1).",
            ))

        def check_mark_paid():
            Fee = fee_model()
            require(hasattr(Fee, "action_mark_paid"), _("The method action_mark_paid() is missing (mission 1)."))
            member = create_member()
            fees = Fee.create([{"partner_id": member.id, "year": year} for year in (this_year - 1, this_year)])
            fees.action_mark_paid()
            require(set(fees.mapped("state")) == {"paid"},
                    _("action_mark_paid() must mark the fees as paid, also when called on several fees."))
            require(set(fees.mapped("payment_date")) <= {today, fields.Date.today()},
                    _("action_mark_paid() must set the payment date to today."))

        def check_access():
            Fee = fee_model()
            user = env["res.users"].with_context(no_reset_password=True).create({
                "name": "Checker user",
                "login": "trivia.garden.checker",
                "group_ids": [Command.set([env.ref("base.group_user").id])],
            })
            for operation in ("read", "create", "write", "unlink"):
                require(Fee.with_user(user).has_access(operation), _(
                    "The internal users are not allowed to %(operation)s the fees: see security/ir.access.csv (mission 2).",
                    operation=operation,
                ))

        def check_fee_views():
            Fee = fee_model()
            for view_type in ("list", "form"):
                require(env["ir.ui.view"].search_count([("model", "=", FEE_MODEL), ("type", "=", view_type)]),
                        _("The fees have no %(view_type)s view (mission 3).", view_type=view_type))
            form = get_arch(Fee, "form")
            require(form.xpath("//header//field[@name='state'][@widget='statusbar']"),
                    _("The form of the fees must display the state as a statusbar, in its header."))
            buttons = form.xpath("//header//button[@name='action_mark_paid']")
            require(buttons, _("The form of the fees must have a button calling action_mark_paid(), in its header."))
            invisible = buttons[0].get("invisible", "")
            require(
                "state" in invisible
                and eval_expression(invisible, {"state": "draft"}) is not True
                and eval_expression(invisible, {"state": "paid"}) is not False,
                _("The button calling action_mark_paid() must only be visible on draft fees."),
            )
            actions = env["ir.actions.act_window"].search([("res_model", "=", FEE_MODEL)])
            require(actions, _("No action opens the fees (mission 3)."))
            require(env["ir.ui.menu"].sudo().search_count([("action", "in", [f"{a._name},{a.id}" for a in actions])]),
                    _("No menu opens the fees (mission 3)."))

        def check_last_paid_year():
            Fee = fee_model()
            field = field_of(Partner, "last_paid_year", ["integer"], 4)
            require(field.compute and field.store, _("last_paid_year must be a stored computed field (mission 4)."))
            field_of(Partner, "fee_ids", ["one2many"], 4)
            member = create_member()
            old_fee, new_fee = Fee.create([
                {"partner_id": member.id, "year": this_year - 2, "state": "paid"},
                {"partner_id": member.id, "year": this_year, "state": "draft"},
            ])

            def expect(expected, situation):
                value = from_db(member, "last_paid_year")
                require(value == expected, _(
                    "last_paid_year is %(value)s instead of %(expected)s %(situation)s.",
                    value=value, expected=expected, situation=situation,
                ))

            expect(this_year - 2, _("with a fee paid two years ago and a draft fee this year"))
            new_fee.state = "paid"
            expect(this_year, _("after paying the fee of this year"))
            new_fee.year = this_year + 1
            expect(this_year + 1, _("after changing the year of a paid fee"))
            new_fee.unlink()
            expect(this_year - 2, _("after deleting a fee"))
            old_fee.state = "draft"
            expect(0, _("when no fee is paid"))

        def check_contact_form():
            field_of(Partner, "fee_ids", ["one2many"], 4)
            form = get_arch(Partner, "form", env.ref("base.view_partner_form").id)
            for name in ("membership_type", "member_since", "last_paid_year", "fee_ids"):
                require(form.xpath(f"//page//field[@name='{name}']"), _(
                    "The field %(field)s is not displayed in a page of the contact form (mission 5).", field=name,
                ))

        def check_filter():
            field_of(Partner, "last_paid_year", ["integer"], 4)
            # the search view of the Contacts app, and not the default one: a new primary search view on res.partner
            # may become the default view, while the Contacts app keeps showing base.view_res_partner_filter
            search = get_arch(Partner, "search", env.ref("base.view_res_partner_filter").id)
            filters = search.xpath("//filter[contains(@domain, 'last_paid_year')]")
            require(filters, _(
                "The contacts have no filter on last_paid_year in their search view (base.view_res_partner_filter): "
                "inherit this view (mission 5).",
            ))
            up_to_date = create_member([this_year - 1, this_year])
            late = create_member([this_year - 1])
            members = up_to_date | late
            context = {
                "context_today": lambda: today,
                "current_date": today.strftime("%Y-%m-%d"),
                "datetime": datetime,
                "time": time,
                "relativedelta": dateutil.relativedelta.relativedelta,
                "uid": env.uid,
            }
            for node in filters:
                try:
                    domain = list(safe_eval(node.get("domain"), context))
                    found = Partner.search(domain + [("id", "in", members.ids)])
                except Exception:  # noqa: BLE001 - try the next filter
                    continue
                if found == late:
                    return
            raise CheckFailed(_("The filter on last_paid_year must only keep the members who did not pay the current year."))

        def check_plots():
            fee_model()
            field_of(Partner, "last_paid_year", ["integer"], 4)
            Plot = env["garden.plot"]
            site = env["garden.site"].create({"name": "Checker site"})
            plot, other_plot = Plot.create([
                {"name": "Checker plot 1", "site_id": site.id},
                {"name": "Checker plot 2", "site_id": site.id},
            ])
            up_to_date = create_member([this_year - 1, this_year])
            late = create_member([this_year - 1])
            require(not refused(lambda: plot.write({"tenant_id": up_to_date.id})),
                    _("A member who paid the fee of this year must be able to rent a plot."))
            require(refused(lambda: other_plot.write({"tenant_id": up_to_date.id})),
                    _("A member can rent two plots (mission 6)."))
            require(refused(lambda: other_plot.write({"tenant_id": late.id})),
                    _("A member who did not pay the fee of this year can rent a plot (mission 6)."))
            require(refused(lambda: Plot.create({"name": "Checker plot 3", "site_id": site.id, "tenant_id": late.id})),
                    _("A plot can be created for a member who did not pay the fee of this year (mission 6)."))

        def check_data():
            count = env["ir.model.data"].search_count([("module", "=", "trivia_garden"), ("model", "=", FEE_MODEL)])
            require(count >= FEE_DATA_COUNT, _(
                "The fees of the members are not loaded: declare data/garden_membership_fee_data.xml in the manifest (mission 7).",
            ))

        def check_smart_button():
            field_of(Partner, "fee_ids", ["one2many"], 4)
            form = get_arch(Partner, "form", env.ref("base.view_partner_form").id)
            require(any(
                "fee" in " ".join([button.get("name") or "", *button.xpath(".//field/@name")])
                for button in form.xpath("//div[@name='button_box']//button")
            ), _("The button box of the contact form has no smart button about the fees."))

        def check_plot_kanban():
            require(env["ir.ui.view"].search_count([("model", "=", "garden.plot"), ("type", "=", "kanban")]),
                    _("The plots have no kanban view."))
            actions = env["ir.actions.act_window"].search([("res_model", "=", "garden.plot")])
            require(any("kanban" in action.view_mode for action in actions),
                    _("The action of the plots does not open the kanban view."))
            grouped = get_arch(env["garden.plot"], "kanban").get("default_group_by") == "site_id" or any(
                "site_id" in (action.context or "") for action in actions
            )
            require(grouped, _("The kanban view of the plots is not grouped by site."))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. The membership fees"), check_fee_model, False),
            (_("1. One fee per member and per year"), check_unique_fee, False),
            (_("1. Mark a fee as paid"), check_mark_paid, False),
            (_("2. Access rights to the fees"), check_access, False),
            (_("3. Views and menu of the fees"), check_fee_views, False),
            (_("4. Last paid year of the members"), check_last_paid_year, False),
            (_("5. Membership page of the contact form"), check_contact_form, False),
            (_("5. Filter of the members not up to date"), check_filter, False),
            (_("6. Rules of the plots"), check_plots, False),
            (_("7. Fees of the members"), check_data, False),
            (_("Smart button of the fees on the contact form"), check_smart_button, True),
            (_("Kanban view of the plots, grouped by site"), check_plot_kanban, True),
        ]]
