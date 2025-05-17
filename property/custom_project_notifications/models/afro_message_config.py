from odoo import models, fields, api

class AfroMessageConfig(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Afro Message Configuration'

    afromessage_token = fields.Char(string='API Token', config_parameter='afromessage.token')
    afromessage_identifier_id = fields.Char(string='Identifier ID', config_parameter='afromessage.identifier_id')
    afromessage_sender_name = fields.Char(string='Sender Name', config_parameter='afromessage.sender_name')