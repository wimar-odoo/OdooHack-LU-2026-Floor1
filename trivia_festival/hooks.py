import random

FIRST_NAMES = [
    "Marie", "Jean", "Ana", "Luca", "Sophie", "Tom", "Claire", "Paulo", "Léa", "Max",
    "Nadia", "Jeff", "Inês", "Pierre", "Sarah", "Yves", "Emma", "Carlos", "Julie", "Ben",
]
LAST_NAMES = [
    "Weber", "Schmit", "Ferreira", "Rossi", "Muller", "Hoffmann", "Wagner", "Santos", "Kremer", "Thill",
    "Haddad", "Reuter", "Costa", "Klein", "Becker", "Schroeder", "Lux", "Pereira", "Faber", "Meyer",
]


def post_init_hook(env):
    _generate_registrations(env)


def _generate_registrations(env):
    """ 120 registrations to the festival (reproducible), 10 of them already checked in. """
    rng = random.Random(2026)
    event = env.ref("trivia_festival.event_festival")
    tickets = [env.ref("trivia_festival.ticket_solidaire"), env.ref("trivia_festival.ticket_soutien")]
    names = rng.sample([f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES], 120)
    registrations = env["event.registration"].create([{
        "event_id": event.id,
        "event_ticket_id": rng.choices(tickets, weights=[3, 1])[0].id,
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@example.com",
    } for name in names])
    early_birds = registrations[:10]
    early_birds.action_set_done()
    early_birds.checkin_source = "backend"
