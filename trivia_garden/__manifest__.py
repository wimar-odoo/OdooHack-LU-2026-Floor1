{
    "name": "Gaart fir Jiddereen",
    "summary": "Trivi'Hackathon challenge: the membership fees and the plots of the shared gardens",
    "description": """
Gaart fir Jiddereen
===================
Challenge of the Trivi'Hackathon (Python: models, inheritance, computed fields, constraints, views, access rights).

Gaart fir Jiddereen runs shared gardens in Luxembourg City and in Esch-sur-Alzette. Complete this module so that
the treasurer can follow the membership fees, and so that only the members up to date can rent a plot.
""",
    "version": "20.0.1.0.0",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon", "contacts"],
    "data": [
        "security/ir.access.csv",
        "data/trivia_challenge_data.xml",
        "data/garden_data.xml",
        "views/garden_site_views.xml",
        "views/garden_plot_views.xml",
        "views/garden_membership_fee_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
        # needs the fee model and the member fields: loaded after everything else
        "data/garden_membership_fee_data.xml",
    ],
    "application": True,
}
