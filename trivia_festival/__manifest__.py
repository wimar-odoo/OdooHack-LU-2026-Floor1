{
    "name": "Festival Solidaire",
    "summary": "Trivi'Hackathon challenge: the welcome desk of a solidarity festival, in JavaScript",
    "description": """
Festival Solidaire
==================
Challenge of the Trivi'Hackathon (JavaScript: OWL components, field widget, client action, services).

The Festival Solidaire opens its doors today. Complete this module to show how full the festival is, and to give
the volunteers of the welcome desk a simple screen to check the attendees in.
""",
    "version": "20.0.1.0.4",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon", "event"],
    "data": [
        "data/trivia_challenge_data.xml",
        "data/festival_data.xml",
        "views/event_event_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "trivia_festival/static/src/**/*",
        ],
    },
    "post_init_hook": "post_init_hook",
    "application": True,
}
