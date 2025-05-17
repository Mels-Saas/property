from odoo import models,fields

class BulkLeadSms(models.TransientModel):
    _name="bulk.lead.sms"

    customer_ids= fields.Many2many('res.partner',string="Customers")
    message_body = fields.Text(string="Message")

    def send_sms(self):
        for cutomer in self.customer_ids:
            if cutomer.phone:
                response = self.env['afro.message'].send_sms(
                    phone_number=cutomer.phone,
                    message=self.message_body
                )
            
        
        return  {
                    'type': 'ir.actions.act_window_close'
                }