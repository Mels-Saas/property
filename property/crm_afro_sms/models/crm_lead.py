from odoo import models,fields
import logging

_logger = logging.getLogger(__name__)
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
            
        }
    }

    def send_sms_bulk(self):
        partner_ids = self.env.context.get('active_ids', [])
        _logger.info(f"SMS PARTMERS {partner_ids}")
        partners=[]
        for i in partner_ids:
            p = self.env['res.partner'].search([('id','=',i)])
            if p:
                _logger.info(f"SMS PARTMERS {p.name}")
                partners.append(p)
            else:
                _logger.info(f"SMS PARTMERS partner with id {i} not found")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Send SMS',
            'res_model': 'bulk.lead.sms',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_customer_ids': partners,
            }
        }