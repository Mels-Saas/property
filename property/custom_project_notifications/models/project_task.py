from odoo import models, api
from odoo.exceptions import UserError
from odoo.addons.custom_project_notifications.models.afro_send_sms import AfroMessage

TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJpZGVudGlmaWVyIjoiYld1S29iWTA5Y1JHeWRLajI1RHlBenN6ems4VnVwRFQiLCJleHAiOjE4OTQ3ODY2MjgsImlhdCI6MTczNzAyMDIyOCwianRpIjoiM2U1OTRiOTYtNmI4ZC00YjM4LWIyNDctYzAwNGRhMjNlMTE3In0.VdQiAz1ziL2OTKkkgD333d39jEIaSLLDA7z-rijLufo"

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        self.send_sms_notification(task)
        return task

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if 'stage_id' in vals:
            self.notify_manager()
        return res

    def send_sms_notification(self, task):
        if not task.user_id.phone:
            raise UserError(f"User {task.user_id.name} does not have a phone number set.")
            
        message = f"Task '{task.name}' on project {task.project_id.name} has been assigned to you."
        self.env['afro.message'].send_sms(
            phone_number=task.user_id.phone,
            message=message
        )

    def notify_manager(self):
        if not self.project_id.user_id.phone:
            raise UserError(f"Project manager {self.project_id.user_id.name} does not have a phone number set.")
            
        old_stage = self.env['project.task.type'].browse(self._context.get('old_stage_id')).name if self._context.get('old_stage_id') else 'previous stage'
        message = f"Task '{self.name}' on project {self.project_id.name} has changed state from {old_stage} to {self.stage_id.name}."
        
        self.env['afro.message'].send_sms(
            phone_number=self.project_id.user_id.phone,
            message=message
        )

    def test_send_sms(self):
        """Test method to verify SMS functionality"""
        if not self.user_id.phone:
            raise UserError("Please set a phone number for testing")
            
        message = "This is a test SMS from Odoo Project Management"
        self.env['afro.message'].send_sms(
            phone_number=self.user_id.phone,
            message=message
        )
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
            'message': 'Test SMS sent successfully',
            'type': 'success',
            'sticky': False,
        }}
