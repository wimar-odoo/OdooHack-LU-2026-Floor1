{
    "name": "La Ressourcerie",
    "summary": "Trivi'Hackathon challenge: the articles, donations and till of a reuse centre",
    "description": """
La Ressourcerie
===============
Functional challenge of the Trivi'Hackathon (Inventory, traceability, pricelists, Point of Sale): no code,
everything is done in the interface of Odoo.

La Ressourcerie collects donated objects, repairs them and sells them at solidarity prices.
""",
    "version": "20.0.1.0.0",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon", "stock", "point_of_sale"],
    "data": [
        "data/trivia_challenge_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "application": False,
}
