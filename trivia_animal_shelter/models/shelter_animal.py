from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

SPECIES = [
    ("cat", "Cat"),
    ("dog", "Dog"),
    ("rabbit", "Rabbit"),
    ("bird", "Bird"),
]
SPECIES_EMOJI = {"cat": "🐱", "dog": "🐶", "rabbit": "🐰", "bird": "🐦"}


class ShelterAnimal(models.Model):
    _name = "shelter.animal"
    _inherit = ["website.published.mixin"]
    _description = "Shelter Animal"
    _order = "name"

    name = fields.Char(required=True)
    species = fields.Selection(SPECIES, required=True, default="cat")
    species_emoji = fields.Char(compute="_compute_species_emoji")
    breed = fields.Char(translate=True)
    sex = fields.Selection([("female", "Female"), ("male", "Male")])
    birth_date = fields.Date()
    age = fields.Char(compute="_compute_age")
    description = fields.Text(translate=True)
    adopted = fields.Boolean()
    request_ids = fields.One2many("shelter.adoption.request", "animal_id", string="Adoption Requests")
    request_count = fields.Integer(string="Requests", compute="_compute_request_count")

    @api.depends("species")
    def _compute_species_emoji(self):
        for animal in self:
            animal.species_emoji = SPECIES_EMOJI.get(animal.species, "🐾")

    @api.depends("birth_date")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for animal in self:
            if not animal.birth_date:
                animal.age = False
                continue
            delta = relativedelta(today, animal.birth_date)
            if delta.years:
                animal.age = self.env._("%(count)s year(s)", count=delta.years)
            else:
                animal.age = self.env._("%(count)s month(s)", count=max(delta.months, 1))

    def _compute_website_url(self):
        super()._compute_website_url()
        for animal in self:
            if animal.id:
                animal.website_url = f"/adopt/{self.env['ir.http']._slug(animal)}"

    @api.depends("request_ids")
    def _compute_request_count(self):
        for animal in self:
            animal.request_count = len(animal.request_ids)

    @api.model
    def _get_species(self):
        """ Return the species as a list of (key, label), e.g. [('cat', "Cat"), ...]. """
        return self._fields["species"]._description_selection(self.env)

    def action_view_requests(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Adoption Requests"),
            "res_model": "shelter.adoption.request",
            "view_mode": "list,form",
            "domain": [("animal_id", "=", self.id)],
            "context": {"default_animal_id": self.id},
        }

    # ----------------------------------------------------------------------------
    # TODO 1 - The adoptable animals
    # ----------------------------------------------------------------------------

    @api.model
    def _get_adoptable_animals(self, species=None):
        """ Return the animals that can be adopted: published on the website and not
        adopted yet, ordered by name. When ``species`` is given (e.g. 'cat'), only the
        animals of this species.
        """
        domain = [("is_published", "=", True), ("adopted", "=", False)]
        if species:
            domain.append(("species", "=", species))
        return self.search(domain, order="name")
