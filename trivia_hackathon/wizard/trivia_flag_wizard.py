from odoo import fields, models

from ..models.trivia_challenge import WEDGES


class TriviaFlagWizard(models.TransientModel):
    _name = "trivia.flag.wizard"
    _description = "Submit a Trivia Flag"

    challenge_id = fields.Many2one("trivia.challenge", required=True, ondelete="cascade")
    flag = fields.Char(required=True)

    def action_submit(self):
        self.ensure_one()
        challenge = self.challenge_id
        if challenge._submit_flag(self.flag):
            message = self.env._("Correct flag! You won the %(wedge)s wedge.", wedge=WEDGES[challenge.wedge_color])
            return challenge._notify_result(message, "success", {"type": "ir.actions.client", "tag": "soft_reload"})
        return challenge._notify(self.env._("Wrong flag, keep digging!"), "danger")
