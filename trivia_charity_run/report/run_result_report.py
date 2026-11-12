from odoo import fields, models, tools
from odoo.tools import SQL

from ..models.run_runner import CATEGORIES, GENDERS


class RunResultReport(models.Model):
    """ The results of the races: one row per runner who reached the finish. """
    _name = "run.result.report"
    _description = "Race Results"
    _auto = False  # no table: the model reads the SQL view created by init()
    _order = "edition_id desc, rank, bib"

    runner_id = fields.Many2one("run.runner", string="Runner", readonly=True)
    edition_id = fields.Many2one("run.edition", string="Edition", readonly=True)
    bib = fields.Integer(readonly=True)
    category = fields.Selection(CATEGORIES, readonly=True)
    gender = fields.Selection(GENDERS, readonly=True)
    finish_time = fields.Float(string="Time (min)", readonly=True, aggregator="avg")
    pace = fields.Float(string="Pace (min/km)", readonly=True, aggregator="avg")
    rank = fields.Integer(readonly=True, aggregator="min")
    category_rank = fields.Integer(string="Rank in Category", readonly=True, aggregator="min")

    def init(self):
        """ Create the SQL view of the results (called when the module is installed or updated).

        One row per runner who reached the finish (a split at km 10) and who is not
        disqualified. The ranks are computed in the outer query, so they only take the
        remaining runners into account.
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(SQL(
            """
            CREATE OR REPLACE VIEW %s AS (
                SELECT t.id,
                       t.runner_id,
                       t.edition_id,
                       t.bib,
                       t.category,
                       t.gender,
                       t.finish_time,
                       t.finish_time / 10.0 AS pace,
                       RANK() OVER (PARTITION BY t.edition_id
                                    ORDER BY t.finish_time) AS rank,
                       RANK() OVER (PARTITION BY t.edition_id, t.category
                                    ORDER BY t.finish_time) AS category_rank
                  FROM (
                        SELECT r.id AS id,
                               r.id AS runner_id,
                               r.edition_id,
                               r.bib,
                               r.category,
                               r.gender,
                               EXTRACT(EPOCH FROM (fin.time - st.time)) / 60.0 AS finish_time
                          FROM run_runner r
                          JOIN run_split st  ON st.runner_id = r.id AND st.checkpoint_km = 0
                          JOIN run_split fin ON fin.runner_id = r.id AND fin.checkpoint_km = 10
                         WHERE NOT r.disqualified
                       ) t
            )
            """,
            SQL.identifier(self._table),
        ))