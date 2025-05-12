from pprint import pprint

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class PropertyReservationInherit(models.Model):
    _inherit = 'property.reservation'

    property_id = fields.Many2one(
        'property.property',
        domain=lambda self: self._get_property_domain(),
        string="Property",
        required=True,
        tracking=True
    )
    reservation_type_id = fields.Many2one('property.reservation.configuration',
                                         string="Reservation Type",
                                          domain=[('is_used_use', '!=', True)],
                                         tracking=True, required=True)

    crm_lead_id = fields.Many2one("crm.lead")

    @api.model
    def create(self, vals):
        """Create a new reservation with calculated expiration date."""

        expire_date = self.get_expire_date(vals.get('reservation_type_id'))
        status = "requested" if self.is_sufficient else "draft"



        vals.update({
            'expire_date': expire_date,
            'status': status
        })
        res =super(PropertyReservationInherit, self).create(vals)
        if res.reservation_type_id.one_time_use:
            res.reservation_type_id.sudo().write({'is_used_use':True,
                                       'used_by_id':self.env.user.id})
            
        return res

    @api.onchange('reservation_type_id')
    def _onchange_property_id(self):
        self.expire_date = self.get_expire_date(self.reservation_type_id.id)
                                                                                                        
    @api.depends('crm_lead_id')
    def _get_property_domain(self):
        """Dynamic domain for property selection"""
        for rec in self:
            domain = [('state', '=', 'available')]  # Include available properties

            if rec.crm_lead_id:
                # Get property IDs that are reserved but NOT by the current crm_lead_id
                reserved_properties = self.env['property.reservation'].search([
                    ('status', '=', 'reserved'),
                    ('crm_lead_id', '!=', rec.crm_lead_id.id)
                ]).mapped('property_id.id')

                # Add condition to allow selection of those properties
                if reserved_properties:
                    domain = ['|', ('state', '=', 'available'), ('id', 'in', reserved_properties)]

            return domain

    @api.onchange('crm_lead_id')
    def _onchange_crm_lead_id(self):
        """Update property_id domain dynamically when crm_lead_id changes"""
        return {'domain': {'property_id': self._get_property_domain()}}


    def change_reservation(self):

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Reservation',
            'res_model': 'change.reservation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reservation_id': self.id,
            }
        }
    
  
    

    def get_expire_date(self, reservation_type_id):
        
        reservation_type = self.env['property.reservation.configuration'].browse(reservation_type_id)
        if not reservation_type:
            return False

        start_time = 8.5  # 8:30 AM (in hours)
        end_time = 17.5  # 5:30 PM (in hours)
        current_time = fields.Datetime.now()
        expire_date = current_time

        def is_working_hour(dt):
            """Check if a given datetime is within working hours."""
            return dt.weekday() < 5 and start_time <= dt.hour + dt.minute / 60 < end_time

        def next_working_time(dt):
            """Move to the next available working time."""
            if dt.hour + dt.minute / 60 >= end_time:  # If after 5:30 PM, move to next day 8:30 AM
                dt += timedelta(days=1)
                dt = dt.replace(hour=8, minute=30, second=0)
            elif dt.hour + dt.minute / 60 < start_time:  # If before 8:30 AM, move to 8:30 AM
                dt = dt.replace(hour=8, minute=30, second=0)
            while dt.weekday() >= 5:  # Skip weekends
                dt += timedelta(days=1)
                dt = dt.replace(hour=8, minute=30, second=0)
            return dt

        # Ensure the current time is in working hours
        expire_date = next_working_time(expire_date)

        if reservation_type.duration_in == "minutes":
            remaining_minutes = reservation_type.duration
        elif reservation_type.duration_in == "hours":
            remaining_minutes = reservation_type.duration * 60
        elif reservation_type.duration_in == "days":
            remaining_minutes = reservation_type.duration * 9 * 60  # 9 hours per working day
        elif reservation_type.duration_in == "weeks":
            remaining_minutes = reservation_type.duration * 5 * 9 * 60  # 5 working days per week
        else:  # months
            expire_date += relativedelta(months=reservation_type.duration)
            return next_working_time(expire_date)

        # Add time while respecting working hours
        while remaining_minutes > 0:
            if is_working_hour(expire_date):
                increment = min(remaining_minutes, 60)  # Add up to 1 hour at a time
                expire_date += timedelta(minutes=increment)
                remaining_minutes -= increment
            else:
                expire_date = next_working_time(expire_date)

        return expire_date

    @api.constrains('crm_lead_id')
    def _check_reservation_constraints(self):
        for record in self:
            if record.crm_lead_id:
                existing_reservations = self.env['property.reservation'].search([
                    ('crm_lead_id', '=', record.crm_lead_id.id)
                ])
                canceled_reservations = existing_reservations.filtered(lambda r: r.status == 'canceled')

                if canceled_reservations:
                    now = fields.Datetime.now()
                    for res in canceled_reservations:
                        if res.canceled_time and now < res.canceled_time + timedelta(hours=24):
                            raise ValidationError(
                                "You cannot create a new reservation for this CRM lead until 24 hours have passed since the cancellation."
                            )