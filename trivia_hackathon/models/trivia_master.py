import logging
import os

import requests

from odoo import api, models
from odoo.http import request

_logger = logging.getLogger(__name__)

# URL of the master database of the organisers, which collects the results of all the teams
# TODO: set the URL of the Odoo.sh master database before the hackathon
DEFAULT_MASTER_URL = "https://hackathon26.odoo.com"
TIMEOUT = 5  # seconds: never keep the players waiting when the master database is slow or down

PARAM_URL = "trivia_hackathon.master_url"
PARAM_TEAM = "trivia_hackathon.master_team"
# The PIN is never stored in the database: all the teams' databases are branches of the same Odoo.sh project, and
# any team can connect to the database of another one. It is kept in the session of the user who entered it instead.
SESSION_PIN = "trivia_hackathon_master_pin"


class TriviaMasterError(Exception):
    """ The master database could not be reached, or refused the request. """


class TriviaMaster(models.AbstractModel):
    """ Client of the API of the master database (module ``hackathon``), which keeps the scores of all the teams.

    The URL of the master database and the name of the team are stored in the database, the PIN of the team only in
    the session of the user: each player enters it once per session (see trivia.master.wizard). Without a request
    (e.g. a scheduled action), there is no PIN: the results wait for the next check of a player who entered it. """
    _name = "trivia.master"
    _description = "Trivia Master Database"

    @api.model
    def _get_config(self):
        params = self.env["ir.config_parameter"].sudo()
        return {
            "url": (params.get_str(PARAM_URL) or DEFAULT_MASTER_URL).strip().rstrip("/"),
            "team": (params.get_str(PARAM_TEAM) or "").strip(),
            "pin": self._get_session_pin(),
        }

    @api.model
    def _set_config(self, url, team, pin):
        params = self.env["ir.config_parameter"].sudo()
        params.set_str(PARAM_URL, (url or "").strip().rstrip("/") or False)
        params.set_str(PARAM_TEAM, (team or "").strip() or False)
        if request:
            request.session[SESSION_PIN] = (pin or "").strip()

    @api.model
    def _get_session_pin(self):
        return ((request and request.session.get(SESSION_PIN)) or "").strip()

    @api.model
    def _get_odoo_sh_stage(self):
        """ Return the environment of this database on Odoo.sh (dev, staging or production), or None when it is
        not on Odoo.sh, e.g. a local database: the master database only counts the results of Odoo.sh. """
        return os.environ.get("ODOO_STAGE") or None

    @api.model
    def _is_configured(self):
        return all(self._get_config().values())

    @api.model
    def _post(self, route, payload=None, config=None):
        """ POST ``payload`` to ``route`` of the master database, with the team and its PIN.

        :return: the JSON answer of the master database (a dict, with "status": "ok")
        :raise TriviaMasterError: with a message for the players
        """
        config = config or self._get_config()
        if not all(config.values()):
            raise TriviaMasterError(self.env._(
                "The connection to the master database is not set: enter your team and your PIN in "
                "Trivi'Hackathon › Master Connection."
            ))
        body = {**(payload or {}), "team": config["team"], "pin": config["pin"], "stage": self._get_odoo_sh_stage()}
        try:
            response = requests.post(f"{config['url']}{route}", json=body, timeout=TIMEOUT)
        except requests.RequestException as e:
            _logger.info("Trivi'Hackathon: master database unreachable: %s", e)
            raise TriviaMasterError(self.env._("The master database can't be reached: %(error)s", error=e)) from None
        try:
            result = response.json()
        except ValueError:
            result = None
        if not isinstance(result, dict):
            raise TriviaMasterError(self.env._(
                "Unexpected answer of the master database (HTTP %(status)s): is its URL right?", status=response.status_code,
            ))
        if result.get("status") != "ok":
            raise TriviaMasterError(result.get("message") or self.env._("The master database refused the request."))
        return result
