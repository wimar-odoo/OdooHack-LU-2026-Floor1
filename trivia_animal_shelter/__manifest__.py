{
    "name": "Refuge Les 4 Pattes",
    "summary": "Trivi'Hackathon challenge: the adoption website of an animal shelter",
    "description": """
Refuge Les 4 Pattes
===================
Challenge of the Trivi'Hackathon (website: controllers, QWeb templates, Bootstrap, SCSS, forms, PDF report).

The animal shelter Les 4 Pattes wants its animals to find a family thanks to its website. Complete this module so
that visitors can see the animals waiting for a family and send an adoption request.
""",
    "version": "20.0.1.0.1",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon", "website"],
    "data": [
        "security/ir.access.csv",
        "data/trivia_challenge_data.xml",
        "data/shelter_data.xml",
        "views/shelter_animal_views.xml",
        "views/shelter_adoption_request_views.xml",
        "views/menus.xml",
        "views/website_templates.xml",
        "report/adoption_certificate_report.xml",
    ],
    # TODO 5: add static/src/scss/shelter.scss to the assets of the website (bundle web.assets_frontend)
    "application": True,
}
