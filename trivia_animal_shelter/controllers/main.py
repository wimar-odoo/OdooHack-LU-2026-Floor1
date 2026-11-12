from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class ShelterController(http.Controller):
    """ The pages of the website of the shelter.

    Keep the controllers thin: the business logic belongs to the models (TODO 1 and TODO 4).
    """

    # TODO 2 - The page /adopt
    @http.route("/adopt", type="http", auth="public", website=True)
    def adopt(self, species=None, **kwargs):
        animals = request.env["shelter.animal"]._get_adoptable_animals(species or None)
        return request.render("trivia_animal_shelter.animal_list", {
            "animals": animals,
            "species": species or False,
        })

    # TODO 3 - The page of an animal
    @http.route('/adopt/<model("shelter.animal"):animal>', type="http", auth="public", website=True)
    def adopt_animal(self, animal, **kwargs):
        if not animal.exists() or not (
            animal.is_published or request.env.user.has_group("website.group_website_publisher")
        ):
            raise request.not_found()
        return request.render("trivia_animal_shelter.animal_detail", {"animal": animal})

    # TODO 4 - The adoption request
    @http.route('/adopt/<model("shelter.animal"):animal>/request',
                type="http", auth="public", website=True, methods=["POST"])
    def adopt_request(self, animal, **post):
        try:
            adoption_request = request.env["shelter.adoption.request"]._create_from_website(animal, post)
        except ValidationError:
            return request.redirect(animal.website_url)
        return request.render("trivia_animal_shelter.adoption_thanks", {
            "animal": animal,
            "adoption_request": adoption_request,
        })