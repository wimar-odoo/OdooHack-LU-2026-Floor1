from odoo import http
from odoo.http import request


class ShelterController(http.Controller):
    """ The pages of the website of the shelter.

    Keep the controllers thin: the business logic belongs to the models (TODO 1 and TODO 4).
    """

    # ----------------------------------------------------------------------------
    # TODO 2 - The page /adopt
    #
    # A public page of the website (anybody can see it, without logging in), which
    # renders the template trivia_animal_shelter.animal_list with the adoptable
    # animals (TODO 1). An optional parameter filters the species: /adopt?species=cat
    # ----------------------------------------------------------------------------
    @http.route('/adopt', type='http', auth='public', website=True)
    def adopt(self, species=None, **kwargs):
        animals = request.env['shelter.animal']._get_adoptable_animals(species)
        return request.render('trivia_animal_shelter.animal_list', {
            'animals': animals,
            'species': species or False,
        })

    # ----------------------------------------------------------------------------
    # TODO 3 - The page of an animal
    #
    # /adopt/<model("shelter.animal"):animal> renders the template
    # trivia_animal_shelter.animal_detail.
    # ----------------------------------------------------------------------------
    @http.route('/adopt/<model("shelter.animal"):animal>', type='http', auth='public', website=True)
    def adopt_animal(self, animal, **kwargs):
        return request.render('trivia_animal_shelter.animal_detail', {'animal': animal})

    # ----------------------------------------------------------------------------
    # TODO 4 - The adoption request
    #
    # The form of the page of an animal is posted (POST only) to
    # /adopt/<model("shelter.animal"):animal>/request: create the request with
    # shelter.adoption.request._create_from_website(), then render the template
    # trivia_animal_shelter.adoption_thanks.
    # ----------------------------------------------------------------------------
    @http.route('/adopt/<model("shelter.animal"):animal>/request', type='http', auth='public',
                website=True, methods=['POST'])
    def adopt_request(self, animal, **post):
        adoption_request = request.env['shelter.adoption.request']._create_from_website(animal, post)
        return request.render('trivia_animal_shelter.adoption_thanks', {
            'animal': animal,
            'adoption_request': adoption_request,
        })
