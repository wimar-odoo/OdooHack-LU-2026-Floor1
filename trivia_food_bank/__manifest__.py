{
    "name": "Les Restos du Quartier",
    "summary": "Trivi'Hackathon challenge: the donors, patrons and donations of a food aid association",
    "description": """
Les Restos du Quartier
======================
Functional challenge of the Trivi'Hackathon (Contacts, Invoicing, CRM, Email Marketing): no code, everything is
done in the interface of Odoo.

Les Restos du Quartier is a food aid association which wants to manage its donors, patrons and donations in Odoo.
""",
    "version": "20.0.1.1.0",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon", "contacts", "crm", "account", "mass_mailing"],
    "data": [
        "data/trivia_challenge_data.xml",
    ],
    "application": False,
}
