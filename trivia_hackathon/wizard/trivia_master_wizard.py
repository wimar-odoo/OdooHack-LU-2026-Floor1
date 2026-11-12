from odoo import api, fields, models

from ..models.trivia_master import TriviaMasterError

CLOSE = {"type": "ir.actions.act_window_close"}
SOFT_RELOAD = {"type": "ir.actions.client", "tag": "soft_reload"}


class TriviaMasterWizard(models.TransientModel):
    """ Connection of the team's database to the master database of the organisers.

    The URL and the team are saved in the database, the PIN only in the session of the user (see trivia.master).
    Opened from the menu, or by a check (or a flag) when the connection is not complete: then the context holds the
    action that the check returned (``trivia_master_next_action``), run once the connection is saved or skipped. """
    _name = "trivia.master.wizard"
    _description = "Trivia Master Connection"

    # required in the view only, when opened from the menu: opened by a check, "Later" must close it even when empty
    # (a button saves the record before calling its method), action_save() checks them
    url = fields.Char(string="Master URL")
    team = fields.Char(help="Name of your team, given by the organisers, e.g. Team03.")
    # emptied once the connection is saved: the PIN is only kept in the session of the user
    pin = fields.Char(string="PIN", help="Secret code of your team, given by the organisers.")
    from_check = fields.Boolean(default=lambda self: bool(self.env.context.get("trivia_master_from_check")))

    @api.model
    def default_get(self, fields):
        values = super().default_get(fields)
        config = self.env["trivia.master"]._get_config()
        # the PIN of the session is never sent back to the browser
        values.update({key: config[key] for key in ("url", "team") if key in fields and config[key]})
        return values

    def action_save(self):
        """ Check the connection, save it, and send the results that were not sent yet. """
        self.ensure_one()
        master = self.env["trivia.master"]
        config = {"url": (self.url or "").strip().rstrip("/"), "team": (self.team or "").strip(), "pin": (self.pin or "").strip()}
        if not all(config.values()):
            return self.env["trivia.challenge"]._notify(
                self.env._("Enter the URL of the master database, the name of your team and its PIN."), "danger",
            )
        try:
            result = master._post("/hackathon/ping", config=config)
        except TriviaMasterError as e:
            return self.env["trivia.challenge"]._notify(str(e), "danger")
        master._set_config(self.url, self.team, self.pin)
        self.pin = False
        challenges = self.env["trivia.challenge"].sudo().search([("sync_uid", "!=", False), ("sync_state", "!=", "sent")])
        challenges._send_to_master()
        message = result.get("message") or self.env._("Connected to the master database.")
        return self.env["trivia.challenge"]._notify(message, "success", self._get_next_action())

    def action_skip(self):
        """ Close the wizard without connecting: the results wait until the connection is saved. """
        self.pin = False
        return self._get_next_action()

    def _get_next_action(self):
        """ The action returned by the check that opened the wizard, which also closes the wizard. """
        action = self.env.context.get("trivia_master_next_action")
        if not action:
            return CLOSE
        params = action.get("params") or {}
        if action.get("tag") == "display_notification" and params.get("next", CLOSE) == SOFT_RELOAD:
            # closing the wizard reloads the view of the check button
            action = {**action, "params": {**params, "next": CLOSE}}
        return action
