from odoo import api, fields, models

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
        grouped_pledges = self.env["run.pledge"]._read_group(
            [("runner_id", "in", self.ids)],
            ["runner_id"],
            ["amount_per_km:sum"],
        )
        rates_by_runner = {
            runner.id: rate or 0.0 for runner, rate in grouped_pledges
        }
        for runner in self:
            if runner.id:
                rate = rates_by_runner.get(runner.id, 0.0)
            else:
                rate = sum(runner.pledge_ids.mapped("amount_per_km"))
            runner.amount_raised = rate * runner.distance_km

    def action_disqualify(self):
        self.disqualified = True

    def action_requalify(self):
        self.disqualified = False

    # ----------------------------------------------------------------------------
    # TODO 3 - The results kiosk
    # ----------------------------------------------------------------------------

    @api.model
    def search_by_bib_or_name(self, term):
        """ Return the runners whose bib number is ``term``, or whose name contains ``term``.

        It is used by the results kiosk of the race village, where anybody can type
        anything... This query is vulnerable to SQL injection: try ' OR 1=1 --
        """
        self.flush_model(["bib", "name"])  # raw SQL reads the database, not the cache of the ORM
        self.env.cr.execute(f"""
            SELECT id
              FROM run_runner
             WHERE bib::text = '{term}'
                OR name ILIKE '%{term}%'
          ORDER BY edition_id DESC, bib
        """)
        return self.browse([row[0] for row in self.env.cr.fetchall()])
