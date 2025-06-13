import requests
from odoo import api, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
class AfroMessage(models.AbstractModel):
    _name = 'afro.message'
    _description = 'AfroMessage SMS Service'
    
    BASE_URL = "https://api.afromessage.com/api/bulk_send"

    def _get_config(self):
        """Get AfroMessage configuration parameters"""
        params = self.env['ir.config_parameter'].sudo()
        return {
            'token': params.get_param('afromessage.token'),
            'identifier_id': params.get_param('afromessage.identifier_id'),
            'sender_name': params.get_param('afromessage.sender_name')
        }

    def send_sms(self, phone_number, message, callback_url=None):
        """Send SMS using AfroMessage API"""
        config = self._get_config()
        _logger.info("SMS IN Afro")
        
        if not config['token'] :
            raise ValueError("AfroMessage configuration is missing. Please configure it in Settings.")

        headers = {
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": phone_number,
            "message": message,
            "from": config['sender_name'] or "",
          
        }
        
        if callback_url:
            payload["callback"] = callback_url

        try:
            import urllib.parse
            params = {
                "from": config["identifier_id"],
                "to": phone_number,
                "message": message,
                "sender": config["sender_name"],
                "callback": callback_url
            }
            response = requests.Session().post(self.BASE_URL, json=params, headers=headers)
            if response.status_code == 200:

                _logger.info("SMS AFRO SENT")
                resp_json = response.json()
                if resp_json['acknowledge'] == 'success':
                    return "done"
            _logger.info(f"SMS {response.json()}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to send SMS: {str(e)}")
            raise UserError("Failed to send SMS. Please check the configuration and try again.")

# def send_sms(phone_number, message, token, callback_url=None):
#     try:
#         phone_number="0961386082"
#         message="test message"
#         callback_url="http://localhost:8000/afro_message/"
#         response = AfroMessage.send_sms(phone_number, message, callback_url)
#         print('api success')
#         return response
#     except Exception as e:
#         print('api error')
#         raise e