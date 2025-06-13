from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import re
import base64

from markupsafe import Markup

from odoo.tools.populate import compute
from dateutil.relativedelta import relativedelta


class PropertyCommssionLine(models.Model):

    _name="property.commission.line"

    sale_id = fields.Many2one('property.sale')
    payment_term_id = fields.Many2one('property.payment.term.line')
    sequence = fields.Integer(related='payment_term_id.sequence', store=True)
    expected = fields.Float('Expected(%)')
    expected_amount = fields.Float('Expected Amount', compute="compute_expected_amount")
    paid_amount = fields.Float('Paid Amount')
    discount = fields.Float('Discount')
    remaining = fields.Float('Remaining', compute="compute_remaining_amount")
    expected_date = fields.Date('Expected Date',compute="_compute_expected_date")  # Added expected_date field
    state = fields.Selection(
        [
            ("not_paid", "Not Paid"),
            ("partial", "Partial"),
            ("paid", "Paid"),
            ("discounted", "Discounted"),
        ],
        string="State",
        compute="compute_payment_status",
    )

    def compute_remaining_amount(self):
        for rec in self:
            rec.remaining=rec.expected_amount - rec.paid_amount - rec.discount

    @api.depends('expected')
    def compute_expected_amount(self):
        for rec in self:
            rec.expected_amount=rec.expected*rec.sale_id.total_commission/100

    @api.depends('expected','expected_amount','paid_amount','discount')
    def compute_payment_status(self):
        for rec in self:
            paid=rec.paid_amount + rec.discount
            if paid >=rec.expected_amount:
                if rec.paid_amount == 0:
                    rec.state="discounted"
                else:
                    rec.state="paid"
            elif rec.paid_amount>0 and (paid <= rec.expected_amount):
                rec.state="partial"
            else:
                rec.state = "not_paid"
    
    @api.depends('sale_id.order_date', 'payment_term_id.duration_type', 'payment_term_id.duration_number')
    def _compute_expected_date(self):
        for rec in self:
            if rec.sale_id.order_date and rec.payment_term_id.duration_type and rec.payment_term_id.duration_number:
                duration = int(rec.payment_term_id.duration_number)  # Convert to integer for relativedelta
                if rec.payment_term_id.duration_type == 'day':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(days=duration)
                elif rec.payment_term_id.duration_type == 'week':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(weeks=duration)
                elif rec.payment_term_id.duration_type == 'month':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(months=duration)
                elif rec.payment_term_id.duration_type == 'year':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(years=duration)
            else:
                rec.expected_date = False



class PropertyPaymentLine(models.Model):
    _name = 'property.payment.line'

    sale_id = fields.Many2one('property.sale')
    payment_term_id = fields.Many2one('property.payment.term.line')
    sequence = fields.Integer(related='payment_term_id.sequence', store=True)
    expected = fields.Float('Expected(%)')
    expected_amount = fields.Float('Expected Amount', compute="compute_expected_amount")
    paid_amount = fields.Float('Paid Amount')
    discount = fields.Float('Discount')
    remaining = fields.Float('Remaining', compute="compute_remaining_amount")
    expected_date = fields.Date('Expected Date',compute="_compute_expected_date")  # Added expected_date field
    state = fields.Selection(
        [
            ("not_paid", "Not Paid"),
            ("partial", "Partial"),
            ("paid", "Paid"),
            ("discounted", "Discounted"),
        ],
        string="State",
        compute="compute_payment_status",
    )
    
    def compute_remaining_amount(self):
        for rec in self:
            rec.remaining=rec.expected_amount - rec.paid_amount - rec.discount

    @api.depends('expected')
    def compute_expected_amount(self):
        for rec in self:
            rec.expected_amount=rec.expected*rec.sale_id.new_sale_price/100

    @api.depends('expected','expected_amount','paid_amount','discount')
    def compute_payment_status(self):
        for rec in self:
            paid=rec.paid_amount + rec.discount
            if paid >=rec.expected_amount:
                if rec.paid_amount == 0:
                    rec.state="discounted"
                else:
                    rec.state="paid"
            elif rec.paid_amount>0 and (paid <= rec.expected_amount):
                rec.state="partial"
            else:
                rec.state = "not_paid"

    @api.depends('sale_id.order_date', 'payment_term_id.duration_type', 'payment_term_id.duration_number')
    def _compute_expected_date(self):
        for rec in self:
            if rec.sale_id.order_date and rec.payment_term_id.duration_type and rec.payment_term_id.duration_number:
                duration = int(rec.payment_term_id.duration_number)  # Convert to integer for relativedelta
                if rec.payment_term_id.duration_type == 'day':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(days=duration)
                elif rec.payment_term_id.duration_type == 'week':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(weeks=duration)
                elif rec.payment_term_id.duration_type == 'month':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(months=duration)
                elif rec.payment_term_id.duration_type == 'year':
                    rec.expected_date = rec.sale_id.order_date + relativedelta(years=duration)
            else:
                rec.expected_date = False








