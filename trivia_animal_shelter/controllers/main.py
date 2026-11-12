from odoo import http
from odoo.http import request  # noqa: F401


class ShelterController(http.Controller):
    """ The pages of the website of the shelter.

    Keep the controllers thin: the business logic belongs to the models (TODO 1 and TODO 4).
    """

    @http.route("/adopt", type="http", auth="public", website=True)
    def adopt(self, species=None, **kwargs):
        animals = request.env["shelter.animal"]._get_adoptable_animals(species or None)
        return request.render("trivia_animal_shelter.animal_list", {
            "animals": animals,
            "species": species or False,
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
