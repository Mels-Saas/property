from odoo import fields, models, _

class LeadSMSWizard(models.TransientModel):
    _name = 'lead.sms.wizard'
    _description = 'Lead SMS Wizard'

    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    phone_no = fields.Char(string='Phone Number', required=True)
    message_body = fields.Text(string='Message', required=True)

    def action_send_sms(self):
        self.ensure_one()
        
        response = self.env['afro.message'].send_sms(
            phone_number=self.phone_no,
            message=self.message_body
        )
        
        if response.get('acknowledge') == 'success':
            # Log the success in the chatter
            self.env['crm.lead'].browse(self._context.get('active_id')).message_post(
                body=_("SMS sent successfully to %s: %s") % (self.phone_no, self.message_body)
            )
            # Return a multi-action: show success notification and close the wizard
            return [
                {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('SMS sent successfully!'),
                        'type': 'success',
                        'sticky': False,
                    }
                },
                {
                    'type': 'ir.actions.act_window_close'
                }
            ]
        else:
            # Show error notification and close the wizard
            error_message = response.get('error', _('Failed to send SMS.'))
            return [
                {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': error_message,
                        'type': 'danger',
                        'sticky': True,
                    }
                },
                {
                    'type': 'ir.actions.act_window_close'
                }
            ]