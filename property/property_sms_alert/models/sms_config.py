from odoo import models, fields, api

class PropertySMSConfig(models.Model):
    _name = 'property.sms.config'
    _description = 'Property SMS Configuration'

    name = fields.Char(string='Name', required=True)
    site_ids = fields.Many2many('property.site', string='Sites', required=True)
    message_content = fields.Text(string='Message Content', required=True)
    days_before = fields.Integer(string='Days Before Alert', required=True, default=1)
    active = fields.Boolean(string='Active', default=True)