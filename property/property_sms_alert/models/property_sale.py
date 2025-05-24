from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging
_logger=logging.getLogger(__name__)
class PropertySale(models.Model):
    _inherit = 'property.sale'

    def action_send_manual_sms(self):
        self.ensure_one()
        today = datetime.now().date()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        config = self.env['property.sms.config'].search([
            ('active', '=', True),
            ('site_ids', 'in', self.property_id.site.id),
        ], limit=1)

        if not config:
            raise UserError("No active SMS configuration found for the property's site.")

        lines_to_notify = self.payment_installment_line_ids.filtered(
            lambda line: line.expected_date and line.state not in ('paid', 'discounted')
        )

        if not lines_to_notify:
            raise UserError("No upcoming unpaid payment installments found for this sale.")

        nearest_line = min(lines_to_notify, key=lambda l: l.expected_date)

        recipients = set()
        if self.partner_id.phone:
            recipients.add((self.partner_id.id, self.partner_id.phone))
        if self.property_id.finance_manager.phone:
            recipients.add((self.property_id.finance_manager.id, self.property_id.finance_manager.phone))

        if not recipients:
            raise UserError("No valid recipients (customer or finance manager) found.")

        mailing_list = self.env['mailing.list'].create({
            'name': f"SMS Alert for Sale {self.name} - {today}",
        })

        phones = [phone for _, phone in recipients]
        existing_contacts = self.env['mailing.contact'].search([('mobile', 'in', phones)])
        existing_phones = {c.mobile for c in existing_contacts}

        # Create missing contacts
        new_contacts_data = [
            {
                'name': self.env['res.partner'].browse(partner_id).name,
                'mobile': phone,
            }
            for partner_id, phone in recipients if phone not in existing_phones
        ]
        
        if new_contacts_data:
            self.env['mailing.contact'].create(new_contacts_data)
        _logger.info("################### new_contacts_data")
        _logger.info(new_contacts_data)

        # Add only missing contacts to mailing list
        all_contacts = self.env['mailing.contact'].search([
            ('mobile', 'in', phones),
            ('id', 'not in', mailing_list.contact_ids.ids),
        ])
        _logger.info("################### all_contacts")
        _logger.info(all_contacts)
        mailing_list.contact_ids = [(4, cid) for cid in all_contacts.ids]

        mailing = self.env['mailing.mailing'].create({
            'name': f"SMS Alert for Sale {self.name} - {today} - {timestamp}",
            'subject': f"SMS Alert for Sale {self.name}",
            'mailing_type': 'sms',
            'body_plaintext': config.message_content,
            'contact_list_ids': [(6, 0, [mailing_list.id])],
            'mailing_on_mailing_list': True,
        })

        a=mailing.action_put_in_queue()
        _logger.info("######################## a")
        _logger.info(a)
    
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
        today = datetime.now().date()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        configs = self.env['property.sms.config'].search([('active', '=', True)])

        for config in configs:
            sales = self.search([
                ('property_id.site', 'in', config.site_ids.ids),
                ('state', '=', 'draft'),
            ])

            for sale in sales:
                lines_to_notify = sale.payment_installment_line_ids.filtered(
                    lambda line: line.expected_date and line.state not in ('paid', 'discounted')
                )
                if not lines_to_notify:
                    continue

                nearest_line = min(lines_to_notify, key=lambda l: l.expected_date)
                alert_date = nearest_line.expected_date - timedelta(days=config.days_before)

                if today < alert_date:
                    continue

                recipients = set()
                if sale.partner_id.phone:
                    recipients.add((sale.partner_id.id, sale.partner_id.phone))
                if sale.property_id.finance_manager.phone:
                    recipients.add((sale.property_id.finance_manager.id, sale.property_id.finance_manager.phone))

                if not recipients:
                    continue

                mailing_list = self.env['mailing.list'].create({
                    'name': f"SMS Alert for Sale {sale.name} - {today}",
                })

                phones = [phone for _, phone in recipients]
                existing_contacts = self.env['mailing.contact'].search([('mobile', 'in', phones)])
                existing_phones = {c.mobile for c in existing_contacts}

                # Create missing contacts
                new_contacts_data = [
                    {
                        'name': self.env['res.partner'].browse(partner_id).name,
                        'mobile': phone,
                    }
                    for partner_id, phone in recipients if phone not in existing_phones
                ]
                if new_contacts_data:
                    self.env['mailing.contact'].create(new_contacts_data)

                # Add only new contacts to mailing list
                all_contacts = self.env['mailing.contact'].search([
                    ('mobile', 'in', phones),
                    ('id', 'not in', mailing_list.contact_ids.ids),
                ])
                mailing_list.contact_ids = [(4, cid) for cid in all_contacts.ids]

                mailing = self.env['mailing.mailing'].create({
                    'name': f"SMS Alert for Sale {sale.name} - {today} - {timestamp}",
                    'subject': f"SMS Alert for Sale {sale.name}",
                    'mailing_type': 'sms',
                    'body_plaintext': config.message_content,
                    'contact_list_ids': [(6, 0, [mailing_list.id])],
                    'mailing_on_mailing_list': True,
                })

                mailing.action_put_in_queue()


                   

 