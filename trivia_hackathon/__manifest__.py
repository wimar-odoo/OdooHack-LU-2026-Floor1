{
    "name": "Trivi'Hackathon",
    "summary": "Hackathon game: help the non-profit organisations and collect the 6 wedges",
    "description": """
Trivi'Hackathon
===============
Game engine of the Trivi'Hackathon 2026, a Trivial Pursuit of the non-profit organisations:

* the game board: one card per challenge, with a short instruction and the full statement;
* the *Check* button, which runs the automatic checker of a challenge and reports what is still missing;
* the flags, to get the wedges of the solved challenges back on a new database;
* the wedges announced in the Trivi'Hackathon Discuss channel.

Each challenge is brought by its own module (trivia_*), which only depends on this one.
""",
    "version": "20.0.1.1.0",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    # website: in Odoo 20, website makes ir.ui.view.visibility required (NOT NULL, without database default).
    # A module loaded before website cannot create a view during an update (-u) once website is installed:
    # depending on it here loads all the challenges after website.
    "depends": ["mail", "website"],
    "data": [
        "security/ir.access.csv",
        "data/discuss_channel_data.xml",
        "views/trivia_challenge_views.xml",
        "wizard/trivia_flag_wizard_views.xml",
        "wizard/trivia_master_wizard_views.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "application": True,
}
