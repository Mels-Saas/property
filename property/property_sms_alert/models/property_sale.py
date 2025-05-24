from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class PropertySale(models.Model):
    _inherit = 'property.sale'

    def action_send_manual_sms(self):
        """Send SMS for the nearest upcoming unpaid installment due date."""
        self.ensure_one()
        today = datetime.now().date()

        # Get active SMS config related to the property's site
        config = self.env['property.sms.config'].search([
            ('active', '=', True),
            ('site_ids', 'in', self.property_id.site.id),
        ], limit=1)

        if not config:
            raise UserError("No active SMS configuration found for the property's site.")

        # Filter unpaid and non-discounted lines
        lines_to_notify = self.payment_installment_line_ids.filtered(
            lambda line: line.expected_date and line.state not in ('paid', 'discounted')
        )

        if not lines_to_notify:
            raise UserError("No upcoming unpaid payment installments found for this sale.")

        # Get the nearest upcoming line
        nearest_line = min(lines_to_notify, key=lambda l: l.expected_date)

        due_date = nearest_line.expected_date
        alert_date = due_date - timedelta(days=config.days_before)

        if today < alert_date:
            raise UserError("It's not yet time to send SMS for the nearest due date.")

        # Prepare recipients
        recipients = set()
        if self.partner_id.phone:
            recipients.add(self.partner_id.phone)
        if self.property_id.finance_manager.phone:
            recipients.add(self.property_id.finance_manager.phone)

        if not recipients:
            raise UserError("No valid recipients (customer or finance manager) found.")

        # Send SMS to each recipient
        for phone_number in recipients:
            
            self.env['afro.message'].send_sms(
                phone_number=phone_number,
                message=config.message_content
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'SMS Sent',
                'message': "SMS alert sent for the nearest upcoming payment installment.",
                'type': 'success',
                'sticky': False,
            }
        }



    def _send_sms_alerts(self):
        """Scheduled action to send SMS alerts for the nearest upcoming payment due date."""
        today = datetime.now().date()

        configs = self.env['property.sms.config'].search([('active', '=', True)])
        
        for config in configs:
            # Get sales linked to the config's sites and in draft state
            sales = self.search([
                ('property_id.site', 'in', config.site_ids.ids),
                ('state', '=', 'draft'),
            ])

            for sale in sales:
                # Filter unpaid and non-discounted lines
                lines_to_notify = sale.payment_installment_line_ids.filtered(
                    lambda line: line.expected_date and line.state not in ('paid', 'discounted')
                )
                if not lines_to_notify:
                    continue

                # Get the nearest unpaid upcoming line
                nearest_line = min(lines_to_notify, key=lambda l: l.expected_date)
                due_date = nearest_line.expected_date
                alert_date = due_date - timedelta(days=config.days_before)

                if today < alert_date:
                    continue  # Not time yet

                # Collect recipients
                recipients = set()
                if sale.partner_id.phone:
                    recipients.add(sale.partner_id.phone)
                if sale.property_id.finance_manager.phone:
                    recipients.add(sale.property_id.finance_manager.phone)

                if not recipients:
                    continue

                # Format message
               

                # Send SMS to each recipient
                for phone_number in recipients:
                    self.env['afro.message'].send_sms(
                        phone_number=phone_number,
                        message=config.message_content
                    )

                    # Optional: Log message on chatter
                   

 