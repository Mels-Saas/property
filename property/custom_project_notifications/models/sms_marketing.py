from odoo import models, api,fields
import logging
import ast

_logger = logging.getLogger(__name__)

class SMSMarketing(models.Model):
    _inherit = "mailing.mailing"
    sent_count = fields.Integer(default=0, string="Sent")


    def action_put_in_queue(self):
        self.state="in_queue"
        for record in self:
            try:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info(f"*** {record.mailing_domain}")
                if not self.mailing_on_mailing_list:
                    domain = ast.literal_eval(record.mailing_domain)
                    contact_list_ids = self.env['res.partner'].search([('id','in',domain[2])])
                else:
                    # get the contact list ids from the mailing list
                    contact_list_ids = self.contact_list_ids.contact_ids
                   
                body_plaintext = record.body_plaintext or "No message"
                phones = []
                for contact in contact_list_ids:
                    if self.mailing_on_mailing_list:
                        phone = contact.mobile
                        if phone:
                            phones.append(phone)
                    else:
                        phone = contact.phone
                        if phone:
                            phones.append(phone)
                    # if phone:
                    #     _logger.info(f"Sending SMS to {phone}")
                    #     response=  self.env['afro.message'].send_sms(
                    #         phone_number=phone,
                    #         message=body_plaintext
                    #     )
                    #     _logger.info("SMS sent")
                        
                        
                    #     if response['acknowledge']== 'success':
                    #         _logger.info("SMS: SENT")
                    #         ack=  self.env['mailing.trace'].create({
                    #         'trace_status': 'sent',
                    #         'sms_number': phone,
                    #         'mass_mailing_id': self.id,
                    #         'model': 'res.partner',
                    #         'trace_type':'sms',
                    #         'res_id': contact.id,
                    #         'sent_datetime':fields.Datetime.now(),
                    #         'mail_mail_id_int':self.id
                    #     })
                    #         ack['message_id']= ack.id
                    #         self.sent +=1
                    #         self.calendar_date = fields.Datetime.now()
                    #         _logger.info(f"SMS: Sent {ack.sms_number} ")
                    #     else:
                    #         _logger.info("SMS: Failed")
                    #         self.env['mailing.trace'].create({
                    #             'trace_status':'cancel',
                    #             'sms_number': phone,
                    #             'mass_mailing_id': self.id,
                    #             'model': 'res.partner',
                    #             'res_id': contact.id,
                    #         })
                
                response=  self.env['afro.message'].send_sms(
                            phone_number=phones,
                            message=body_plaintext
                        )
                
                self.state= response or 'draft'
            except Exception as e:
                _logger.exception(f"Failed to reload SMS: {e}")



    def action_reload(self):
        _logger.info("SMS IN")
        for record in self:
            try:
                domain = ast.literal_eval(record.mailing_domain)
                contact_list_ids = self.env['res.partner'].search(domain)

                body_plaintext = record.body_plaintext or "No message"

                for contact in contact_list_ids:
                    if contact.phone:
                        _logger.info(f"Sending SMS to {contact.phone}")
                        self.env['afro.message'].send_sms(
                            phone_number=contact.phone,
                            message=body_plaintext
                        )
                        _logger.info("SMS sent")
                        self.sent_count +=1
            except Exception as e:
                _logger.exception(f"Failed to reload SMS: {e}")
