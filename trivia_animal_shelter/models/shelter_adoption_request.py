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
        if not animal.exists() or not animal.is_published or animal.adopted:
            raise ValidationError("This animal is not available for adoption.")

        form_values = {
            field: (values.get(field) or "").strip()
            for field in ("name", "email", "phone", "message")
        }
        if not form_values["name"] or not form_values["email"]:
            raise ValidationError("Please provide your name and email address.")

        form_values["animal_id"] = animal.id
        form_values["state"] = "new"
        return self.sudo().create(form_values)
