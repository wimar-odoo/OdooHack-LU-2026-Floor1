import re

from odoo import models
from odoo.tools import file_open

from odoo.addons.trivia_hackathon.models.trivia_challenge import get_arch, require

MODULE = "trivia_festival"
CHECKINS = 3
TEMPLATE_RE = re.compile(r'''static\s+template\s*=\s*["']([\w.]+)["']''')
TEMPLATE_NAME_RE = re.compile(r'''t-name\s*=\s*["']([\w.]+)["']''')


def _without_comments(content, language):
    if language == "xml":
        return re.sub(r"<!--.*?-->", "", content, flags=re.S)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    return re.sub(r"^\s*//.*$", "", content, flags=re.M)


def _registers(content, category, key=None):
    """ Whether the JavaScript ``content`` adds something (``key``, if given) to the registry ``category``. """
    if not re.search(rf'''category\(\s*["']{category}["']\s*\)''', content):
        return False
    return key is None or bool(re.search(rf'''["']{re.escape(key)}["']''', content))


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "The Welcome Desk": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_festival(self):
        _ = self._get_report_env()._
        env = self.env
        festival = env.ref(f"{MODULE}.event_festival")

        def module_files(extension):
            """ The files of the module in the assets of the backend: {path: content without comments} """
            Asset = env["ir.asset"]
            files = {}
            for path, full_path, *_rest in Asset._get_asset_paths("web.assets_backend", Asset._get_asset_params()):
                if f"{MODULE}/static/" in path and path.endswith(f".{extension}"):
                    with file_open(full_path) as file:
                        files[path] = _without_comments(file.read(), extension)
            return files

        def require_registered(category, key, message):
            scripts = [content for content in module_files("js").values() if _registers(content, category, key)]
            require(scripts, message)
            templates = {name for content in module_files("xml").values() for name in TEMPLATE_NAME_RE.findall(content)}
            for name in TEMPLATE_RE.findall(scripts[0]):
                require(name in templates, _(
                    "The template %(template)s of the component does not exist in the XML files of the module.",
                    template=name,
                ))

        def check_gauge():
            require_registered("fields", "festival_fill_gauge", _(
                "No JavaScript file of the module adds festival_fill_gauge to the registry of the fields (mission 1).",
            ))

        def check_gauge_form():
            form = get_arch(env["event.event"], "form", env.ref("event.view_event_form").id)
            require(form.xpath("//field[@name='seats_taken'][@widget='festival_fill_gauge']"),
                    _("The form of the events does not display seats_taken with the widget festival_fill_gauge."))

        def check_kiosk():
            require_registered("actions", "festival_kiosk", _(
                "No JavaScript file of the module adds festival_kiosk to the registry of the actions (mission 2).",
            ))
            actions = env["ir.actions.client"].search([("tag", "=", "festival_kiosk")])
            require(actions, _("There is no client action with the tag festival_kiosk (mission 2)."))
            require(env["ir.ui.menu"].sudo().search_count([("action", "in", [f"{a._name},{a.id}" for a in actions])]),
                    _("No menu opens the welcome desk (mission 2)."))

        def check_checkins():
            count = env["event.registration"].search_count([("event_id", "=", festival.id), ("checkin_source", "=", "kiosk")])
            require(count >= CHECKINS, _(
                "%(count)s attendee(s) checked in from the welcome desk: check %(expected)s attendees in from your screen.",
                count=count, expected=CHECKINS,
            ))

        def check_systray():
            require_registered("systray", None, _("No JavaScript file of the module adds a component to the systray."))

        def check_search():
            require(any("t-model" in content for content in module_files("xml").values()),
                    _("The welcome desk has no search box (an input with t-model)."))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. Widget festival_fill_gauge"), check_gauge, False),
            (_("1. Fill gauge on the form of the event"), check_gauge_form, False),
            (_("2. Client action of the welcome desk"), check_kiosk, False),
            (_("3. Attendees checked in from the welcome desk"), check_checkins, False),
            (_("Counter of the attendees in the systray"), check_systray, True),
            (_("Search box in the welcome desk"), check_search, True),
        ]]
