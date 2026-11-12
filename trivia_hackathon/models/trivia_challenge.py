import hashlib
import hmac
import logging
import uuid
from contextlib import closing
from typing import NamedTuple

from lxml import etree
from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import remove_accents
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import html_translate

from .trivia_master import TriviaMasterError

_logger = logging.getLogger(__name__)

WEDGE_COLORS = [
    ("blue", "Blue"),
    ("green", "Green"),
    ("yellow", "Yellow"),
    ("red", "Red"),
    ("orange", "Orange"),
    ("purple", "Purple"),
]
WEDGES = {
    "blue": "🔵",
    "green": "🟢",
    "yellow": "🟡",
    "red": "🔴",
    "orange": "🟠",
    "purple": "🟣",
}
EMPTY_WEDGE = "⚪"
# the messages posted in the Discuss channel are written in each language, after its flag
LANG_FLAGS = {"en_US": "🇬🇧", "fr_FR": "🇫🇷"}
DIFFICULTIES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

# The flag revealed by a checker only depends on the code of the challenge: on Odoo.sh, each push
# rebuilds the database, and the teams submit their flags again to get their wedges back.
FLAG_SECRET = b"trivia-hackathon-2026"


class CheckFailed(Exception):
    """ Raised by a checker step when a requirement of the challenge is not met. """


class CheckResult(NamedTuple):
    label: str
    passed: bool
    detail: str = ""
    bonus: bool = False


def require(condition, message):
    """ Make the current checker step fail with ``message`` unless ``condition`` holds. """
    if not condition:
        raise CheckFailed(message)


def normalize(text):
    """ Return ``text`` without accents nor case: "Mécénat" and "mecenat" are the same. """
    return remove_accents(text or "").strip().lower()


def name_matches(typed, expected):
    """ Whether a name typed by the players matches the ``expected`` one, leniently: without accents nor case,
    in the singular or the plural, with more words or longer words. Each word of ``expected`` must start a word
    of ``typed``: "Meuble" and "Meubles", "Électroménager" and "Électro", "Atelier de réparation" and
    "Atelier réparation" match.

    :param expected: a name, or a list of accepted names (e.g. the English and the French one)
    """
    if not isinstance(expected, str):
        return any(name_matches(typed, name) for name in expected)
    words = normalize(typed).split()
    return all(any(word.startswith(part.rstrip("s")) for word in words) for part in normalize(expected).split())


def get_arch(model, view_type, view_id=None):
    """ Return the arch (lxml) of a view of ``model``, with all its inherited views applied. """
    return etree.fromstring(model.get_view(view_id=view_id, view_type=view_type)["arch"])


def eval_expression(expression, values):
    """ Evaluate a view expression (invisible, readonly, decoration-*...) with the given values.

    :return: True or False, or None when it can't be evaluated (e.g. it uses other fields)
    """
    try:
        return bool(safe_eval(expression, values))
    except Exception:  # noqa: BLE001
        return None


class TriviaChallenge(models.Model):
    """ A challenge of the game board, brought by the module of a non-profit organisation.

    A challenge is validated by the method ``_check_<code>()`` that its module adds to this model.
    It returns a list of results, one per step, made by ``_run_step()``, and translates its messages
    with ``_ = self._get_report_env()._``.
    """
    _name = "trivia.challenge"
    _description = "Trivia Challenge"
    _order = "difficulty_rank, sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, readonly=True, help="Technical identifier, the checker method is _check_<code>.")
    organization = fields.Char(string="Organisation", help="The non-profit organisation that needs your help.")
    category = fields.Selection(
        [("functional", "Functional"), ("dev", "Dev")],
        required=True, default="dev",
        help="Functional: no code, everything is done in the interface of Odoo. Dev: you write code.",
    )
    topic = fields.Char(translate=True)
    summary = fields.Text(string="Instruction", translate=True, help="Short instruction displayed on the game board.")
    description = fields.Html(string="Statement", translate=html_translate)
    difficulty = fields.Selection(DIFFICULTIES, required=True, default="easy")
    # ordering by a selection field sorts its keys alphabetically: this rank sorts the board from easy to hard
    difficulty_rank = fields.Integer(compute="_compute_difficulty_rank", store=True)
    wedge_color = fields.Selection(WEDGE_COLORS, required=True, default="blue")
    wedge = fields.Char(compute="_compute_wedge")
    state = fields.Selection([("todo", "To do"), ("solved", "Solved")], required=True, default="todo", readonly=True)
    solved_date = fields.Datetime(readonly=True)
    solved_by_id = fields.Many2one("res.users", string="Solved By", readonly=True)
    attempt_count = fields.Integer(string="Attempts", readonly=True)
    flag = fields.Char(readonly=True, help="Keep it: submit it again to get the wedge back on a new database.")
    # written in each language by each check, see _write_checker_report()
    checker_report = fields.Html(readonly=True, translate=html_translate)
    # the results of the last check, 0 until the first check
    requirement_count = fields.Integer(string="Requirements Met", readonly=True)
    requirement_total = fields.Integer(string="Requirements", readonly=True)
    star_count = fields.Integer(string="Bonus Objectives Reached", readonly=True)
    star_total = fields.Integer(string="Bonus Objectives", readonly=True)
    progress = fields.Char(compute="_compute_progress")
    is_perfect = fields.Boolean(string="Perfect", compute="_compute_is_perfect")
    board = fields.Char(compute="_compute_board")
    # sending of the results to the master database of the organisers
    check_results = fields.Json(readonly=True, help="Results of the steps of the last check.")
    sync_uid = fields.Char(readonly=True, copy=False, help="Identifier of the last result, for the master database.")
    sync_state = fields.Selection(
        [("todo", "Not sent"), ("sent", "Sent"), ("error", "Not sent (error)")],
        string="Master Database", default="todo", required=True, readonly=True, copy=False,
    )
    sync_date = fields.Datetime(string="Sent on", readonly=True, copy=False)
    sync_message = fields.Char(string="Master Answer", readonly=True, copy=False)

    _code_uniq = models.Constraint("UNIQUE(code)", "The code of a challenge must be unique.")

    @api.depends("difficulty")
    def _compute_difficulty_rank(self):
        ranks = [key for key, _label in DIFFICULTIES]
        for challenge in self:
            challenge.difficulty_rank = ranks.index(challenge.difficulty)

    @api.depends("wedge_color", "state")
    def _compute_wedge(self):
        for challenge in self:
            challenge.wedge = WEDGES[challenge.wedge_color] if challenge.state == "solved" else EMPTY_WEDGE

    @api.depends("state", "requirement_count", "requirement_total", "star_count", "star_total")
    def _compute_progress(self):
        """ Requirements and bonus objectives met at the last check, e.g. "3/5 ⌛ 1/3 ⭐":
        ❌ when no requirement is met yet, ⌛ when some are, ✅ when all are. """
        for challenge in self:
            met, total = challenge.requirement_count, challenge.requirement_total
            stars, star_total = challenge.star_count, challenge.star_total
            if not total:
                # not checked yet on this database: count the steps of the checker
                total, star_total = challenge._get_step_totals()
                # a challenge solved with its flag met all its requirements
                met = total if challenge.state == "solved" else 0
            if not total:
                challenge.progress = False
                continue
            icon = "✅" if met == total else "⌛" if met else "❌\ufe0f"
            progress = f"{met}/{total} {icon}"
            if star_total:
                progress += f" {stars}/{star_total} ⭐"
            challenge.progress = progress

    @api.depends("state", "requirement_count", "requirement_total", "star_count", "star_total")
    def _compute_is_perfect(self):
        """ Solved with all the requirements AND all the bonus objectives at the last check. """
        for challenge in self:
            challenge.is_perfect = bool(
                challenge.state == "solved"
                and challenge.requirement_total
                and challenge.requirement_count == challenge.requirement_total
                and challenge.star_count == challenge.star_total
            )

    def _compute_board(self):
        board = self._get_board()
        for challenge in self:
            challenge.board = board

    @api.model
    def _get_board(self):
        return " ".join(self.sudo().search([]).mapped("wedge"))

    # ------------------------------------------------------------------
    # Game engine
    # ------------------------------------------------------------------

    def action_open_flag_wizard(self):
        self.ensure_one()
        # the menus of the card and of the form offer it on every challenge: say why before opening the wizard
        if self.state == "solved":
            raise UserError(self.env._("This challenge is already solved: its wedge is already on the board."))
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Submit a flag"),
            "res_model": "trivia.flag.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_challenge_id": self.id},
        }

    def action_run_checker(self):
        self.ensure_one()
        checker = getattr(self, f"_check_{self.code}", None)
        if not checker:
            raise UserError(self.env._("This challenge has no automatic checker."))
        results = checker()
        requirements = [result for result in results if not result.bonus]
        failed = [result for result in requirements if not result.passed]
        bonus = [result for result in results if result.bonus]
        challenge = self.sudo()
        vals = {
            "attempt_count": challenge.attempt_count + 1,
            "requirement_count": len(requirements) - len(failed),
            "requirement_total": len(requirements),
            "star_count": len([result for result in bonus if result.passed]),
            "star_total": len(bonus),
            "check_results": [result._asdict() for result in results],
            "sync_uid": str(uuid.uuid4()),
        }
        if not failed:
            vals["flag"] = challenge._get_checker_flag()
        challenge.write(vals)
        self._write_checker_report(results)
        if self.env.context.get("trivia_open_challenge"):
            # checked from the game board: show the report
            next_action = {
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "res_id": self.id,
                "views": [(False, "form")],
            }
        else:
            next_action = {"type": "ir.actions.client", "tag": "soft_reload"}
        if failed:
            challenge._send_to_master()
            message = self.env._("%(failed)s requirement(s) not met yet: see the tab Checker Report.", failed=len(failed))
            return self._notify_result(message, "warning", next_action)
        if challenge.state != "solved":
            challenge._mark_solved()
        challenge._send_to_master()
        message = self.env._("All requirements are met, you won the %(wedge)s wedge!", wedge=WEDGES[self.wedge_color])
        return self._notify_result(message, "success", next_action)

    def _write_checker_report(self, results):
        """ Write the report of a check in each language of the database, so that everybody reads it in their own
        language. ``results`` come from the checker run in the language of the user. In the other languages, the
        checker runs again (its steps are always rolled back, see _run_step()) and still reads the data in the
        language of the user: only its messages change language (see _get_report_env()), so that the report says
        the same thing in every language. """
        self.ensure_one()
        reports = {self.env.lang or "en_US": self._render_checker_report(results)}
        for lang, _name in self.env["res.lang"].get_installed():
            if lang not in reports:
                translated = getattr(self.with_context(trivia_report_lang=lang), f"_check_{self.code}")()
                reports[lang] = self.with_context(lang=lang)._render_checker_report(translated)

        def get_terms(report):
            terms = []
            html_translate(lambda term: terms.append(term) or term, report)
            return terms

        # the English report is the source, the others are its translations, item by item (same steps, same order)
        challenge = self.sudo().with_context(lang="en_US")
        challenge.checker_report = reports.pop("en_US")
        field = self._fields["checker_report"]
        sources = get_terms(challenge.checker_report)
        translations = {}
        for lang, report in reports.items():
            terms = get_terms(field.convert_to_cache(report, challenge))
            if len(terms) == len(sources):
                translations[lang] = dict(zip(sources, terms))
        if translations:
            challenge.update_field_translations("checker_report", translations)

    def _submit_flag(self, flag):
        """ Return whether ``flag`` is the flag of this challenge, mark it as solved if so. """
        self.ensure_one()
        challenge = self.sudo()
        challenge.attempt_count += 1
        flag = (flag or "").strip()
        if not hmac.compare_digest(flag.encode(), challenge._get_checker_flag().encode()):
            return False
        if challenge.state != "solved":
            challenge.flag = flag
            challenge.sync_uid = str(uuid.uuid4())
            challenge._mark_solved()
            challenge._send_to_master()
        return True

    def _get_step_totals(self):
        """ Return the number of requirements and of bonus objectives of the checker, without running it. """
        self.ensure_one()
        checker = getattr(self.with_context(trivia_list_steps=True), f"_check_{self.code}", None)
        steps = checker() if checker else []
        bonus = len([step for step in steps if step.bonus])
        return len(steps) - bonus, bonus

    def _get_checker_flag(self):
        self.ensure_one()
        digest = hmac.new(FLAG_SECRET, self.code.encode(), hashlib.sha256).hexdigest()[:12]
        return f"TRIVIA{{{self.code}_{digest}}}"

    def _mark_solved(self):
        for challenge in self:
            challenge.write({
                "state": "solved",
                "solved_date": fields.Datetime.now(),
                "solved_by_id": self.env.uid,
            })
            challenge._announce_wedge()

    def _announce_wedge(self):
        """ Post the won wedge and the current board in the Trivi'Hackathon channel, in each language of the
        database, like the welcome message: the players of both languages share the channel. """
        self.ensure_one()
        channel = self.env.ref("trivia_hackathon.channel_trivia", raise_if_not_found=False)
        if not channel:
            return
        langs = [lang for lang, _name in self.env["res.lang"].get_installed()]
        complete = all(state == "solved" for state in self.sudo().search([]).mapped("state"))

        def in_each_language(text, paragraph=Markup("<p>%s</p>")):
            """ One paragraph per language: its flag, then ``text(challenge)`` in this language. """
            return Markup().join(
                paragraph % " ".join(filter(None, [LANG_FLAGS.get(lang), text(self.with_context(lang=lang))]))
                for lang in langs
            )

        body = in_each_language(lambda challenge: challenge.env._(
            "%(user)s won the %(wedge)s wedge of “%(challenge)s” (%(organization)s)!",
            user=self.env.user.name, wedge=WEDGES[self.wedge_color],
            challenge=challenge.name, organization=self.organization,
        ))
        body += Markup('<p style="font-size: 2rem;">%s</p>') % self._get_board()
        if complete:
            body += in_each_language(
                lambda challenge: challenge.env._("🧀 The six wedges are on the board, congratulations!"),
                paragraph=Markup("<p><b>%s</b></p>"),
            )
        channel.sudo().message_post(
            body=body,
            author_id=self.env.ref("base.partner_root").id,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )

    # ------------------------------------------------------------------
    # Master database
    # ------------------------------------------------------------------

    def action_send_to_master(self):
        """ Send the last result again, e.g. after a network error or once the connection is set. """
        challenges = self.filtered("sync_uid")
        if not challenges:
            return self._notify(self.env._("Check the challenge first: there is no result to send yet."), "warning")
        if not self.env["trivia.master"]._is_configured():
            return self._ask_master_connection()
        challenges._send_to_master()
        errors = challenges.filtered(lambda challenge: challenge.sync_state == "error")
        if errors:
            return self._notify(errors[0].sync_message, "danger", {"type": "ir.actions.client", "tag": "soft_reload"})
        return self._notify(challenges[-1].sync_message, "success", {"type": "ir.actions.client", "tag": "soft_reload"})

    def _send_to_master(self):
        """ Send the last result of the challenges to the master database. Never raises: the players must be able to
        play even when the master database is down. The challenges not sent yet are sent again at the next try. """
        challenges = self.sudo()
        master = self.env["trivia.master"]
        if not master._is_configured():
            # e.g. no PIN in the session of the user yet: sent once they enter it (see trivia.master.wizard)
            challenges.filtered("sync_uid").write({
                "sync_state": "todo",
                "sync_message": self.env._(
                    "Waiting for the connection to the master database: enter your team and your PIN."
                ),
            })
            return
        # send again the results not sent before: the scheduled actions don't run on the Odoo.sh development builds
        challenges |= challenges.search([("sync_state", "!=", "sent"), ("sync_uid", "!=", False)])
        for challenge in challenges.filtered("sync_uid"):
            try:
                result = master._post("/hackathon/submit", challenge._get_master_payload())
            except TriviaMasterError as e:
                challenge.write({"sync_state": "error", "sync_message": str(e)})
            else:
                challenge.write({
                    "sync_state": "sent",
                    "sync_date": fields.Datetime.now(),
                    "sync_message": result.get("message"),
                })

    def _get_master_payload(self):
        self.ensure_one()
        step_count, step_total = self.requirement_count, self.requirement_total
        if not step_total:
            # solved with its flag, without any check on this database: all its requirements are met
            step_total = self._get_step_totals()[0]
            step_count = step_total if self.state == "solved" else 0
        return {
            "uid": self.sync_uid,
            "challenge": self.code,
            "solved": self.state == "solved",
            "step_count": step_count,
            "step_total": step_total,
            "star_count": self.star_count,
            "star_total": self.star_total,
            "attempt_count": self.attempt_count,
            "steps": [
                {key: step.get(key) for key in ("label", "passed", "bonus", "detail")}
                for step in self.check_results or []
            ],
            "checked_date": fields.Datetime.to_string(self.write_date),
            "db": self.env.cr.dbname,
        }

    def _notify_result(self, message, notification_type, next_action=None):
        """ Notify the result of a check or of a flag. On Odoo.sh, open the connection to the master database
        first when it is not complete. Elsewhere (e.g. a local database), the master database doesn't count the
        result: remind the players to validate the challenge on their Odoo.sh database too. """
        if self.env["trivia.master"]._get_odoo_sh_stage():
            return self._ask_master_connection(self._notify(message, notification_type, next_action))
        reminder = self.env._(
            "This database is not on Odoo.sh: the master database of the organisers doesn't count its results. "
            "Don't forget to check (or flag) this challenge on your Odoo.sh database to validate it!"
        )
        action = self._notify(f"{message} {reminder}", notification_type, next_action)
        # sticky, and not cut after 2 lines (o_line_clamp of the notifications): the players must read it
        action["params"].update(sticky=True, className="o_line_clamp_7")
        return action

    def _ask_master_connection(self, next_action=None):
        """ Return the wizard of the connection to the master database when it is not complete, e.g. when the user
        didn't enter the PIN of the team in their session yet, then ``next_action``. Return ``next_action`` otherwise. """
        if self.env["trivia.master"]._is_configured():
            return next_action
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Master Connection"),
            "res_model": "trivia.master.wizard",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
            "context": {"trivia_master_next_action": next_action, "trivia_master_from_check": True},
        }

    def _notify(self, message, notification_type, next_action=None):
        params = {"message": message, "type": notification_type, "sticky": False}
        if next_action:
            params["next"] = next_action
        return {"type": "ir.actions.client", "tag": "display_notification", "params": params}

    # ------------------------------------------------------------------
    # Tools for the checkers
    # ------------------------------------------------------------------

    def _get_report_env(self):
        """ The environment of the messages of a checker. They are written in the language of the report, which is
        not always the language of the user, in which the checker reads the data (see _write_checker_report()). """
        lang = self.env.context.get("trivia_report_lang")
        return self.with_context(lang=lang).env if lang else self.env

    def _run_step(self, label, step, bonus=False):
        """ Run a checker step in a savepoint which is always rolled back, so that the records
        created to check the challenge never stay in the database.

        :param str label: what the step checks, displayed in the report
        :param step: function without argument, raising ``CheckFailed`` (see ``require()``)
            when a requirement is not met
        :param bool bonus: whether the step is a bonus objective, which is not needed to win the wedge
        :rtype: CheckResult
        """
        if self.env.context.get("trivia_list_steps"):
            # only list the steps, without running them (see _get_step_totals())
            return CheckResult(label, False, bonus=bonus)
        try:
            # closing(): the savepoint is rolled back on exit, whether the step passes or fails
            with closing(self.env.cr.savepoint()):
                step()
        except CheckFailed as e:
            return CheckResult(label, False, str(e), bonus)
        except Exception as e:  # noqa: BLE001 - the code of the challengers may raise anything
            _logger.info("Trivi'Hackathon checker step %r crashed", label, exc_info=True)
            detail = self._get_report_env()._("Your code raised %(error)s", error=f"{type(e).__name__}: {e}")
            return CheckResult(label, False, detail, bonus)
        return CheckResult(label, True, bonus=bonus)

    @api.model
    def _render_checker_report(self, results):
        def icon(result):
            if result.bonus:
                return "⭐" if result.passed else "☆"
            return "✅" if result.passed else "❌\ufe0f"

        items = Markup().join(
            Markup('<li class="mb-2">%s <b>%s</b>%s</li>') % (
                icon(result),
                self.env._("Bonus: %(label)s", label=result.label) if result.bonus else result.label,
                Markup("<br/><i>%s</i>") % result.detail if result.detail else "",
            )
            for result in results
        )
        return Markup('<ul class="list-unstyled">%s</ul>') % items
