from collections import defaultdict
from datetime import datetime, timedelta

from odoo import models
from odoo.tools import SQL

from odoo.addons.trivia_hackathon.models.trivia_challenge import CheckFailed, require

RECORD_5K_MINUTES = 12 + 35 / 60  # world record of the 5 km
MAX_QUERIES = 10  # to compute the amount raised of 50 runners
INJECTIONS = ["' OR 1=1 --", "x' OR 'x'='x"]


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "The Charity Run": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_charity_run(self):
        _ = self._get_report_env()._
        env = self.env
        Edition, Runner, Split, Pledge, Result = (
            env[model] for model in ("run.edition", "run.runner", "run.split", "run.pledge", "run.result.report")
        )

        def create_race(runners, disqualified=()):
            """ Create a test edition. ``runners``: list of (name, category, start offset in seconds,
            minutes at km 5, minutes at km 10 or None when the runner gave up). """
            edition = Edition.create({"name": "Checker edition", "year": 1900})
            records = Runner.create([{
                "name": name, "bib": bib, "edition_id": edition.id, "category": category, "gender": "female",
                "distance_km": 10 if finish else 5, "disqualified": name in disqualified,
            } for bib, (name, category, _offset, _km5, finish) in enumerate(runners, start=1)])
            race_start = datetime(1900, 5, 17, 8, 0)
            split_vals = []
            for runner, (_name, _category, offset, km5, finish) in zip(records, runners):
                start = race_start + timedelta(seconds=offset)
                split_vals += [
                    {"runner_id": runner.id, "checkpoint_km": km, "time": start + timedelta(minutes=minutes)}
                    for km, minutes in ((0, 0), (5, km5), (10, finish)) if minutes is not None
                ]
            Split.create(split_vals)
            env.flush_all()
            env.invalidate_all()
            return edition

        def get_results(edition):
            return {row.runner_id.name: row for row in Result.search([("edition_id", "=", edition.id)])}

        # name, category, start offset (s), minutes at km 5, minutes at km 10
        race = [
            ("Checker Ada", "senior", 60, 20, 41),
            ("Checker Bea", "master", 0, 22, 43.5),
            ("Checker Cleo", "senior", 150, 21, 43.5),
            ("Checker Dora", "senior", 30, 25, 50.25),
            ("Checker Eva", "master", 0, 30, None),
            ("Checker Fay", "junior", 90, 28, 55),
        ]
        # name: (rank, rank in category)
        expected_ranks = {
            "Checker Ada": (1, 1), "Checker Bea": (2, 1), "Checker Cleo": (2, 2),
            "Checker Dora": (4, 3), "Checker Fay": (5, 1),
        }

        def check_times():
            results = get_results(create_race(race))
            require(results, _("The results are still empty: write the SQL view of the results (mission 1)."))
            require("Checker Eva" not in results, _("A runner who gave up (no split at km 10) must not be in the results."))
            require(set(results) == set(expected_ranks), _("The results must contain one row per runner who reached the finish."))
            for name, _category, _offset, _km5, finish in race:
                if finish is None:
                    continue
                row = results[name]
                require(abs(row.finish_time - finish) < 0.01, _(
                    "The time of a runner must be the minutes between their own start and their finish: "
                    "%(expected)s instead of %(value)s.", expected=finish, value=row.finish_time,
                ))
                require(abs(row.pace - finish / 10) < 0.01, _(
                    "The pace must be the minutes per km: %(expected)s instead of %(value)s.",
                    expected=round(finish / 10, 3), value=row.pace,
                ))

        def check_ranks():
            results = get_results(create_race(race))
            require(set(results) == set(expected_ranks), _("The results must contain one row per runner who reached the finish."))
            for name, (rank, category_rank) in expected_ranks.items():
                row = results[name]
                require(row.rank == rank, _(
                    "%(name)s must be ranked %(expected)s in the edition, not %(value)s "
                    "(runners with the same time share the same rank: 1, 2, 2, 4).",
                    name=name, expected=rank, value=row.rank,
                ))
                require(row.category_rank == category_rank, _(
                    "%(name)s must be ranked %(expected)s in their category, not %(value)s.",
                    name=name, expected=category_rank, value=row.category_rank,
                ))

        def check_amount_raised():
            edition = Edition.create({"name": "Checker edition", "year": 1900})
            runners = Runner.create([{
                "name": f"Checker runner {bib}", "bib": bib, "edition_id": edition.id, "category": "senior",
                "gender": "male", "distance_km": 5 if bib % 4 == 0 else 10,
            } for bib in range(1, 51)])
            Pledge.create([
                {"runner_id": runner.id, "sponsor": "Checker sponsor", "amount_per_km": runner.bib % 3 + 0.5}
                for runner in runners for _i in range(runner.bib % 3)
            ])
            env.flush_all()
            env.invalidate_all()
            runners = Runner.browse(runners.ids)
            count = env.cr.sql_log_count
            amounts = runners.mapped("amount_raised")
            queries = env.cr.sql_log_count - count
            for runner, amount in zip(runners, amounts):
                expected = (runner.bib % 3) * (runner.bib % 3 + 0.5) * runner.distance_km
                require(abs(amount - expected) < 0.001, _(
                    "The amount raised by %(name)s is %(value)s instead of %(expected)s.",
                    name=runner.name, value=amount, expected=expected,
                ))
            require(queries <= MAX_QUERIES, _(
                "Computing the amount raised of 50 runners runs %(count)s queries: compute all the runners at once "
                "(e.g. with _read_group).", count=queries,
            ))
            # a write is only sent to the database at the next flush (unlike a create)
            runner = runners[0]
            runner.pledge_ids.amount_per_km = 10
            expected = 10 * len(runner.pledge_ids) * runner.distance_km
            require(abs(runner.amount_raised - expected) < 0.001, _(
                "The amount raised ignores a pledge modified just before: raw SQL reads the database, "
                "flush the pledges first (flush_model).",
            ))

        def check_index():
            env.cr.execute(SQL("SELECT indexdef FROM pg_indexes WHERE tablename = %s", Split._table))
            require(any("(runner_id" in indexdef for (indexdef,) in env.cr.fetchall()),
                    _("The table of the split times has no index on runner_id (mission 2)."))

        def check_search():
            edition = Edition.create({"name": "Checker edition", "year": 1900})
            obrien, other = Runner.create([
                {"name": "Checker Seán O'Brien", "bib": 4242, "edition_id": edition.id, "category": "senior", "gender": "male"},
                {"name": "Checker Other", "bib": 4343, "edition_id": edition.id, "category": "senior", "gender": "male"},
            ])
            for term, situation in [("4242", _("by bib")), ("o'brien", _("by name, with an apostrophe"))]:
                try:
                    with env.cr.savepoint():
                        found = Runner.search_by_bib_or_name(term)
                except Exception as e:  # noqa: BLE001
                    raise CheckFailed(_(
                        "search_by_bib_or_name(%(term)s) crashed: %(error)s", term=repr(term), error=f"{type(e).__name__}: {e}",
                    ))
                require(obrien in found and other not in found, _(
                    "search_by_bib_or_name() does not find the right runner %(situation)s.", situation=situation,
                ))

        def check_injection():
            for payload in INJECTIONS:
                try:
                    with env.cr.savepoint():
                        found = Runner.search_by_bib_or_name(payload)
                except Exception as e:  # noqa: BLE001
                    raise CheckFailed(_(
                        "search_by_bib_or_name(%(term)s) crashed: %(error)s", term=repr(payload), error=f"{type(e).__name__}: {e}",
                    ))
                require(not found, _(
                    "search_by_bib_or_name(%(term)s) returns %(count)s runners: the query is open to SQL injection.",
                    term=repr(payload), count=len(found),
                ))

        def check_cheater():
            last_edition = Edition.search([], order="year desc", limit=1)
            times = defaultdict(dict)
            for split in Split.search([("runner_id.edition_id", "=", last_edition.id)]):
                times[split.runner_id][split.checkpoint_km] = split.time
            cheaters = Runner.browse()
            for runner, checkpoints in times.items():
                kms = sorted(checkpoints)
                for km_from, km_to in zip(kms, kms[1:]):
                    minutes = (checkpoints[km_to] - checkpoints[km_from]).total_seconds() / 60
                    if minutes < RECORD_5K_MINUTES * (km_to - km_from) / 5:
                        cheaters |= runner
            disqualified = Runner.search([("edition_id", "=", last_edition.id), ("disqualified", "=", True)])
            require(disqualified, _("Nobody is disqualified in the last edition yet (mission 4)."))
            require(disqualified == cheaters, _(
                "The wrong runners are disqualified in the last edition: only the runner with an impossible time "
                "between km 5 and km 10 must be.",
            ))

        def check_without_disqualified():
            results = get_results(create_race(race + [("Checker Gina", "senior", 0, 19, 39)], disqualified=["Checker Gina"]))
            require("Checker Gina" not in results, _("A disqualified runner is still in the results."))
            require(results.get("Checker Ada") and results["Checker Ada"].rank == 1, _(
                "The ranks must be computed without the disqualified runners.",
            ))

        def check_report_views():
            for view_type in ("pivot", "graph"):
                require(env["ir.ui.view"].search_count([("model", "=", Result._name), ("type", "=", view_type)]),
                        _("The results have no %(view_type)s view.", view_type=view_type))
                require(env["ir.actions.act_window"].search_count([
                    ("res_model", "=", Result._name), ("view_mode", "ilike", view_type),
                ]), _("The action of the results does not open the %(view_type)s view.", view_type=view_type))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. Results: finishers, times and paces"), check_times, False),
            (_("1. Results: ranks in the edition and in the category"), check_ranks, False),
            (_("2. Amount raised in a few queries"), check_amount_raised, False),
            (_("2. Index on the split times"), check_index, False),
            (_("3. Search by bib or name"), check_search, False),
            (_("3. No SQL injection"), check_injection, False),
            (_("4. The cheater is disqualified"), check_cheater, False),
            (_("Results without the disqualified runners"), check_without_disqualified, True),
            (_("Pivot and graph views of the results"), check_report_views, True),
        ]]
