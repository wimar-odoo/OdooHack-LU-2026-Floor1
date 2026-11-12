from odoo import http
from odoo.http import request


class ShelterController(http.Controller):
    """ The pages of the website of the shelter.

    Keep the controllers thin: the business logic belongs to the models (TODO 1 and TODO 4).
    """

    @http.route(["/adopt"], type="http", auth="public", website=True, sitemap=True)
    def animal_list(self, species=None, **kwargs):
        Animal = request.env["shelter.animal"]
        species = species if species in dict(Animal._get_species()) else False
        return request.render("trivia_animal_shelter.animal_list", {
            "animals": Animal._get_adoptable_animals(species=species or None),
            "species": species,
            "species_list": Animal._get_species(),
        })

    @http.route(['/adopt/<model("shelter.animal"):animal>'], type="http", auth="public", website=True, sitemap=True)
    def animal_detail(self, animal, **kwargs):
        return request.render("trivia_animal_shelter.animal_detail", {"animal": animal})

    @http.route(
        ['/adopt/<model("shelter.animal"):animal>/request'],
        type="http", auth="public", website=True, methods=["POST"],
    )
    def adoption_request(self, animal, **post):
        adoption_request = request.env["shelter.adoption.request"]._create_from_website(animal, post)
        return request.render("trivia_animal_shelter.adoption_thanks", {
            "animal": animal,
            "adoption_request": adoption_request.sudo(),
        })
