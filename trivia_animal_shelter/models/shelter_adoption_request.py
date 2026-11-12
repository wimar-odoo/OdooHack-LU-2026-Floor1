from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ShelterAdoptionRequest(models.Model):
    _name = "shelter.adoption.request"
    _description = "Adoption Request"
    _order = "create_date desc, id desc"

    animal_id = fields.Many2one("shelter.animal", string="Animal", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Applicant", required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    message = fields.Text()
    state = fields.Selection(
        [("new", "New"), ("accepted", "Accepted"), ("refused", "Refused")],
        string="Status", required=True, default="new",
    )

    def action_accept(self):
        self.state = "accepted"
        self.animal_id.adopted = True

    def action_refuse(self):
        self.state = "refused"

    # ----------------------------------------------------------------------------
    # TODO 4 - The adoption request sent from the website
    # ----------------------------------------------------------------------------

    @api.model
    def _create_from_website(self, animal, values):
        """ Create the adoption request sent by a visitor of the website for ``animal``,
        from the ``values`` posted by the form (name, email, phone, message).

        * the visitors (public user) have no access rights on the requests;
        * only the fields of the form can be set: a visitor must not be able to choose
          the animal or the status of the request;
        * only an adoptable animal (TODO 1) can be requested.

        :return: the new request
        """
        
        animal.ensure_one()
        if animal not in self.env["shelter.animal"]._get_adoptable_animals():
            raise ValidationError(self.env._("This animal cannot be adopted."))
        vals = {
            field_name: (values.get(field_name) or "").strip() or False
            for field_name in ("name", "email", "phone", "message")
        }
        if not vals["name"] or not vals["email"]:
            raise ValidationError(self.env._("Your name and your email are required."))
        vals["animal_id"] = animal.id
        return self.sudo().create(vals)
