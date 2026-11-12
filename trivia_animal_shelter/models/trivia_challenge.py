import re

import psycopg2
from lxml import html
from werkzeug.exceptions import HTTPException

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import file_open

from odoo.addons.trivia_hackathon.models.trivia_challenge import CheckFailed, require

MODULE = "trivia_animal_shelter"
# AccessError and ValidationError are UserErrors, a NotFound (404) is an HTTPException
REFUSALS = (UserError, HTTPException, psycopg2.IntegrityError)
LIST_ROUTE = re.compile(r"^/adopt/?$")
ANIMAL_ROUTE = re.compile(r'''^/adopt/<model\(["']shelter\.animal["']\):\w+>/?$''')
REQUEST_ROUTE = re.compile(r'''^/adopt/<model\(["']shelter\.animal["']\):\w+>/request/?$''')
CLASS_ATTRIBUTES = ("class", "t-att-class", "t-attf-class")
URL_ATTRIBUTES = ("href", "t-att-href", "t-attf-href")
# a rule whose selector contains .o_shelter_card, e.g. ".o_shelter_card {", "&.o_shelter_card:hover {"
CARD_RULE = re.compile(r"\.o_shelter_card\b[^{};]*\{")


def _attributes(node, names):
    return " ".join(node.get(name) or "" for name in names)


def _without_style_comments(content):
    """ Remove the comments of a SCSS or CSS file: the TODO of the skeleton mentions .o_shelter_card. """
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
    # "//" starts a comment at the start of a line or after a space, not in an URL (http://)
    return re.sub(r"(^|\s)//.*$", r"\1", content, flags=re.M)


class TriviaChallenge(models.Model):
    _inherit = "trivia.challenge"

    # ----------------------------------------------------------------------------
    # Checker of the challenge "Adopt Me!": DO NOT MODIFY
    # ----------------------------------------------------------------------------

    def _check_shelter(self):
        _ = self._get_report_env()._
        env = self.env
        Animal = env["shelter.animal"]
        Request = env["shelter.adoption.request"]
        public = env.ref("base.public_user")
        routes = {}

        def get_routes():
            if not routes:
                routes.update({rule.rule: rule.endpoint.routing for rule in env["ir.http"].routing_map().iter_rules()})
            return routes

        def require_route(pattern, route, mission, post=False):
            matching = [(url, routing) for url, routing in get_routes().items() if pattern.match(url)]
            require(matching, _("There is no route %(route)s (mission %(mission)s).", route=route, mission=mission))
            url, routing = matching[0]
            require(routing.get("auth") == "public", _("The route %(route)s must be public (auth='public').", route=url))
            require(routing.get("website"), _("The route %(route)s must be a page of the website (website=True).", route=url))
            if post:
                methods = routing.get("methods") or []
                require("POST" in methods and "GET" not in methods,
                        _("The route %(route)s must only accept the POST method (methods=['POST']).", route=url))

        def template_arch(name, mission):
            view = env.ref(f"{MODULE}.{name}", raise_if_not_found=False)
            require(view, _("The template %(template)s is missing (mission %(mission)s).", template=f"{MODULE}.{name}", mission=mission))
            return view._get_combined_arch()

        def nodes(arch):
            return [node for node in arch.iter() if isinstance(node.tag, str)]

        def create_animals():
            return Animal.create([
                {"name": "Checker Bijou", "species": "cat", "breed": "Checker breed", "is_published": True,
                 "birth_date": "2020-01-01"},
                {"name": "Checker Albert", "species": "dog", "is_published": True},
                {"name": "Checker Hidden", "species": "cat", "is_published": False},
                {"name": "Checker Adopted", "species": "cat", "is_published": True, "adopted": True},
            ])

        def refused(function):
            """ Return whether ``function`` is refused; when it is not, its changes are kept. """
            try:
                with env.cr.savepoint():
                    function()
                    env.flush_all()
            except REFUSALS:
                return True
            return False

        def check_adoptable():
            create_animals()
            expected = Animal.search([("is_published", "=", True), ("adopted", "=", False)], order="name")
            found = Animal._get_adoptable_animals()
            require(set(found.ids) == set(expected.ids),
                    _("_get_adoptable_animals() must return the published animals which are not adopted yet."))
            require(found.ids == expected.ids, _("_get_adoptable_animals() must return the animals ordered by name."))
            cats = Animal._get_adoptable_animals(species="cat")
            require(set(cats.ids) == set(expected.filtered(lambda animal: animal.species == "cat").ids),
                    _("_get_adoptable_animals(species='cat') must only return the adoptable cats."))

        def check_list_route():
            require_route(LIST_ROUTE, "/adopt", 2)

        def check_grid():
            arch = template_arch("animal_list", 2)
            require(
                arch.xpath(f"//*[@t-foreach]//t[@t-call='{MODULE}.animal_card'] | //*[@t-foreach][@t-call='{MODULE}.animal_card']"),
                _("The page /adopt must call the template %(template)s for each animal (t-foreach and t-call).",
                  template=f"{MODULE}.animal_card"),
            )
            require(any("row" in _attributes(node, CLASS_ATTRIBUTES).split() for node in nodes(arch)),
                    _("The grid of the animals must be a Bootstrap row."))
            # columns with breakpoints, or the row-cols of Bootstrap 5
            breakpoint_classes = re.compile(r"\b(col|row-cols)-(sm|md|lg|xl|xxl)-\d+\b")
            require(any(breakpoint_classes.search(_attributes(node, CLASS_ATTRIBUTES)) for node in nodes(arch)),
                    _("The grid must be responsive: use columns with breakpoints, e.g. col-12 col-md-6 col-lg-4."))

        def check_card():
            animal = create_animals()[0].with_user(public)
            env.flush_all()
            try:
                rendered = env["ir.qweb"].with_user(public)._render(f"{MODULE}.animal_card", {"animal": animal})
            except Exception as e:  # noqa: BLE001
                raise CheckFailed(_("The card of an animal cannot be displayed: %(error)s", error=f"{type(e).__name__}: {e}"))
            root = html.fragment_fromstring(str(rendered), create_parent="div")
            cards = root.xpath(f"//*[@data-animal-id='{animal.id}']")
            require(cards, _("The root element of the card must have the attribute data-animal-id (t-att-data-animal-id=\"animal.id\")."))
            card = cards[0]
            require({"card", "o_shelter_card"} <= set((card.get("class") or "").split()),
                    _("The root element of the card must have the classes card and o_shelter_card."))
            text = card.text_content()
            for label, value in [(_("emoji"), animal.species_emoji), (_("name"), animal.name),
                                 (_("breed"), animal.breed), (_("age"), animal.age)]:
                require(value in text, _("The card does not show the %(info)s of the animal.", info=label))
            # the link may be absolute, or start with the code of a language
            require(any(node.get("href", "").endswith(animal.website_url) for node in [card, *card.xpath(".//a")]),
                    _("The card must link to the page of the animal (animal.website_url)."))

        def check_detail():
            require_route(ANIMAL_ROUTE, '/adopt/<model("shelter.animal"):animal>', 3)
            arch = template_arch("animal_detail", 3)
            values = " ".join(f"{name}={value}" for node in nodes(arch) for name, value in node.attrib.items())
            for field_name in ("name", "breed", "age", "description"):
                require(f"animal.{field_name}" in values, _(
                    "The page of an animal does not show its %(field)s (animal.%(field)s).", field=field_name,
                ))

        def check_form():
            arch = template_arch("animal_detail", 4)
            forms = [form for form in arch.xpath("//form") if (form.get("method") or "").lower() == "post"]
            require(forms, _("The page of an animal has no form posted with method=\"post\" (mission 4)."))
            form = forms[0]
            require("request" in _attributes(form, ("action", "t-att-action", "t-attf-action")),
                    _("The form must be posted to the URL of the animal followed by /request."))
            require(form.xpath(".//input[@name='csrf_token']"),
                    _("The form has no CSRF token: <input type=\"hidden\" name=\"csrf_token\" t-att-value=\"request.csrf_token()\"/>"))
            for name in ("name", "email", "phone", "message"):
                require(form.xpath(f".//*[self::input or self::textarea][@name='{name}']"),
                        _("The form has no field %(field)s.", field=name))

        def check_requests():
            require_route(REQUEST_ROUTE, '/adopt/<model("shelter.animal"):animal>/request', 4, post=True)
            animal, other, hidden, adopted = create_animals()
            values = {
                "name": "Checker visitor", "email": "visitor@example.com", "phone": "+352 621 000 000",
                "message": "Checker message", "csrf_token": "token",
                # a malicious visitor adds fields to the form
                "state": "accepted", "animal_id": other.id,
            }
            try:
                adoption = Request.with_user(public)._create_from_website(animal.with_user(public), dict(values))
            except NotImplementedError:
                raise CheckFailed(_("_create_from_website() is not implemented yet (mission 4)."))
            require(isinstance(adoption, models.BaseModel) and adoption._name == Request._name and len(adoption) == 1,
                    _("_create_from_website() must return the new request."))
            adoption = adoption.sudo()
            require(adoption.animal_id == animal,
                    _("A visitor must not be able to choose the animal of the request: it is the animal of the page."))
            require(adoption.state == "new", _("A visitor must not be able to choose the status of the request."))
            require(
                [adoption.name, adoption.email, adoption.phone, adoption.message]
                == [values["name"], values["email"], values["phone"], values["message"]],
                _("The request must keep the name, email, phone and message of the form."),
            )
            for animal_refused, reason in [(hidden, _("not published")), (adopted, _("already adopted"))]:
                require(
                    refused(lambda animal_refused=animal_refused: Request.with_user(public)._create_from_website(
                        animal_refused.with_user(public), dict(values),
                    )),
                    _("A visitor can ask to adopt an animal which is %(reason)s.", reason=reason),
                )

        def check_visitor_request():
            require(Request.search_count([("create_uid", "=", public.id)]), _(
                "No visitor has asked to adopt an animal yet: open /adopt in a private window and send a request.",
            ))

        def check_style_menu():
            Asset = env["ir.asset"]
            styles = []
            for path, full_path, *_rest in Asset._get_asset_paths("web.assets_frontend", Asset._get_asset_params()):
                if f"{MODULE}/static/" in path and path.endswith((".scss", ".css")):
                    with file_open(full_path) as file:
                        styles.append(_without_style_comments(file.read()))
            require(styles, _("The style of the module is not in the assets of the website, web.assets_frontend (mission 5)."))
            require(any(CARD_RULE.search(style) for style in styles),
                    _("The style of the module does not style the cards of the animals (.o_shelter_card)."))
            require(env["website.menu"].search_count([("url", "in", ["/adopt", "/adopt/"])]),
                    _("The website has no menu opening /adopt (mission 5)."))

        def check_certificate():
            reports = env["ir.actions.report"].search([("model", "=", Request._name), ("report_type", "=", "qweb-pdf")])
            require(reports, _("There is no PDF report on the adoption requests (mission 6)."))
            require(reports.filtered("binding_model_id"),
                    _("The certificate cannot be printed from a request: add it to the Print menu (binding_model_id)."))
            animal = create_animals()[0]
            adoption = Request.create({"animal_id": animal.id, "name": "Checker applicant", "email": "applicant@example.com"})
            report = reports.filtered("binding_model_id")[0]
            content = env["ir.actions.report"]._render_qweb_html(report, adoption.ids)[0]
            content = content.decode() if isinstance(content, bytes) else str(content)
            require(adoption.name in content and animal.name in content,
                    _("The certificate must show the name of the applicant and the name of the animal."))

        def check_species_filter():
            arch = template_arch("animal_list", 2)
            # links to /adopt?species=..., or a form with a field "species"
            require(any("species=" in _attributes(node, URL_ATTRIBUTES) or node.get("name") == "species"
                        for node in nodes(arch)),
                    _("The page /adopt has no button to filter the species (?species=...)."))

        def check_snippet():
            snippets = env.ref("website.snippets")._get_combined_arch()
            require(snippets.xpath(f"//t[starts-with(@t-snippet, '{MODULE}.')]"),
                    _("The website editor has no building block of the module (t-snippet)."))

        return [self._run_step(label, step, bonus=bonus) for label, step, bonus in [
            (_("1. Adoptable animals"), check_adoptable, False),
            (_("2. Route of the page /adopt"), check_list_route, False),
            (_("2. Grid of the animals"), check_grid, False),
            (_("2. Card of an animal"), check_card, False),
            (_("3. Page of an animal"), check_detail, False),
            (_("4. Adoption form"), check_form, False),
            (_("4. Safe adoption requests"), check_requests, False),
            (_("4. A visitor asked to adopt an animal"), check_visitor_request, False),
            (_("5. Style and menu of the website"), check_style_menu, False),
            (_("6. Adoption certificate"), check_certificate, False),
            (_("Filter by species"), check_species_filter, True),
            (_("Building block Animal of the week"), check_snippet, True),
        ]]
