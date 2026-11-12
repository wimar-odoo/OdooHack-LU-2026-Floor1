from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    checkin_source = fields.Selection(
        [("backend", "Backend"), ("kiosk", "Welcome Desk")],
        string="Checked In From", readonly=True, copy=False,
    )

    # ----------------------------------------------------------------------------
    # The server side of the welcome desk (TODO 2): ready, call it from JavaScript
    # ----------------------------------------------------------------------------

    @api.model
    def get_kiosk_data(self):
        """ Return the data of the welcome desk: the festival and its registrations.

        :return: {
            'event': {'id': 7, 'name': "Festival Solidaire 2026", 'attendees': 12, 'seats_max': 150},
            'registrations': [{'id': 42, 'name': "Marie Weber", 'ticket': "Solidarity", 'attended': False}, ...],
        }
        """
        event = self.env.ref("trivia_festival.event_festival")
        registrations = self.search([("event_id", "=", event.id), ("state", "in", ("open", "done"))], order="name, id")
        return {
            "event": {
                "id": event.id,
                "name": event.name,
                "attendees": event.seats_used,
                "seats_max": event.seats_max,
            },
            "registrations": [{
                "id": registration.id,
                "name": registration.name,
                "ticket": registration.event_ticket_id.name or "",
                "attended": registration.state == "done",
            } for registration in registrations],
        }

    def action_kiosk_checkin(self):
        """ Check the attendees in at the welcome desk. """
        self.action_set_done()
        self.checkin_source = "kiosk"
        return True
