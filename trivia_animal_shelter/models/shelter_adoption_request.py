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
        """Create a request only if the animal is available for adoption."""
        animal = animal.sudo().exists()
        if not animal:
            raise ValidationError("This animal is not available for adoption.")

        animals = self.env["shelter.animal"].sudo()._get_adoptable_animals()
        if animal.id not in animals.ids:
            raise ValidationError("This animal is not available for adoption.")

        name = (values.get("name") or "").strip()
        email = (values.get("email") or "").strip()
        phone = (values.get("phone") or "").strip()
        message = (values.get("message") or "").strip()

        if not name or not email or "@" not in email:
            raise ValidationError("Please enter your name and a valid email address.")
        if len(name) > 120 or len(email) > 254 or len(phone) > 40 or len(message) > 5000:
            raise ValidationError("One of the form fields is too long.")

        # Only these fields are saved. Visitors cannot set animal_id or state.
        return self.sudo().create({
            "animal_id": animal.id,
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
        })
