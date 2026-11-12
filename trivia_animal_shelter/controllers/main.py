from odoo import http
from odoo.http import request  # noqa: F401

from odoo import http
from odoo.exceptions import ValidationError
from werkzeug.exceptions import NotFound

from odoo.http import request

class ShelterController(http.Controller):
    """ The pages of the website of the shelter.

    Keep the controllers thin: the business logic belongs to the models (TODO 1 and TODO 4).
    """
    @http.route("/adopt", type="http", auth="public", website=True)
    def adopt(self, species=None, **kwargs):
        Animal = request.env["shelter.animal"]
        if species not in dict(Animal._get_species()):
            species = False
        return request.render("trivia_animal_shelter.animal_list", {
            "animals": Animal._get_adoptable_animals(species=species),
            "species": species,
        })

    @http.route('/adopt/<model("shelter.animal"):animal>', type="http", auth="public", website=True)
    def animal(self, animal, **kwargs):
        if animal not in request.env["shelter.animal"]._get_adoptable_animals():
            raise NotFound()
        return request.render("trivia_animal_shelter.animal_detail", {"animal": animal})

    @http.route('/adopt/<model("shelter.animal"):animal>/request', type="http", auth="public", website=True,
                methods=["POST"])
    def adoption_request(self, animal, **post):
        try:
            adoption_request = request.env["shelter.adoption.request"]._create_from_website(animal, post)
        except ValidationError:
            raise NotFound()
        return request.render("trivia_animal_shelter.adoption_thanks", {
            "animal": animal,
            "adoption_request": adoption_request,
        })

    # ----------------------------------------------------------------------------
    # TODO 2 - The page /adopt
    #
    # A public page of the website (anybody can see it, without logging in), which
    # renders the template trivia_animal_shelter.animal_list with the adoptable
    # animals (TODO 1). An optional parameter filters the species: /adopt?species=cat
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # TODO 3 - The page of an animal
    #
    # /adopt/<model("shelter.animal"):animal> renders the template
    # trivia_animal_shelter.animal_detail.
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # TODO 4 - The adoption request
    #
    # The form of the page of an animal is posted (POST only) to
    # /adopt/<model("shelter.animal"):animal>/request: create the request with
    # shelter.adoption.request._create_from_website(), then render the template
    # trivia_animal_shelter.adoption_thanks.
    # ----------------------------------------------------------------------------
