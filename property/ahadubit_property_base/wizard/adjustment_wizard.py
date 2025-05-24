from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PropertySaleAdjustmentWizard(models.Model):
    _name = 'property.sale.adjustment.wizard'
    _description = 'Property Sale Value Adjustment Wizard'

    sale_id = fields.Many2one('property.sale', string='Sale', required=True, default=lambda self: self.env.context.get('default_sale_id'))
    amount = fields.Float(string='Amount', required=True, help='Positive to increase, negative to decrease.')
    reason = fields.Text(string='Reason', required=True)
    payment_installment_line_ids = fields.Many2one('property.payment.line', string='Payment Installments', required=True)
    adjustment_date = fields.Datetime(string='Adjustment Date', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Adjusted By', required=True, default=lambda self: self.env.user)

    @api.constrains('payment_installment_line_ids')
    def _check_payment_lines(self):
        for wizard in self:
            if not wizard.payment_installment_line_ids:
                raise ValidationError("At least one payment installment line must be selected.")
            for line in wizard.payment_installment_line_ids:
                if line.state in ('paid', 'discounted'):
                    raise ValidationError(f"Cannot adjust paid or discounted installment: {line.name}")

    @api.constrains('amount', 'payment_installment_line_ids')
    def _check_adjustment_validity(self):
        for wizard in self:
            if wizard.sale_id:
                new_sale_price = wizard.amount
                if new_sale_price < 0:
                    raise ValidationError("Adjustment would result in a negative sale price.")
              
               

    def action_apply_adjustment(self):
        """Apply the value adjustment to the sale and payment installments."""
        self.ensure_one()

        # Update sale price

     

        # Distribute adjustment amount equally across selected payment lines
        amount_per_line = self.amount 
        for line in self.payment_installment_line_ids:
            line.expected_amount += amount_per_line
        self.sale_id.sale_price+=self.amount

        # Log the adjustment in chatter
        # self.sale_id.message_post(
        #     body=f"Value adjustment applied: Amount={self.amount}, Reason={self.reason}, Installments={', '.join(self.payment_installment_line_ids.mapped('name'))}",
        #     subject="Sale Value Adjustment"
        # )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Adjustment Applied',
                'message': f"Sale price adjusted by {self.amount}. Payment installments updated.",
                'type': 'success',
                'sticky': False,
            }
        }