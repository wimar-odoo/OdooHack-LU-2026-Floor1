from odoo import api, fields, models
from odoo.tools import SQL  # add to the imports at the top of the file

CATEGORIES = [
    ("junior", "Junior (under 20)"),
    ("senior", "Senior (20-39)"),
    ("master", "Master (40-59)"),
    ("veteran", "Veteran (60 and over)"),
]
GENDERS = [("female", "Women"), ("male", "Men")]


class RunRunner(models.Model):
    _name = "run.runner"
    _description = "Runner"
    _order = "edition_id desc, bib"

    name = fields.Char(required=True)
    bib = fields.Integer(required=True)
    edition_id = fields.Many2one("run.edition", string="Edition", required=True, ondelete="cascade", index=True)
    category = fields.Selection(CATEGORIES, required=True)
    gender = fields.Selection(GENDERS, required=True)
    distance_km = fields.Float(string="Distance (km)", help="Distance covered by the runner.")
    disqualified = fields.Boolean()
    split_ids = fields.One2many("run.split", "runner_id", string="Split Times")
    pledge_ids = fields.One2many("run.pledge", "runner_id", string="Pledges")
    amount_raised = fields.Float(
        compute="_compute_amount_raised",
        help="Amount given by the sponsors: their pledges per km × the distance covered by the runner.",
    )

    _bib_uniq = models.Constraint("UNIQUE(edition_id, bib)", "Two runners of an edition cannot have the same bib.")

    # ----------------------------------------------------------------------------
    # TODO 2 - The amount raised
    #
    # This computation runs one query per runner (the famous "N+1 queries"): the
    # list of the runners is slow. Compute it for all the runners at once.
    # ----------------------------------------------------------------------------

    @api.depends("pledge_ids.amount_per_km", "distance_km")
    def _compute_amount_raised(self):
        Pledge = self.env["run.pledge"]
        Pledge.flush_model(["runner_id", "amount_per_km"])  # send pending changes to the database
        groups = Pledge._read_group(
            [("runner_id", "in", self.ids)],
            groupby=["runner_id"],
            aggregates=["amount_per_km:sum"],
        )
        totals = {runner.id: total for runner, total in groups}
        for runner in self:
            runner.amount_raised = totals.get(runner.id, 0.0) * runner.distance_km

    def action_disqualify(self):
        self.disqualified = True

    def action_requalify(self):
        self.disqualified = False

    # ----------------------------------------------------------------------------
    # TODO 3 - The results kiosk
    # ----------------------------------------------------------------------------

    @api.model
    def search_by_bib_or_name(self, term):
        """ Return the runners whose bib number is ``term``, or whose name contains ``term``. """
        self.flush_model(["bib", "name"])  # raw SQL reads the database, not the cache of the ORM
        term = str(term or "").strip()
        # escape the LIKE wildcards, so that "50%" or "_" are searched literally
        escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        self.env.cr.execute(SQL(
            """
            SELECT id
              FROM run_runner
             WHERE bib::text = %s
                OR name ILIKE %s
          ORDER BY edition_id DESC, bib
            """,
            term,
            f"%{escaped}%",
        ))
        return self.browse([row[0] for row in self.env.cr.fetchall()])
