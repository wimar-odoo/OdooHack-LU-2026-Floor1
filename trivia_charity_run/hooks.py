import random
from datetime import date, datetime, timedelta

RUNNERS_PER_EDITION = 600
CATEGORY_WEIGHTS = {"junior": 10, "senior": 45, "master": 35, "veteran": 10}
FIRST_NAMES = [
    "Marie", "Jean", "Ana", "Luca", "Sophie", "Tom", "Claire", "Paulo", "Léa", "Max",
    "Nadia", "Jeff", "Inês", "Pierre", "Sarah", "Yves", "Emma", "Carlos", "Julie", "Ben",
    "Lisa", "Marc", "Sofia", "Kevin", "Laura", "Paul", "Chloé", "Tiago", "Anne", "Luc",
    "Elena", "Patrick", "Mia", "Hugo", "Nora", "Sven", "Rita", "Gilles", "Joana", "Mike",
]
LAST_NAMES = [
    "Weber", "Schmit", "Ferreira", "Rossi", "Muller", "Hoffmann", "Wagner", "Santos", "Kremer", "Thill",
    "Haddad", "Reuter", "Costa", "Klein", "Becker", "Schroeder", "Lux", "Pereira", "Faber", "Meyer",
    "Kieffer", "Hansen", "Martins", "Bauer", "Wolff", "Steffen", "Goncalves", "Schneider", "Majerus", "Reding",
    "Lentz", "Bernard", "Silva", "Fischer", "Frank", "Wirtz", "Kohl", "Dupont", "Morel", "Neumann",
]
SPONSORS = [
    "Boulangerie Kremer", "Garage Weber", "Pharmacie du Centre", "Café Am Eck", "Velosbuttek",
    "Cabinet Schmit & Associés", "Épicerie Bio Esch", "Fitness Kirchberg", "Imprimerie Reuter",
    "Restaurant Bella Vista", "Fleuriste Rosa", "Auto-école Thill",
]


def post_init_hook(env):
    _generate_races(env)


def _generate_races(env):
    """ The last three editions of the race, with reproducible data.

    The last edition hides a cheater: an impossible time between km 5 and km 10 (TODO 4).
    The edition before also had one, already disqualified.
    """
    rng = random.Random(2026)
    last_year = date.today().year - 1
    editions = env["run.edition"].create([
        {"name": f"Course du Cœur {year}", "year": year, "date": date(year, 5, 17)}
        for year in range(last_year - 2, last_year + 1)
    ])
    full_names = [f"{first} {last}" for first in FIRST_NAMES for last in LAST_NAMES]
    for edition in editions:
        start = datetime(edition.year, 5, 17, 8, 0)  # 10:00 in Luxembourg, in UTC
        plans = []
        for bib, name in enumerate(rng.sample(full_names, RUNNERS_PER_EDITION), start=1):
            pace = min(max(rng.gauss(5.8, 0.9), 3.5), 9.0)  # minutes per km
            plans.append({
                "vals": {
                    "name": name,
                    "bib": bib,
                    "edition_id": edition.id,
                    "category": rng.choices(list(CATEGORY_WEIGHTS), weights=list(CATEGORY_WEIGHTS.values()))[0],
                    "gender": rng.choice(["female", "male"]),
                },
                "start": start + timedelta(seconds=rng.randint(0, 180)),
                "legs": [5 * pace * rng.uniform(0.95, 1.05), 5 * pace * rng.uniform(0.95, 1.12)],  # minutes
                "finished": rng.random() > 0.03,
            })
        finishers = [plan for plan in plans if plan["finished"]]
        if edition.year == last_year:
            plans[41]["vals"]["name"] = "Seán O'Brien"  # TODO 3: the results kiosk cannot find him
            rng.choice(finishers)["legs"][1] = 10.5
        elif edition.year == last_year - 1:
            cheater = rng.choice(finishers)
            cheater["legs"][1] = 9.2
            cheater["vals"]["disqualified"] = True
        for plan in plans:
            plan["vals"]["distance_km"] = 10 if plan["finished"] else 5

        runners = env["run.runner"].create([plan["vals"] for plan in plans])
        split_vals, pledge_vals = [], []
        for runner, plan in zip(runners, plans):
            times = [plan["start"], plan["start"] + timedelta(minutes=plan["legs"][0])]
            if plan["finished"]:
                times.append(times[1] + timedelta(minutes=plan["legs"][1]))
            split_vals += [
                {"runner_id": runner.id, "checkpoint_km": km, "time": moment.replace(microsecond=0)}
                for km, moment in zip((0, 5, 10), times)
            ]
            if rng.random() < 0.35:
                pledge_vals += [{
                    "runner_id": runner.id,
                    "sponsor": rng.choice(SPONSORS),
                    "amount_per_km": rng.choice([0.5, 1.0, 2.0, 2.5, 5.0]),
                } for _i in range(rng.randint(1, 3))]
        env["run.split"].create(split_vals)
        env["run.pledge"].create(pledge_vals)
