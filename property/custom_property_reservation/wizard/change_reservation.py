from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import re

from odoo.tools.safe_eval import datetime


class PropertyReservation(models.TransientModel):
    _name = 'change.reservation.wizard'

    reservation_id = fields.Many2one('property.reservation', string="Reservation")

    reservation_type=fields.Many2one('property.reservation.configuration',string="Reservation Type")


    def action_change_reservation(self):
        if self.reservation_id:
            self.reservation_id.write({
                'reservation_type_id': self.reservation_type.id,
            })
