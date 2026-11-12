{
    "name": "La Course du Cœur",
    "summary": "Trivi'Hackathon challenge: the results of a charity run, with SQL",
    "description": """
La Course du Cœur
=================
Challenge of the Trivi'Hackathon (SQL: SQL views, window functions, performance, SQL injection).

La Course du Cœur is a charity run of 10 km: sponsors give money for each kilometre covered by the runners.
Complete this module to publish the results, speed up the amounts raised, close a security hole and catch a cheater.
""",
    "version": "20.0.2.0.0",
    "category": "Hidden",
    "author": "Odoo PS",
    "license": "LGPL-3",
    "depends": ["trivia_hackathon"],
    "data": [
        "security/ir.access.csv",
        "data/trivia_challenge_data.xml",
        "views/run_edition_views.xml",
        "views/run_runner_views.xml",
        "report/run_result_report_views.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "application": True,
}
