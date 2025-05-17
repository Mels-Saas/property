from odoo import models,fields

class CRMLead(models.Model):
    _inherit="crm.lead"



    def send_sms(self):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Send SMS',
        'res_model': 'lead.sms.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_partner_id': self.partner_id.id,
            'default_phone_no': self.phone,
        }
    }